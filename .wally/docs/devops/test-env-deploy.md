# 测试环境部署

> 本页是 Deploy 阶段的权威执行指南。仓库没有独立的“测试环境”目录或远程测试集群，实际可复现路径是 Docker Compose 自托管栈；FastAPI Cloud 是另一条云部署路径。以下命令来自仓库文件，初始化阶段只做静态核对，未执行部署。

> Source: `deployment-docker-compose.md`、`deployment.md`、`compose.yml`、`compose.deploy.yml`、`backend/Dockerfile`、`.github/workflows/deploy-docker-compose.yml`
> Last-verified: 2026-11-19（静态核对，未执行）

---

## 一、环境与执行

| 项 | 实际内容 | 来源 |
|---|---|---|
| 环境类型 | 单机 Docker Compose，自托管；或 FastAPI Cloud | `deployment-docker-compose.md`、`deployment.md` |
| 资源归属 | 目标服务器由部署方提供，仓库不声明地址 | `deployment-docker-compose.md` |
| 执行目录 | 仓库根 | `deployment-docker-compose.md` |
| 部署授权 | 需用户显式授权；初始化不执行 | SOP 边界 |
| 依赖 | Docker Engine、Compose、可解析的 `DOMAIN` | `deployment-docker-compose.md` |

## 二、部署命令

```bash
# 1) 构建前端与后端镜像
docker compose -f compose.yml -f compose.deploy.yml build

# 2) 迁移数据库并创建初始超级用户
docker compose -f compose.yml -f compose.deploy.yml run --rm backend bash scripts/prestart.sh

# 3) 启动完整栈
docker compose -f compose.yml -f compose.deploy.yml up -d
```

第 2 步执行 `alembic upgrade head` 与 `python app/initial_data.py`，见 `backend/scripts/prestart.sh:7-10`。镜像构建先跑 Bun 前端构建，再复制到 Python 3.14 运行时，见 `backend/Dockerfile:1-65`。

## 三、配置与凭证

| 变量 | 用途 | 获取方式 |
|---|---|---|
| `DOMAIN` | Traefik 域名与 HTTPS 证书 | 部署方提供 |
| `POSTGRES_PASSWORD` | 数据库密码 | 部署方生成，不写入仓库 |
| `SECRET_KEY` | JWT 与重置令牌签名 | 部署方生成 |
| `FIRST_SUPERUSER`、`FIRST_SUPERUSER_PASSWORD` | 初始管理员 | 部署方提供 |
| `SMTP_HOST`、`SMTP_USER`、`SMTP_PASSWORD`、`EMAILS_FROM_EMAIL` | 邮件 | 邮件服务商 |
| `SENTRY_DSN` | 可选错误上报 | Sentry 项目 |

`deployment-docker-compose.md` 给出用 `python -c "import secrets; print(secrets.token_urlsafe(32))"` 生成密钥的方式。本页不记录任何真实值。FastAPI Cloud 路径把 `FASTAPI_CLOUD_TOKEN`、`FASTAPI_CLOUD_APP_ID`、`DATABASE_URL` 等放在 GitHub secrets。

## 四、生效检查

```bash
curl -fsS http://localhost:8000/api/v1/utils/health-check/
curl -fsS http://localhost:8000/ >/dev/null
```

第一条期望返回 `true`，第二条期望返回前端 HTML。Compose 的 backend 健康检查同样请求 `/api/v1/utils/health-check/`，见 `compose.yml:67-71`。健康检查只证明进程可响应，不证明数据库迁移、邮件或前端资源都正确。

## 五、回滚与清理

- 回滚：仓库没有镜像版本标签、数据库备份恢复或 `alembic downgrade` 执行流程。迁移文件含 `downgrade()`，但没有触发条件、备份步骤与验收标准，因此 Deploy 配置标为 `pending`，缺口见 `.wally/config.json`。
- 清理：`docker compose down -v --remove-orphans` 会删除数据库卷与测试数据；只应在本地或一次性测试环境执行。
- 基线保留：缺陷修复前应先保留当前镜像、数据库快照与版本 SHA；仓库当前未提供自动化基线脚本。

## 六、项目自定义

FastAPI Cloud 部署由 `.github/workflows/deploy.yml` 在 `master` 推送时执行，先构建前端、运行 `prestart.sh`，再 `fastapi deploy`。Docker Compose 的 GitHub Actions 版本是 `.github/workflows/deploy-docker-compose.yml`，使用 self-hosted runner，需单独配置变量与 secrets。两条路径都不由初始化执行。
