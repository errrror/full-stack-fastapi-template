---
kind: business-workflow
scope: auth-and-users
status: draft
origin: generated
source_paths: [backend/app/api/routes/login.py, backend/app/api/routes/users.py, backend/app/api/deps.py, backend/app/core/security.py, backend/app/crud.py]
symbols: [login_access_token, register_user, create_user, get_current_user, authenticate]
upstream: [business/index.md]
downstream: [business/domain-models/user.md, contracts/api-reference.md, contracts/error-codes.md]
---
# 认证与用户流程

认证由 OAuth2 密码流完成：`/login/access-token` 校验邮箱密码并签发 JWT，后续请求用 Bearer Token 解析用户。用户管理区分自助注册与管理员建号，两者共享唯一性与哈希规则。

## 1. 登录符号调用树

```text
POST /api/v1/login/access-token
  → backend/app/api/routes/login.py:23 login_access_token()
      ├─ backend/app/crud.py:45 authenticate(email, password)
      │    ├─ backend/app/crud.py:34 get_user_by_email()
      │    ├─ [不存在] verify_password(password, DUMMY_HASH) 防时序
      │    └─ [存在] verify_password() 并在需要时升级哈希
      ├─ [失败] HTTP 400 "Incorrect email or password"
      ├─ [未激活] HTTP 400 "Inactive user"
      └─ backend/app/core/security.py:22 create_access_token(sub=user.id)
  ← Token(access_token, token_type="bearer")
```

## 2. 用户创建的三条路径

| 路径 | 入口 | 权限 | 差异 |
|---|---|---|---|
| 自助注册 | `POST /api/v1/users/signup` | 匿名 | 使用 `UserRegister`，不接受 `is_superuser` |
| 管理员建号 | `POST /api/v1/users/` | 超级用户 | 使用 `UserCreate`，可设 `is_superuser` |
| 开发内部建号 | `POST /api/v1/private/users/` | 仅 development | 使用 `PrivateUserCreate`，不做唯一性检查 |

自助注册与管理员建号都会先查邮箱，存在则 400；`backend/app/crud.py:10-17` 统一哈希密码。

## 3. 权限校验

| 依赖 | 检查 | 失败 | 证据 |
|---|---|---|---|
| `get_current_user` | JWT 解码、用户存在、`is_active` | 403/404/400 | `backend/app/api/deps.py:30-46` |
| `get_current_active_superuser` | `is_superuser` | 403 | `backend/app/api/deps.py:52-57` |
| 资源归属 | `owner_id == current_user.id` 或超级用户 | 403 | `backend/app/api/routes/items.py:48-59` |

## 4. 用户更新与删除

- 本人更新：`PATCH /users/me` 只允许 `full_name` 与 `email`，邮箱冲突返回 409。
- 本人改密：`PATCH /users/me/password` 校验旧密码，新旧相同返回 400。
- 本人删除：`DELETE /users/me` 拒绝超级用户自删，普通用户删除后条目级联删除。
- 管理员更新/删除：`PATCH/DELETE /users/{user_id}` 需要超级用户；删除前显式删除条目再删用户。

补充源码锚点：`backend/app/api/routes/users.py:54`。

## 5. 共变耦合与修改清单

1. 改 Token：同步 `backend/app/core/security.py:22-26`、`backend/app/api/deps.py:30-46` 与前端 `frontend/src/hooks/useAuth.ts`。
2. 改用户字段：同步 `backend/app/models.py:13-62`、`backend/app/crud.py` 与 [用户模型](domain-models/user.md)。
3. 改权限：同步 [接口全集](../contracts/api-reference.md) 与 Playwright 的 admin 用例。
