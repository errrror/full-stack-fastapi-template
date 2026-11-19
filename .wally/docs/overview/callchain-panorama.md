---
kind: panorama
scope: callchain
status: draft
origin: generated
source_paths: [backend/app/main.py, backend/app/api/deps.py, backend/app/api/routes/login.py, backend/app/crud.py, backend/app/utils.py, frontend/src/main.tsx]
symbols: [login_access_token, authenticate, create_access_token, send_email, readUserMe]
upstream: [INDEX.md]
downstream: [business/auth-and-users.md, integrations/topology-and-mapping.md, operations/runbook-and-observability.md]
---
# 主干调用链全景

本页把浏览器登录、受保护 API 与邮件发送三条主链按符号级顺序展开。所有链路的入口都在 `backend/app/main.py:21` 创建的 FastAPI 应用内，前端只通过同域 `/api/v1` 访问。

## 1. 浏览器登录主链

```text
frontend/src/hooks/useAuth.ts:41 login(data)
  → LoginService.loginAccessToken (generated client)
  → POST /api/v1/login/access-token
  → backend/app/api/routes/login.py:23 login_access_token()
      ├─ crud.authenticate() (backend/app/crud.py:45)
      │    ├─ get_user_by_email() (backend/app/crud.py:34)
      │    └─ verify_password() (backend/app/core/security.py:29)
      ├─ [用户不存在或密码错误] HTTP 400 "Incorrect email or password"
      ├─ [is_active=false] HTTP 400 "Inactive user"
      └─ security.create_access_token() (backend/app/core/security.py:22)
  ← Token(access_token, token_type="bearer")
frontend/src/hooks/useAuth.ts:45 写入 localStorage.access_token
```

## 2. 受保护请求主链

```text
frontend/src/main.tsx:17-20 client.setConfig(baseURL, auth=localStorage token)
  → 任意 generated service 调用
  → backend/app/api/deps.py:30 get_current_user()
      ├─ jwt.decode(token, SECRET_KEY, HS256)
      ├─ TokenPayload(**payload) (backend/app/models.py:120)
      ├─ [Token 非法] HTTP 403 "Could not validate credentials"
      ├─ session.get(User, sub) (backend/app/api/deps.py:41)
      ├─ [用户不存在] HTTP 404 "User not found"
      └─ [未激活] HTTP 400 "Inactive user"
  → 路由内 owner 或 superuser 判定
```

注意：`backend/app/api/deps.py:36` 当前写作 `except InvalidTokenError, ValidationError:`，该行不是合法 Python 3 语法，会在导入阶段失败；修复方式见 [高危雷区](../operations/pitfalls-and-adr.md)。

## 3. 条目读写链

```text
GET /api/v1/items/
  → backend/app/api/routes/items.py:13 read_items()
      ├─ [superuser] select(func.count()).select_from(Item)
      ├─ [普通用户] where(Item.owner_id == current_user.id)
      └─ offset(skip).limit(limit) 默认 0/100
  → ItemsPublic(data=[ItemPublic], count)
```

写路径 `backend/app/api/routes/items.py:61-73` 在 `Item.model_validate(..., update={"owner_id": current_user.id})` 时强制写入当前用户，避免客户端伪造归属。

## 4. 邮件发送链

```text
users.create_user / login.recover_password
  → backend/app/utils.py:87 generate_new_account_email() 或 :70 generate_reset_password_email()
  → backend/app/utils.py:25 render_email_template()
  → backend/app/utils.py:34 send_email()
      ├─ 断言 settings.emails_enabled
      ├─ emails.message.Message(subject, html, mail_from)
      ├─ smtp_options = {host, port, tls|ssl, user, password}
      └─ message.send(to=email_to, smtp=smtp_options)
  → backend/app/utils.py:57 logger.info("send email result: ...")
```

## 5. 共变耦合与修改清单

1. 改登录返回：同步 `backend/app/api/routes/login.py:23-43`、`backend/app/models.py:114-118` 与前端 `frontend/src/hooks/useAuth.ts:41-46`。
2. 改鉴权依赖：同步 `backend/app/api/deps.py:30-57`、[接口全集](../contracts/api-reference.md) 与 [错误码](../contracts/error-codes.md)。
3. 改邮件上下文：同步 `backend/app/utils.py:70-102`、`packages/react-email/emails/*.tsx` 与 [邮件模板组件](../architecture/email-templates.md)。
