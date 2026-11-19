---
kind: integrations-index
scope: integrations
status: draft
origin: generated
source_paths: [backend/app/utils.py, backend/app/core/db.py, backend/app/main.py, frontend/src/main.tsx, packages/react-email/package.json]
symbols: [send_email, engine, sentry_sdk.init, client, export]
upstream: [INDEX.md]
downstream: [integrations/topology-and-mapping.md, integrations/downstream/postgresql.md, integrations/downstream/smtp.md, integrations/downstream/sentry.md]
---
# 上下游集成总览

本仓库的运行时上游是浏览器与测试客户端，下游是 PostgreSQL、SMTP 与可选的 Sentry；构建期还有 React Email 导出链。所有下游都在后端封装，前端不直接连接数据库或邮件服务器。

## 1. 双向拓扑

| 方向 | 对象 | 协议 | 入口 | 失败影响 |
|---|---|---|---|---|
| 上游 | React SPA | HTTP JSON | `frontend/src/main.tsx:17-20` | 页面无法加载数据，401/403 跳登录 |
| 上游 | Playwright | HTTP | `frontend/tests/config.ts` | 端到端用例失败 |
| 下游 | PostgreSQL | psycopg + SQLModel | `backend/app/core/db.py:7` | 所有读写失败，健康检查仍可能为真 |
| 下游 | SMTP | emails 库 | `backend/app/utils.py:34-57` | 建号/找回邮件失败，事务已提交 |
| 下游 | Sentry | HTTPS SDK | `backend/app/main.py:18-19` | 仅观测缺失，不影响请求 |
| 构建期 | React Email | CLI | `packages/react-email/package.json:9` | 模板不更新，运行时用旧 HTML |

## 2. 下游系统总表

| 下游 | 封装位置 | 契约页 | 是否必需 |
|---|---|---|---|
| PostgreSQL | `backend/app/core/db.py` | [PostgreSQL](downstream/postgresql.md) | 是 |
| SMTP | `backend/app/utils.py` | [SMTP](downstream/smtp.md) | 邮件功能必需 |
| Sentry | `backend/app/main.py` | [Sentry](downstream/sentry.md) | 否，可选 |

## 3. 入向调用方与边界

浏览器通过同域 `/api/v1` 调用；Playwright 通过 `PLAYWRIGHT_BASE_URL` 指向 Compose 后端；FastAPI Cloud 或自托管 Compose 是部署形态，不是业务下游。跨仓库依赖为空，本仓库不调用其他业务服务。

## 4. 字段映射入口

上游 DTO 到下游字典的转换集中在路由和 `backend/app/utils.py`。逐字段来源、默认值与错误翻译见 [参数组装与字段映射](topology-and-mapping.md)。

## 5. 共变耦合与修改清单

1. 新增下游：在 `integrations/downstream/` 新建契约页，补封装模块、配置项、错误翻译与测试。
2. 改连接串：同步 `backend/app/core/config.py:31`、`.env` 与 [配置手册](../contracts/configuration.md)。
3. 改邮件发送：同步 `backend/app/utils.py:34-57` 与 [SMTP 契约](downstream/smtp.md)。
