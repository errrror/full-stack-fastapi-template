---
kind: component
scope: frontend-spa
status: draft
origin: generated
source_paths: [frontend/src/main.tsx, frontend/src/hooks/useAuth.ts, frontend/src/routes/_layout.tsx, frontend/src/routes/login.tsx, frontend/openapi-ts.config.ts, frontend/vite.config.ts]
symbols: [client, useAuth, Route, createFileRoute, defineConfig]
upstream: [contracts/api-reference.md]
downstream: [architecture/api-service.md, business/auth-and-users.md, operations/dev-and-test.md]
---
# frontend（React 单页应用组件）

前端是 React 19 + Vite 的 SPA，使用 TanStack Router 文件路由与 TanStack Query 管理服务端状态。所有 API 调用走 `@hey-api/openapi-ts` 生成的服务，Token 存在 localStorage，401/403 时统一清理并跳转登录。

## 1. 启动与路由装配

```text
frontend/src/main.tsx:17-20 client.setConfig(baseURL, auth)
  → frontend/src/main.tsx:40 createRouter({ routeTree })
  → frontend/src/routes/__root.tsx:7 createRootRoute()
      ├─ HeadContent + Outlet
      ├─ notFoundComponent -> NotFound
      └─ errorComponent -> ErrorComponent
  → frontend/src/routes/_layout.tsx:12 createFileRoute("/_layout")
      └─ beforeLoad: isLoggedIn() ? 放行 : redirect("/login")
```

页面路由包括 `/login`、`/signup`、`/recover-password`、`/reset-password`，以及受保护的 `/_layout/`、`/_layout/items`、`/_layout/admin`、`/_layout/settings`，定义见 `frontend/src/routes/login.tsx:35` 与 `frontend/src/routes/_layout.tsx:12`。

## 2. 鉴权状态机

| 状态 | 判定 | 行为 | 源码 |
|---|---|---|---|
| 未登录 | localStorage 无 `access_token` | 访问受保护路由跳 `/login` | `frontend/src/routes/_layout.tsx:14-20` |
| 已登录 | localStorage 有值 | 允许进入并请求 `users/me` | `frontend/src/hooks/useAuth.ts:23-27` |
| Token 失效 | API 返回 401/403 | 清除 Token，整页跳 `/login` | `frontend/src/main.tsx:22-30` |
| 主动退出 | 点击退出 | 清除 Token 并跳登录 | `frontend/src/hooks/useAuth.ts:56-59` |

## 3. 数据获取与契约生成

`frontend/openapi-ts.config.ts:4-19` 从 `openapi.json` 生成 `src/client`，使用 axios 客户端、`throwOnError: true` 与按 tag 分组的静态服务。后端改路由后必须重跑 `scripts/generate-client.sh`，再提交生成文件。

## 4. 构建产物与托管

`frontend/vite.config.ts:9-12` 将产物写入 `../backend/app/frontend` 并清空旧目录；后端 `backend/app/main.py:36` 用 `app.frontend("/")` 同域托管。开发时 Vite 运行在 5173，`frontend/.env` 的 `VITE_API_URL=http://localhost:8000` 指向后端。

## 5. 共变耦合与修改清单

1. 新增页面：在 `frontend/src/routes/` 建文件路由，补导航与 Playwright 用例。
2. 改 API 契约：先改后端，再生成客户端，最后更新调用组件；参考 [接口全集](../contracts/api-reference.md)。
3. 改鉴权存储：同步 `frontend/src/hooks/useAuth.ts`、`frontend/src/main.tsx` 与 [认证流程](../business/auth-and-users.md)。
