# 接口文档总索引

> 后端全部 HTTP 接口的权威契约在 [入向接口契约全集](../contracts/api-reference.md)，本页只做模块索引与导航，不重复维护逐接口字段。新增或修改接口时同时更新契约页与本索引。

> Source: `backend/app/api/main.py`、`backend/app/api/routes/`、`backend/app/models.py`
> Last-verified: 2026-11-19（静态核对）

---

## 一、协议与前缀

- 协议：HTTP + JSON，统一前缀 `/api/v1`，见 `backend/app/main.py:35`。
- 鉴权：OAuth2 密码流，Bearer JWT，见 `backend/app/api/deps.py:16-18`。
- OpenAPI：`/api/v1/openapi.json`，Swagger UI 在 `/docs`。
- 错误包络：`{"detail": "..."}`，状态码见 [错误码字典](../contracts/error-codes.md)。

## 二、模块清单

| 模块 | 源码路径 | 端点数 | 说明 |
|---|---|---|---|
| login | `backend/app/api/routes/login.py` | 5 | 登录、测试 Token、找回、重置、找回 HTML |
| users | `backend/app/api/routes/users.py` | 10 | 注册、本人资料、管理员用户管理 |
| items | `backend/app/api/routes/items.py` | 5 | 所有者隔离的条目 CRUD |
| utils | `backend/app/api/routes/utils.py` | 2 | 健康检查、测试邮件 |
| private | `backend/app/api/routes/private.py` | 1 | 仅 development 挂载的内部建号 |

## 三、接口清单导航

| 分组 | 契约位置 | 代表端点 |
|---|---|---|
| 登录与找回 | [契约全集](../contracts/api-reference.md) | `POST /api/v1/login/access-token` |
| 用户管理 | [契约全集](../contracts/api-reference.md) | `GET /api/v1/users/`、`PATCH /api/v1/users/me` |
| 条目 | [契约全集](../contracts/api-reference.md) | `GET /api/v1/items/`、`POST /api/v1/items/` |
| 工具 | [契约全集](../contracts/api-reference.md) | `GET /api/v1/utils/health-check/` |

## 四、维护规则

1. 先改 `backend/app/models.py` 的请求/响应模型，再改路由。
2. 更新 [契约全集](../contracts/api-reference.md) 的路由总表与分组入参表。
3. 运行 `scripts/generate-client.sh` 更新前端客户端。
4. 补 `backend/tests/api/routes/` 用例与 Playwright 相关流程。
