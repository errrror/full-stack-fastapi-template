---
kind: architecture-index
scope: module-dependencies
status: draft
origin: generated
source_paths: [backend/app/api/main.py, backend/app/api/deps.py, backend/app/core/db.py, backend/app/utils.py, frontend/src/main.tsx, frontend/openapi-ts.config.ts]
symbols: [api_router, get_db, engine, client, defineConfig]
upstream: [INDEX.md]
downstream: [architecture/index.md, integrations/index.md, overview/system-architecture.md]
---
# 模块依赖矩阵

依赖关系以导入和运行时调用为准，不以目录相邻关系推断。后端内部是“路由 → 依赖 → CRUD/模型 → engine”的单向链；前端内部是“路由 → hooks → 生成客户端 → axios”；两端只通过 HTTP 契约耦合。

## 1. 后端模块依赖边

| 源模块 | 目标模块 | 依赖符号 | 边类型 | 证据 |
|---|---|---|---|---|
| `backend/app/main.py` | `backend/app/api/main.py` | `api_router` | 导入并挂载 | `backend/app/main.py:8` |
| `backend/app/api/main.py` | `backend/app/api/routes/*` | `login/users/items/utils/private` | 注册 | `backend/app/api/main.py:7-14` |
| `backend/app/api/routes/*` | `backend/app/api/deps.py` | `SessionDep/CurrentUser` | 依赖注入 | `backend/app/api/routes/items.py:4` |
| `backend/app/api/deps.py` | `backend/app/core/db.py` | `engine` | 创建 Session | `backend/app/api/deps.py:13-23` |
| `backend/app/api/routes/*` | `backend/app/crud.py` | `authenticate/create_user` | 业务调用 | `backend/app/api/routes/login.py:32` |
| `backend/app/crud.py` | `backend/app/models.py` | `User/Item` | ORM 模型 | `backend/app/crud.py:7` |
| `backend/app/utils.py` | `backend/app/core/config.py` | `settings` | 配置读取 | `backend/app/utils.py:13` |

## 2. 前端模块依赖边

| 源模块 | 目标模块 | 依赖符号 | 边类型 | 证据 |
|---|---|---|---|---|
| `frontend/src/main.tsx` | `frontend/src/client/client.gen` | `client` | 配置 baseURL 与 auth | `frontend/src/main.tsx:11-20` |
| `frontend/src/hooks/useAuth.ts` | `frontend/src/client` | `LoginService/UsersService` | 生成服务调用 | `frontend/src/hooks/useAuth.ts:4-10` |
| `frontend/src/routes/_layout.tsx` | `frontend/src/hooks/useAuth.ts` | `isLoggedIn` | 路由守卫 | `frontend/src/routes/_layout.tsx:10-20` |
| `frontend/openapi-ts.config.ts` | `frontend/src/client` | 生成配置 | 构建期 | `frontend/openapi-ts.config.ts:4-19` |

## 3. 扇入、扇出与环检测

- 最高扇入：`backend/app/core/config.py`（几乎所有后端模块读取 `settings`）与 `backend/app/models.py`（CRUD、路由、测试共享）。
- 最高扇出：`backend/app/api/routes/users.py` 同时依赖 crud、security、config、models 与 utils。
- 环检测：后端未发现循环导入；前端 `client` 不反向导入 hooks 或 routes，未发现环。
- 跨仓依赖：本仓库无其他业务仓库，`repoDeps` 为空；外部依赖只有 PostgreSQL、SMTP、Sentry，见 [集成总览](../integrations/index.md)。

## 4. 改动影响规则

改 `models.py` 会影响 Alembic、crud、路由、测试与前端生成类型；改 `deps.py` 会影响所有受保护路由；改 `client` 生成配置会影响所有前端 API 调用。把这些文件作为高扇入节点，提交前跑对应测试与客户端生成。

## 5. 共变耦合与修改清单

1. 新增后端模块：同步 `backend/app/api/main.py`、本页依赖表与 [系统架构](../overview/system-architecture.md)。
2. 新增前端服务：先改后端 OpenAPI，再跑 `scripts/generate-client.sh`，最后更新 `frontend/src/client` 与调用方。
3. 新增外部依赖：同步 [集成总览](../integrations/index.md) 与对应下游契约页。
