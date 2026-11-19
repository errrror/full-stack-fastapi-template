---
kind: operations
scope: runbook
status: draft
origin: generated
source_paths: [backend/app/api/routes/utils.py, backend/app/main.py, backend/app/utils.py, compose.yml, backend/app/core/config.py]
symbols: [health_check, sentry_sdk.init, send_email, logger, SENTRY_DSN]
upstream: [INDEX.md]
downstream: [operations/pitfalls-and-adr.md, integrations/downstream/sentry.md, contracts/error-codes.md]
---
# 排障 Runbook 与可观测性

当前可观测性很薄：一个布尔健康检查、可选的 Sentry、以及少量 `logging.info`。没有指标、告警规则或请求 ID。本页给出在现有信号下的确定性定位顺序，并标出缺口。

## 1. 现有信号

| 信号 | 位置 | 能回答什么 | 局限 |
|---|---|---|---|
| 健康检查 | `backend/app/api/routes/utils.py:29-31` | 进程能否响应 | 不检查数据库或 SMTP |
| Compose 健康检查 | `compose.yml:67-71` | 容器是否就绪 | 只请求健康端点 |
| Sentry | `backend/app/main.py:18-19` | 未捕获异常 | 开发环境不启用 |
| 邮件日志 | `backend/app/utils.py:57` | 发送结果 | 无请求 ID，可能含收件信息 |

## 2. 故障定位决策树

```text
现象：请求 500
  ├─ 启动阶段？ → 检查 SECRET_KEY/DATABASE_URL 校验 (backend/app/core/config.py:67-89)
  ├─ 登录 500？ → 检查 deps.py:36 语法错误与 JWT 解码
  ├─ 条目 500？ → 检查 DATABASE_URL、迁移是否执行 (backend/scripts/prestart.sh:7)
  ├─ 邮件 500？ → 检查 emails_enabled 与 SMTP 配置 (backend/app/utils.py:40-55)
  └─ 其他 → 查 Sentry（若启用）或容器日志
```

## 3. 常见故障与处理

| 故障 | 首查 | 处理 | 验收 |
|---|---|---|---|
| 后端容器反复重启 | `docker compose logs backend` | 修配置或代码，重建镜像 | 健康检查返回 true |
| 数据库连接失败 | `DATABASE_URL` 与 db 健康 | 修正连接串，等待 db healthy | `pg_isready` 成功 |
| 邮件未送达 | `SMTP_HOST`、Mailpit 8025 | 修正 SMTP 配置，重发测试邮件 | 测试邮件出现在 Mailpit |
| 前端 404 | `backend/app/frontend` 是否存在 | 重新构建前端 | 根路径返回 HTML |
| Token 总是失效 | `SECRET_KEY` 是否变化 | 固定密钥并重新登录 | 新 Token 可用 |

## 4. 性能与缺口

没有 profiling、指标或慢查询日志。数据库查询为简单主键/邮箱/所有者过滤，当前风险低；邮件发送是同步阻塞，量大时会占用请求线程。若引入重负载，优先增加指标与异步发送，而不是先调 worker 数。

## 5. 共变耦合与修改清单

1. 加日志：同步 `backend/app/utils.py`、[配置手册](../contracts/configuration.md) 与本页信号表。
2. 加指标：新增观测页并更新 [部署与运行时](deployment-and-runtime.md)。
3. 加告警：写明阈值与责任人，不能只装库。
