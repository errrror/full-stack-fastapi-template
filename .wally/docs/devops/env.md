# 环境搭建与启动

> 目标：在本地启动 PostgreSQL、Mailpit、FastAPI 与 Vite，或直接用 Docker Compose 启动完整栈。配置项与源码事实见 [配置手册](../contracts/configuration.md)，部署流程见 [测试环境部署](test-env-deploy.md)。

> Source: `development.md`、`backend/README.md`、`frontend/README.md`、`compose.yml`、`backend/pyproject.toml`
> Last-verified: 2026-11-19（静态核对，未执行启动）

---

## 一、运行环境

| 环境 | 运行时 | 依赖管理 | 用途 |
|---|---|---|---|
| 本地后端 | Python 3.14 | uv（`uv.lock`） | `uv run fastapi dev` |
| 本地前端 | Bun 1.x | `bun.lock` | Vite 开发服务器 5173 |
| 容器 | Docker Compose | 镜像 `python:3.14`、`oven/bun:1` | 完整栈与 Playwright |
| 数据库 | PostgreSQL 18 | Compose 服务 `db` | 业务数据 |
| 邮件 | Mailpit | Compose 服务 `mailpit` | 捕获本地邮件 |

`backend/pyproject.toml:5` 要求 Python `>=3.14,<4.0`，低于该版本无法安装后端依赖。

## 二、快速启动

### 本地后端与前端

```bash
# 1) 启动数据库与邮件捕获
docker compose up -d db mailpit

# 2) 安装后端依赖并迁移
cd backend
uv sync
uv run bash scripts/prestart.sh
uv run fastapi dev

# 3) 另开终端，安装并启动前端
cd ..
bun install
bun run dev
```

访问地址：前端 `http://localhost:5173`，API `http://localhost:8000`，Swagger `http://localhost:8000/docs`，Mailpit `http://localhost:8025`。

### 完整 Docker Compose

```bash
docker compose run --rm backend bash scripts/prestart.sh
docker compose watch
```

应用在 `http://localhost:8000`，Adminer 在 `http://localhost:8080`，Traefik 面板在 `http://localhost:8090`。启动 Compose 前先停止本地 8000 端口的 FastAPI，避免端口冲突。

## 三、配置体系

| 文件 | 作用 | 注意 |
|---|---|---|
| `.env` | 本地开发默认值 | 提交的是占位值，非 development 环境会拒绝默认密钥 |
| `frontend/.env` | `VITE_API_URL` 与 `MAILPIT_HOST` | 只暴露 `VITE_` 前缀 |
| `compose.yml` | 服务拓扑与环境注入 | 需要 `POSTGRES_PASSWORD` 等变量 |
| `compose.override.yml` | 本地端口、源码同步、Playwright | 由 Compose 自动叠加 |
| `compose.deploy.yml` | HTTPS、域名、证书 | 需要 `DOMAIN` |

完整变量表见 [配置手册](../contracts/configuration.md)。

## 四、常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| `uv sync` 报 Python 版本不满足 | 本机不是 3.14 | 安装 3.14 或用 Compose |
| 后端启动即报默认密钥 | `SECRET_KEY` 仍是占位值 | 改成随机值；开发可设 `FASTAPI_ENV=development` |
| 前端 401/403 循环跳登录 | Token 失效或 `SECRET_KEY` 变化 | 重新登录；固定密钥 |
| 邮件收不到 | `SMTP_HOST` 未指向 Mailpit | 本地用 `localhost:1025`，Compose 用 `mailpit` |
| 8000 端口被占用 | 本地与 Compose 同时启动 | 停止其中一个 |
