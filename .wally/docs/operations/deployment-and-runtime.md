---
kind: operations
scope: deployment-runtime
status: draft
origin: generated
source_paths: [compose.yml, compose.deploy.yml, backend/Dockerfile, deployment.md, .github/workflows/deploy-docker-compose.yml]
symbols: [backend, proxy, db, CMD, prestart]
upstream: [INDEX.md]
downstream: [devops/test-env-deploy.md, contracts/configuration.md, operations/runbook-and-observability.md]
---
# 部署与运行时

应用有两种交付形态：FastAPI Cloud 与自托管 Docker Compose。镜像内先构建前端，再由 FastAPI 同域托管；数据库迁移在启动前由 `prestart.sh` 执行。本页是知识导航，实际执行指南见 [测试环境部署](../devops/test-env-deploy.md)。

## 1. 构建产物

| 产物 | 构建方式 | 位置 | 证据 |
|---|---|---|---|
| 前端静态包 | `bun run build` | `backend/app/frontend` | `frontend/vite.config.ts:9-12` |
| 后端镜像 | `backend/Dockerfile` | 本地镜像 | `backend/Dockerfile:19-65` |
| Python 依赖 | `uv sync --frozen` | 镜像内 `.venv` | `backend/Dockerfile:43-61` |

## 2. 运行拓扑

| 服务 | 镜像 | 端口 | 依赖 | 健康检查 |
|---|---|---|---|---|
| proxy | `traefik:v3.7` | 80/443 | Docker socket | 无 |
| db | `postgres:18` | 5432 | 无 | `pg_isready` (`compose.yml:22-27`) |
| backend | `backend:latest` | 8000 | db 健康 | `/api/v1/utils/health-check/` (`compose.yml:67-71`) |
| adminer | `adminer` | 8080 | db | 无 |
| mailpit | `axllent/mailpit` | 8025/1025 | 无 | 无 |
| playwright | `frontend/Dockerfile.playwright` | 无 | backend、mailpit | 无 |

## 3. 部署命令与凭证

`deployment-docker-compose.md` 给出的顺序是：`docker compose -f compose.yml -f compose.deploy.yml build`、`run --rm backend bash scripts/prestart.sh`、`up -d`。凭证通过环境变量或 GitHub secrets 注入，不写入仓库；`SECRET_KEY`、`FIRST_SUPERUSER_PASSWORD`、`POSTGRES_PASSWORD`、`SMTP_PASSWORD` 均为敏感项。

## 4. 生效检查与回滚

- 生效检查：`curl http://localhost:8000/api/v1/utils/health-check/` 返回 `true`；前端 `curl http://localhost:8000` 返回 HTML。
- 回滚：仓库没有文档化的镜像回滚、数据库备份恢复或 `alembic downgrade` 流程，只有迁移文件内的 `downgrade()`。这是已确认缺口，Deploy 配置保持 pending，见 [测试环境部署](../devops/test-env-deploy.md)。
- 清理：`docker compose down -v --remove-orphans` 会删除卷与测试数据，仅用于本地/测试环境。

补充源码锚点：`deployment.md:1`、`.github/workflows/deploy-docker-compose.yml:1`。

## 5. 共变耦合与修改清单

1. 改镜像：同步 `backend/Dockerfile`、`compose.yml` 与 CI 构建。
2. 改迁移：同步 `backend/scripts/prestart.sh`、Alembic 与回滚指南。
3. 改域名/证书：同步 `compose.deploy.yml` 与 `.env` 的 `DOMAIN`。
