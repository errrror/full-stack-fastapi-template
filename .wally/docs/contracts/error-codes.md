---
kind: api-contract
scope: errors
status: draft
origin: generated
source_paths: [backend/app/api/deps.py, backend/app/api/routes/login.py, backend/app/api/routes/users.py, backend/app/api/routes/items.py]
symbols: [get_current_user, login_access_token, read_user_by_id, read_item]
upstream: [INDEX.md]
downstream: [contracts/api-reference.md, business/index.md, operations/runbook-and-observability.md]
---
# 错误码与失败语义

后端没有集中错误码表，所有错误都是 `HTTPException(detail=...)`。本页按状态码汇总实际文案与触发位置，供前端提示和排障使用。

## 1. HTTP 状态总表

| 状态 | 语义 | 典型触发 | 文案示例 |
|---|---|---|---|
| 400 | 请求可解析但业务拒绝 | 密码错误、未激活、令牌无效 | `Incorrect email or password` |
| 403 | 身份无效或无权限 | Token 非法、非超级用户、越权 | `The user doesn't have enough privileges` |
| 404 | 资源不存在 | 用户或条目查不到 | `Item not found` |
| 409 | 唯一性冲突 | 邮箱被占用 | `User with this email already exists` |
| 422 | Schema 校验失败 | 邮箱格式、标题为空 | FastAPI 默认结构 |

## 2. 认证与登录错误

| 文案 | 状态 | 位置 |
|---|---|---|
| `Could not validate credentials` | 403 | `backend/app/api/deps.py:36-40` |
| `User not found` | 404 | `backend/app/api/deps.py:42-43` |
| `Inactive user` | 400 | `backend/app/api/deps.py:44-45` |
| `Incorrect email or password` | 400 | `backend/app/api/routes/login.py:34-35` |
| `Inactive user` | 400 | `backend/app/api/routes/login.py:38-39` |
| `Invalid token` | 400 | `backend/app/api/routes/login.py:80-85` |

## 3. 用户与条目错误

| 文案 | 状态 | 位置 |
|---|---|---|
| `The user with this email already exists in the system.` | 400 | `backend/app/api/routes/users.py:60-64` |
| `User with this email already exists` | 409 | `backend/app/api/routes/users.py:88-91` |
| `Super users are not allowed to delete themselves` | 403 | `backend/app/api/routes/users.py:135-137` |
| `The user doesn't have enough privileges` | 403 | `backend/app/api/routes/users.py:170-173` |
| `Item not found` | 404 | `backend/app/api/routes/items.py:52-53` |
| `Not enough permissions` | 403 | `backend/app/api/routes/items.py:54-55` |

## 4. 前端处理

`frontend/src/main.tsx:22-30` 只对 401/403 做统一处理：清除 localStorage 的 `access_token` 并跳转 `/login`。其他错误由 `frontend/src/utils.ts:3-17` 提取 `detail` 或 `msg`，再经 toast 展示。错误文案是用户可见内容，改后端 detail 会影响 E2E 断言。

相关页面：[业务总表](../business/index.md)、[排障 Runbook](../operations/runbook-and-observability.md)。

## 5. 共变耦合与修改清单

1. 新增错误：同步本页、[接口全集](api-reference.md) 与前端提示。
2. 改状态码：检查 Playwright 断言与 `frontend/src/main.tsx:22-30` 的跳转逻辑。
3. 改 detail：搜索 `frontend/tests/` 是否断言该文案。
