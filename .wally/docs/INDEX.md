# full-stack-fastapi-template · Agent 知识库总路由表（INDEX）

> **Agent 读取规程（必读）**
> 1. 禁止一次性读取 `.wally/docs/` 全部文件。先查本页「任务意图路由表」或「源码路径反向索引」，只打开命中的 1 至 3 篇文档，先看 YAML 头确认 `source_paths`、`symbols` 与 `status`。
> 2. 本库页面均为 `status: draft`、`origin: generated`。从文档取得 `路径:行号`、字段字典与共变清单后，修改前必须回到源码字面复核；近邻命中不等于事实。
> 3. 标记 `origin: human` 或 `status: verified` 的页面是人工确认结论，重跑不得覆盖。当前基准：`master` @ `77e550a`。

本仓库是一个全栈应用模板：后端为 Python 3.14 + FastAPI + SQLModel + PostgreSQL，前端为 React 19 + Vite + TanStack Router/Query，二者通过生成的 OpenAPI 客户端对接；`packages/react-email` 负责构建后端发送的 HTML 邮件模板。

## 1. 任务意图最短路由表

| 待办任务类型 | 按序必读 |
|---|---|
| 新增或修改 HTTP 接口 | [入向接口全集](contracts/api-reference.md) → [API 服务组件](architecture/api-service.md) → [错误码字典](contracts/error-codes.md) |
| 修改登录、权限或用户管理 | [认证与用户流程](business/auth-and-users.md) → [用户模型](business/domain-models/user.md) → [模块依赖矩阵](architecture/module-dep-matrix.md) |
| 修改条目 CRUD 或所有者隔离 | [条目流程](business/items.md) → [条目模型](business/domain-models/item.md) → [入向接口全集](contracts/api-reference.md) |
| 修改前端路由、鉴权跳转或请求客户端 | [前端 SPA 组件](architecture/frontend-spa.md) → [入向接口全集](contracts/api-reference.md) → [配置手册](contracts/configuration.md) |
| 修改邮件模板或邮件发送 | [邮件模板组件](architecture/email-templates.md) → [SMTP 下游契约](integrations/downstream/smtp.md) → [密码找回流程](business/password-recovery.md) |
| 新增环境变量或部署配置 | [配置手册](contracts/configuration.md) → [部署与运行时](operations/deployment-and-runtime.md) → [边界声明](operations/boundary.md) |
| 定位报错、构建失败或启动失败 | [高危雷区](operations/pitfalls-and-adr.md) → [排障 Runbook](operations/runbook-and-observability.md) → [主干调用链](overview/callchain-panorama.md) |
| 评估改动影响与必跑测试 | [模块依赖矩阵](architecture/module-dep-matrix.md) → [构建与单测映射](operations/dev-and-test.md) → [系统架构](overview/system-architecture.md) |

## 2. 源码路径反向索引

| 源码路径 | 角色 | 首选文档 |
|---|---|---|
| `backend/app/main.py` | FastAPI 装配入口 | [系统架构](overview/system-architecture.md) |
| `backend/app/api/` | 路由与鉴权依赖 | [API 服务组件](architecture/api-service.md) |
| `backend/app/core/` | 配置、数据库引擎、密码与 JWT | [配置手册](contracts/configuration.md) |
| `backend/app/crud.py` | 用户与条目的持久化操作 | [领域模型总览](business/domain-models/index.md) |
| `backend/app/utils.py` | 邮件渲染、发送与重置令牌 | [SMTP 下游契约](integrations/downstream/smtp.md) |
| `backend/app/alembic/` | 数据库迁移 | [PostgreSQL 下游契约](integrations/downstream/postgresql.md) |
| `backend/tests/` | Pytest 测试 | [构建与单测映射](operations/dev-and-test.md) |
| `frontend/src/` | React 单页应用 | [前端 SPA 组件](architecture/frontend-spa.md) |
| `frontend/tests/` | Playwright 端到端测试 | [构建与单测映射](operations/dev-and-test.md) |
| `packages/react-email/` | 邮件模板构建包 | [邮件模板组件](architecture/email-templates.md) |
| `compose.yml` | 本地与自托管运行拓扑 | [部署与运行时](operations/deployment-and-runtime.md) |
| `.github/workflows/` | CI、部署与发布自动化 | [构建与单测映射](operations/dev-and-test.md) |

## 3. 组件能力清单

| 组件 | 模型 | 源码根 | 核心入口 | 文档 |
|---|---|---|---|---|
| backend | API 服务 | `backend/app` | `app` (`backend/app/main.py:21`) | [查看](architecture/api-service.md) |
| frontend | UI 单页应用 | `frontend/src` | `client.setConfig` (`frontend/src/main.tsx:17`) | [查看](architecture/frontend-spa.md) |
| emails | 构建期模板库 | `packages/react-email` | `email export` (`packages/react-email/package.json:9`) | [查看](architecture/email-templates.md) |

## 4. 业务流程与下游依赖速查

- 全景认知：[系统架构](overview/system-architecture.md)、[业务架构](overview/business-architecture.md)、[调用链全景](overview/callchain-panorama.md)、[术语表](overview/glossary.md)。
- 上下游与契约：[集成总览](integrations/index.md)、[字段映射](integrations/topology-and-mapping.md)、[接口全集](contracts/api-reference.md)、[配置手册](contracts/configuration.md)。
- 业务与数据：[业务总表](business/index.md)、[领域模型](business/domain-models/index.md)。
- 运行保障：[构建与单测](operations/dev-and-test.md)、[部署与运行时](operations/deployment-and-runtime.md)、[排障 Runbook](operations/runbook-and-observability.md)、[高危雷区](operations/pitfalls-and-adr.md)、[边界](operations/boundary.md)。

## 5. 外部权威页与执行规范

下列页面由 SOP 初始化生成，属于执行规范或既有权威文档，不在本知识库的生成页集合内；本库只链接，不复制其命令正文。

- [接口文档索引](apis/index.md)、[数据库结构说明](sqls/README.md)。
- [单元测试规范](unittest/unittest.md)、[集成测试规范](integration_test/integration_test.md)。
- [本地环境搭建](devops/env.md)、[测试环境部署](devops/test-env-deploy.md)。

## 6. 维护约定

本库以 `master` 的已提交源码为基线生成；`.wally/` 与 `AGENTS.md` 是本次初始化新增的未跟踪内容，尚未进入提交基线。源码变动后先跑 `operations/boundary.md` 的核对清单，再更新受影响页与 `.wiki-meta.json`。
