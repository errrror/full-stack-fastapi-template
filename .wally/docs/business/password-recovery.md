---
kind: business-workflow
scope: password-recovery
status: draft
origin: generated
source_paths: [backend/app/api/routes/login.py, backend/app/utils.py, backend/app/core/config.py, backend/app/models.py]
symbols: [recover_password, reset_password, generate_password_reset_token, verify_password_reset_token]
upstream: [business/index.md]
downstream: [business/auth-and-users.md, integrations/downstream/smtp.md, architecture/email-templates.md]
---
# 密码找回流程

密码找回分两步：先按邮箱签发短时 JWT 并通过邮件发送链接，再用令牌和新密码调用重置接口。申请接口刻意不暴露邮箱是否存在，避免枚举。

## 1. 申请阶段

```text
POST /api/v1/password-recovery/{email}
  → backend/app/api/routes/login.py:53 recover_password()
      ├─ backend/app/crud.py:34 get_user_by_email()
      ├─ [存在] backend/app/utils.py:105 generate_password_reset_token()
      │    └─ JWT {exp, nbf, sub=email}，有效期 48 小时
      ├─ [存在] backend/app/utils.py:70 generate_reset_password_email()
      └─ [存在] backend/app/utils.py:34 send_email()
  ← 固定文案 "If that email is registered, we sent a password recovery link"
```

无论用户是否存在都返回同一文案（`backend/app/api/routes/login.py:70-75`），这是防枚举设计。

## 2. 重置阶段

```text
POST /api/v1/reset-password/
  → backend/app/api/routes/login.py:77 reset_password()
      ├─ backend/app/utils.py:118 verify_password_reset_token()
      ├─ [无效] HTTP 400 "Invalid token"
      ├─ 查用户；不存在也返回 "Invalid token"
      ├─ [未激活] HTTP 400 "Inactive user"
      └─ crud.update_user(password=new_password) 重新哈希
```

## 3. 令牌与配置

| 项 | 值 | 来源 |
|---|---|---|
| 算法 | HS256 | `backend/app/core/security.py:19` |
| 签名密钥 | `SECRET_KEY` | `backend/app/core/config.py:23` |
| 有效期 | `EMAIL_RESET_TOKEN_EXPIRE_HOURS` 默认 48 | `backend/app/core/config.py:57` |
| 链接前缀 | `FRONTEND_HOST` 加 `/reset-password?token=` | `backend/app/utils.py:73` |

## 4. 失败与安全边界

| 场景 | 行为 | 说明 |
|---|---|---|
| 邮箱不存在 | 仍返回成功文案 | 防枚举 |
| 令牌过期/篡改 | 400 Invalid token | JWT 校验失败 |
| 用户被禁用 | 400 Inactive user | 不发放新密码 |
| 邮件发送失败 | 请求 500 | 令牌已生成但用户收不到 |
| 前端页面 | `/reset-password` 读取 query token | `frontend/src/routes/reset-password.tsx:49-60` |

补充源码锚点：`backend/app/models.py:124`。

## 5. 共变耦合与修改清单

1. 改有效期：同步 `backend/app/core/config.py:57` 与邮件模板的 `valid_hours`。
2. 改链接：同步 `backend/app/utils.py:70-84`、前端路由与 [邮件模板组件](../architecture/email-templates.md)。
3. 改令牌：同步 `backend/app/utils.py:105-125`、[认证流程](auth-and-users.md) 与测试。
