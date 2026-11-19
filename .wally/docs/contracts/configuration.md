---
kind: api-contract
scope: configuration
status: draft
origin: generated
source_paths: [backend/app/core/config.py, .env, compose.yml, frontend/.env, backend/Dockerfile]
symbols: [Settings, DATABASE_URL, SECRET_KEY, VITE_API_URL, CMD]
upstream: [INDEX.md]
downstream: [operations/deployment-and-runtime.md, integrations/downstream/smtp.md, integrations/downstream/postgresql.md]
---
# 配置与环境变量手册

后端配置由 `pydantic-settings` 的 `Settings` 统一读取，默认从仓库根 `.env` 加载；前端只暴露 `VITE_` 前缀变量；Compose 负责把宿主环境注入容器。默认占位密钥在非 development 环境会直接报错。

## 1. 后端配置总表

| 变量 | 类型 | 默认 | 必填 | 作用 |
|---|---|---|---|---|
| `API_V1_STR` | str | `/api/v1` | 否 | 路由前缀 |
| `SECRET_KEY` | str | 无 | 是 | JWT 与重置令牌签名 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | 11520 | 否 | 访问令牌 8 天 |
| `FRONTEND_HOST` | str | `http://localhost:5173` | 否 | CORS 允许源与邮件链接 |
| `FASTAPI_ENV` | 字面量 | 空 | 否 | `development` 时挂载 private、放宽密钥校验 |
| `PROJECT_NAME` | str | 无 | 是 | OpenAPI 标题与邮件主题 |
| `SENTRY_DSN` | HttpUrl | 空 | 否 | Sentry 上报 |
| `DATABASE_URL` | PostgresDsn | 无 | 是 | PostgreSQL 连接 |
| `SMTP_TLS` | bool | true | 否 | SMTP TLS |
| `SMTP_SSL` | bool | false | 否 | SMTP SSL |
| `SMTP_PORT` | int | 587 | 否 | SMTP 端口 |
| `SMTP_HOST` | str | 空 | 否 | SMTP 主机 |
| `SMTP_USER` | str | 空 | 否 | SMTP 用户 |
| `SMTP_PASSWORD` | str | 空 | 否 | SMTP 密码 |
| `EMAILS_FROM_EMAIL` | EmailStr | 空 | 否 | 发件地址 |
| `EMAILS_FROM_NAME` | str | 空 | 否 | 发件显示名，空则用项目名 |
| `EMAIL_RESET_TOKEN_EXPIRE_HOURS` | int | 48 | 否 | 重置令牌有效期 |
| `EMAIL_TEST_USER` | EmailStr | `test@example.com` | 否 | 测试用户 |
| `FIRST_SUPERUSER` | EmailStr | 无 | 是 | 初始超级用户 |
| `FIRST_SUPERUSER_PASSWORD` | str | 无 | 是 | 初始超级用户密码 |

## 2. Compose 与部署变量

| 变量 | 使用处 | 说明 |
|---|---|---|
| `POSTGRES_PASSWORD` | `compose.yml:31` | 数据库密码，必填 |
| `DOMAIN` | `compose.yml:44` | Traefik 域名，默认 localhost |
| `ADMINER_DESIGN` | `compose.yml:39` | Adminer 主题 |
| `PROJECT_NAME` | `compose.yml:56` | 注入后端 |
| `SECRET_KEY` | `compose.yml:57` | 注入后端 |
| `FIRST_SUPERUSER`、`FIRST_SUPERUSER_PASSWORD` | `compose.yml:58-59` | 注入后端 |
| `SMTP_HOST`、`SMTP_USER`、`SMTP_PASSWORD`、`EMAILS_FROM_EMAIL` | `compose.yml:60-63` | 邮件配置 |
| `SENTRY_DSN` | `compose.yml:65` | 可选观测 |
| `SMOKESHOW_AUTH_KEY` | `.github/workflows/smokeshow.yml` | 覆盖率托管，仓库 secret |
| `FASTAPI_CLOUD_TOKEN`、`FASTAPI_CLOUD_APP_ID` | `.github/workflows/deploy.yml` | 云部署 secret |
| `NODE_ENV` | `frontend/Dockerfile.playwright` | Playwright 镜像构建参数 |

## 3. 前端变量

| 变量 | 默认 | 作用 | 证据 |
|---|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | API baseURL | `frontend/.env:1`、`frontend/src/main.tsx:18` |
| `MAILPIT_HOST` | `http://localhost:8025` | E2E 邮件检查 | `frontend/.env:2` |
| `PLAYWRIGHT_BASE_URL` | `http://localhost:5173` | E2E 目标 | `frontend/playwright.config.ts:5` |
| `CI` | 空 | 控制重试、reporter、workers | `frontend/playwright.config.ts:21-29` |

## 4. 校验与优先级

- 加载顺序：进程环境变量覆盖 `.env`，`.env` 覆盖字段默认值；`SettingsConfigDict(env_file="../.env", extra="ignore")` 见 `backend/app/core/config.py:15-20`。
- `DATABASE_URL` 会把 `postgres://` 或 `postgresql://` 改写为 `postgresql+psycopg://`，见 `backend/app/core/config.py:34-40`。
- 非 development 环境若 `SECRET_KEY`、数据库密码或 `FIRST_SUPERUSER_PASSWORD` 仍是默认占位值，启动直接抛错，见 `backend/app/core/config.py:67-89`。
- `EMAILS_FROM_NAME` 为空时自动回退到 `PROJECT_NAME`，见 `backend/app/core/config.py:51-55`。

补充源码锚点：`backend/Dockerfile:1`。

相关页面：[业务总表](../business/index.md)、[排障 Runbook](../operations/runbook-and-observability.md)。

## 5. 共变耦合与修改清单

1. 新增配置：同步 `backend/app/core/config.py`、`.env`、`compose.yml` 与本页。
2. 改端口或域名：同步 `compose.yml`、`frontend/.env` 与 [部署与运行时](../operations/deployment-and-runtime.md)。
3. 改密钥校验：同步 `backend/app/core/config.py:67-89` 与部署文档。
