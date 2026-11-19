---
kind: component
scope: backend-api
status: draft
origin: generated
source_paths: [backend/app/main.py, backend/app/api/main.py, backend/app/api/deps.py, backend/app/api/routes/utils.py, backend/app/api/routes/items.py]
symbols: [app, api_router, get_current_user, health_check, read_items]
upstream: [contracts/api-reference.md]
downstream: [integrations/index.md, business/auth-and-users.md, architecture/module-dep-matrix.md]
---
# backend（API 服务组件）

后端是同步 FastAPI 应用，路由前缀统一为 `/api/v1`，鉴权使用 OAuth2 密码流 + Bearer JWT。数据库会话通过依赖注入按请求创建，业务处理以同步函数执行，由 FastAPI 线程池承接。

## 1. 请求处理洋葱链

```text
HTTP Request
  ├─ [1. CORS] backend/app/main.py:27-33 allow_origins=[FRONTEND_HOST]
  ├─ [2. route] backend/app/api/main.py:7-10 login/users/utils/items
  ├─ [3. auth] backend/app/api/deps.py:30-46 get_current_user()
  ├─ [4. role] backend/app/api/deps.py:52-57 get_current_active_superuser()
  ├─ [5. session] backend/app/api/deps.py:21-23 get_db() -> Session
  ├─ [6. handler] 同步函数，经 FastAPI 线程池执行
  └─ [7. error] HTTPException -> {"detail": "..."}
```

## 2. 路由分组与执行模型

| 路由组 | 前缀 | 端点数 | 鉴权 | 执行模型 | 下游 |
|---|---|---|---|---|---|
| login | 无 | 5 | 公开或当前用户 | 同步 | crud、security、utils |
| users | `/users` | 10 | 当前用户或超级用户 | 同步 | crud、security、utils |
| items | `/items` | 5 | 当前用户 | 同步 | models、Session |
| utils | `/utils` | 2 | 公开或超级用户 | 同步 | utils |
| private | `/private` | 1 | 无，仅开发模式 | 同步 | security、models |

## 3. 核心源码与符号

| 文件 | 符号 | 职责 |
|---|---|---|
| `backend/app/main.py:21-36` | `app` | 创建应用、CORS、路由与静态前端 |
| `backend/app/api/main.py:6-14` | `api_router` | 汇总四组路由并按环境挂载 private |
| `backend/app/api/deps.py:16-57` | `get_current_user` | Token 解码、用户加载、激活与超级用户校验 |
| `backend/app/api/routes/utils.py:29-31` | `health_check` | 返回布尔健康信号 |
| `backend/app/api/routes/items.py:13-46` | `read_items` | 按角色构造 count 与分页查询 |

## 4. 上游与下游

上游是浏览器 SPA、Playwright 测试与直接 API 调用方；下游是 PostgreSQL（经 SQLModel）与 SMTP（经 `backend/app/utils.py`）。外部系统细节见 [SMTP 契约](../integrations/downstream/smtp.md) 与 [PostgreSQL 契约](../integrations/downstream/postgresql.md)。

## 5. 共变耦合与修改清单

1. 新增路由：在 `backend/app/api/routes/` 新建模块，注册到 `backend/app/api/main.py:7-10`，补 `contracts/api-reference.md` 与测试。
2. 修改鉴权：同步 `backend/app/api/deps.py:30-57`、前端 `frontend/src/main.tsx:17-30` 与 [错误码](../contracts/error-codes.md)。
3. 修改执行模型：若引入阻塞 IO，明确是否需要 `run_in_threadpool`；当前全部为同步函数。
