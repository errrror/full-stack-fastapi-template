---
kind: architecture-index
scope: components
status: draft
origin: generated
source_paths: [backend/app/api/main.py, backend/app/core/config.py, frontend/src/main.tsx, packages/react-email/package.json, scripts/generate-client.sh]
symbols: [api_router, settings, client, export, generate-client]
upstream: [INDEX.md]
downstream: [architecture/api-service.md, architecture/frontend-spa.md, architecture/email-templates.md, architecture/module-dep-matrix.md]
---
# 组件总表与目录覆盖

仓库只有三个独立交付组件：FastAPI 后端、React 前端、React Email 模板包；其余目录是构建、CI、Agent 配置或静态资产。下面的目录表用于确认没有源码目录被遗漏。

## 1. 多态组件总表

| 组件 | 模型 | 源码根 | 运行形态 | 文档 |
|---|---|---|---|---|
| backend | API 服务 | `backend/app` | 常驻 FastAPI，4 worker | [API 服务](api-service.md) |
| frontend | UI 单页应用 | `frontend/src` | Vite 构建后由 FastAPI 同域托管 | [前端 SPA](frontend-spa.md) |
| emails | 构建期库 | `packages/react-email` | `email export` 生成静态 HTML | [邮件模板](email-templates.md) |

## 2. 顶层与二级目录覆盖对账

| 目录 | 归属 | 角色 | 文档落点 |
|---|---|---|---|
| `backend` | backend | 服务根、Dockerfile、pyproject、README | [API 服务](api-service.md) |
| `backend/app` | backend | Python 应用源码根 | [API 服务](api-service.md) |
| `backend/app/api` | backend | 路由、依赖、鉴权 | [API 服务](api-service.md) |
| `backend/app/api/routes` | backend | login/users/items/utils/private | [接口全集](../contracts/api-reference.md) |
| `backend/app/core` | backend | 配置、DB、安全 | [配置手册](../contracts/configuration.md) |
| `backend/app/alembic` | backend | 迁移环境与版本 | [PostgreSQL 契约](../integrations/downstream/postgresql.md) |
| `backend/app/alembic/versions` | backend | 5 个迁移脚本 | [领域模型总览](../business/domain-models/index.md) |
| `backend/app/email-templates` | backend | 已导出的 Jinja HTML | [邮件模板](email-templates.md) |
| `backend/tests` | backend | Pytest 用例与 fixture | [构建与单测](../operations/dev-and-test.md) |
| `backend/scripts` | backend | prestart、test、lint | [构建与单测](../operations/dev-and-test.md) |
| `frontend` | frontend | SPA 根、Vite/Playwright 配置 | [前端 SPA](frontend-spa.md) |
| `frontend/src` | frontend | React 源码根 | [前端 SPA](frontend-spa.md) |
| `frontend/src/client` | frontend | OpenAPI 生成客户端 | [前端 SPA](frontend-spa.md) |
| `frontend/src/components` | frontend | Admin/Items/UserSettings/UI | [前端 SPA](frontend-spa.md) |
| `frontend/src/hooks` | frontend | 认证与 UI hook | [前端 SPA](frontend-spa.md) |
| `frontend/src/lib` | frontend | 通用工具 | [前端 SPA](frontend-spa.md) |
| `frontend/src/routes` | frontend | TanStack 文件路由 | [前端 SPA](frontend-spa.md) |
| `frontend/public` | frontend | 静态资源与站点图标 | [前端 SPA](frontend-spa.md) |
| `frontend/tests` | frontend | Playwright 用例 | [构建与单测](../operations/dev-and-test.md) |
| `packages` | emails | Bun workspace 根 | [邮件模板](email-templates.md) |
| `packages/react-email` | emails | 构建包根、package.json | [邮件模板](email-templates.md) |
| `packages/react-email/emails` | emails | 三类邮件模板 | [邮件模板](email-templates.md) |
| `packages/react-email/ui` | emails | 共享邮件组件 | [邮件模板](email-templates.md) |
| `scripts` | 根 | SDK 生成、发布、测试脚本 | [构建与单测](../operations/dev-and-test.md) |
| `.github/workflows` | 根 | CI/CD 与依赖治理 | [部署与运行时](../operations/deployment-and-runtime.md) |
| `.github` | 根 | Dependabot、PR 与 issue 配置 | [边界](../operations/boundary.md) |
| `.codebuddy` | 根 | CodeBuddy skill、hook 与 Token 脚本 | [边界](../operations/boundary.md) |
| `.vscode` | 根 | 编辑器配置 | [边界](../operations/boundary.md) |
| `.wally` | 根 | SOP 规则、任务与知识库 | [边界](../operations/boundary.md) |
| `hooks` | 根 | Cookiecutter 生成后脚本 | [边界](../operations/boundary.md) |
| `img` | 根 | README 截图 | [边界](../operations/boundary.md) |
| `.agents`、`.claude` | 根 | 包提供的 Agent skill 链接 | [边界](../operations/boundary.md) |

## 3. Tier 3 工具与资产

| 资产 | 用途 | 注意 |
|---|---|---|
| `scripts/generate-client.sh` | 从后端 OpenAPI 生成前端客户端 | 会执行 `bun run lint`，需要 Bun |
| `scripts/prepare_release.py` | 读取/推进 release-notes 版本 | 不创建 tag |
| `scripts/add_latest_release_date.py` | 给最新 release 标题补日期 | pre-commit 触发 |
| `frontend/src/routeTree.gen.ts` | TanStack 路由树 | 生成文件，不手工编辑 |
| `frontend/src/client/**` | OpenAPI 客户端 | 生成文件，改接口后重跑生成器 |

## 4. 组件边界

后端不直接渲染 React 组件，只提供静态目录；前端不直连 PostgreSQL 或 SMTP，只调用 `/api/v1`；邮件包不参与运行时，只把 HTML 导出到 `backend/app/email-templates`。跨组件改动优先看 [模块依赖矩阵](module-dep-matrix.md)。

补充源码锚点：`backend/app/api/main.py:6`、`backend/app/core/config.py:14`、`frontend/src/main.tsx:17`、`packages/react-email/package.json:9`。

## 5. 共变耦合与修改清单

1. 新增顶级目录：同步本页覆盖表、[边界](../operations/boundary.md) 与 `.wiki-meta.json` 的 `moduleTree`。
2. 新增生成脚本：同步 `scripts/` 说明与 [构建与单测](../operations/dev-and-test.md)。
3. 调整组件边界：同步 [系统架构](../overview/system-architecture.md) 与 [集成总览](../integrations/index.md)。
