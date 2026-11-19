---
kind: api-contract
scope: inbound-api
status: draft
origin: generated
source_paths: [backend/app/api/main.py, backend/app/api/routes/login.py, backend/app/api/routes/users.py, backend/app/api/routes/items.py, backend/app/api/routes/utils.py, backend/app/api/routes/private.py]
symbols: [api_router, login_access_token, read_users, read_items, health_check]
upstream: [INDEX.md]
downstream: [contracts/error-codes.md, integrations/topology-and-mapping.md, business/index.md]
---
# 入向接口契约全集

后端全部 HTTP 接口挂在 `/api/v1` 下，使用 JSON 与 OAuth2 Bearer Token。成功响应直接返回 Pydantic 模型；失败统一为 `{"detail": "..."}`，状态码由 `HTTPException` 指定。

## 1. 公共协议与鉴权

| 维度 | 规则 | 证据 |
|---|---|---|
| 统一前缀 | `settings.API_V1_STR` 默认 `/api/v1` | `backend/app/main.py:35` |
| 认证 | OAuth2 密码流，Bearer JWT | `backend/app/api/deps.py:16-18` |
| 文档 | OpenAPI JSON 在 `/api/v1/openapi.json` | `backend/app/main.py:23` |
| 错误包络 | `{"detail": string}` | `backend/app/api/deps.py:37-40` |
| 日期 | ISO 8601 UTC | `backend/app/models.py:8-10` |

## 2. 全量路由总表（23 个）

| 分组 | 方法 | 路径 | 鉴权 | Handler |
|---|---|---|---|---|
| login | POST | `/api/v1/login/access-token` | 公开 | `login_access_token` (`backend/app/api/routes/login.py:23`) |
| login | POST | `/api/v1/login/test-token` | 当前用户 | `test_token` (`:45`) |
| login | POST | `/api/v1/password-recovery/{email}` | 公开 | `recover_password` (`:53`) |
| login | POST | `/api/v1/reset-password/` | 公开 | `reset_password` (`:77`) |
| login | POST | `/api/v1/password-recovery-html-content/{email}` | 超级用户 | `recover_password_html_content` (`:100`) |
| users | GET | `/api/v1/users/` | 超级用户 | `read_users` (`backend/app/api/routes/users.py:32`) |
| users | POST | `/api/v1/users/` | 超级用户 | `create_user` (`:54`) |
| users | PATCH | `/api/v1/users/me` | 当前用户 | `update_user_me` (`:81`) |
| users | PATCH | `/api/v1/users/me/password` | 当前用户 | `update_password_me` (`:103`) |
| users | GET | `/api/v1/users/me` | 当前用户 | `read_user_me` (`:124`) |
| users | DELETE | `/api/v1/users/me` | 当前用户 | `delete_user_me` (`:132`) |
| users | POST | `/api/v1/users/signup` | 公开 | `register_user` (`:146`) |
| users | GET | `/api/v1/users/{user_id}` | 当前用户或超级用户 | `read_user_by_id` (`:162`) |
| users | PATCH | `/api/v1/users/{user_id}` | 超级用户 | `update_user` (`:182`) |
| users | DELETE | `/api/v1/users/{user_id}` | 超级用户 | `delete_user` (`:214`) |
| items | GET | `/api/v1/items/` | 当前用户 | `read_items` (`backend/app/api/routes/items.py:13`) |
| items | GET | `/api/v1/items/{id}` | 当前用户 | `read_item` (`:48`) |
| items | POST | `/api/v1/items/` | 当前用户 | `create_item` (`:61`) |
| items | PUT | `/api/v1/items/{id}` | 当前用户 | `update_item` (`:75`) |
| items | DELETE | `/api/v1/items/{id}` | 当前用户 | `delete_item` (`:99`) |
| utils | POST | `/api/v1/utils/test-email/` | 超级用户 | `test_email` (`backend/app/api/routes/utils.py:11`) |
| utils | GET | `/api/v1/utils/health-check/` | 公开 | `health_check` (`:29`) |
| private | POST | `/api/v1/private/users/` | 仅 development | `create_user` (`backend/app/api/routes/private.py:23`) |

## 3. 分组入参与出参

| 分组 | 入参 | 出参 | 备注 |
|---|---|---|---|
| login | `OAuth2PasswordRequestForm` 的 `username/password` | `Token(access_token, token_type)` | `username` 实际是邮箱 |
| users | `UserCreate/UserUpdate/UserUpdateMe/UpdatePassword` | `UserPublic/UsersPublic/Message` | 密码只进不出 |
| items | `ItemCreate/ItemUpdate` 与分页 `skip/limit` | `ItemPublic/ItemsPublic/Message` | `owner_id` 服务端注入 |
| utils | `email_to` 查询参数 | `Message` 或 bool | 测试邮件只允许超级用户 |
| private | `PrivateUserCreate(email,password,full_name,is_verified)` | `UserPublic` | 不做唯一性检查 |

## 4. 错误分支

| 状态 | 触发 | 示例 |
|---|---|---|
| 400 | 凭据错误、未激活、令牌无效、新旧密码相同 | `Incorrect email or password` |
| 403 | Token 非法、非超级用户、越权条目 | `Not enough privileges` |
| 404 | 用户或条目不存在 | `Item not found` |
| 409 | 邮箱已被其他用户占用 | `User with this email already exists` |
| 422 | Pydantic 校验失败 | 标题为空、邮箱格式错误 |

相关页面：[业务总表](../business/index.md)、[排障 Runbook](../operations/runbook-and-observability.md)。

## 5. 共变耦合与修改清单

1. 新增接口：在 `backend/app/api/routes/` 实现，注册到 `backend/app/api/main.py:7-10`，更新本页与 [错误码](error-codes.md)。
2. 改 Schema：同步 `backend/app/models.py`、本页分组表与前端生成客户端。
3. 改鉴权：同步 `backend/app/api/deps.py` 与本页鉴权列。
