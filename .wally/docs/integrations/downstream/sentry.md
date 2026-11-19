---
kind: downstream-contract
scope: sentry
status: draft
origin: generated
source_paths: [backend/app/main.py, backend/app/core/config.py, backend/pyproject.toml]
symbols: [sentry_sdk.init, SENTRY_DSN, FASTAPI_ENV]
upstream: [integrations/index.md]
downstream: [operations/runbook-and-observability.md, contracts/configuration.md, operations/boundary.md]
---
# Sentry 下游契约

Sentry 是可选错误观测下游，只在配置了 `SENTRY_DSN` 且 `FASTAPI_ENV` 不是 `development` 时初始化。它不参与业务事务，初始化失败或未配置都不应阻断 API。

## 1. 初始化条件

```text
backend/app/main.py:18 [settings.SENTRY_DSN and settings.FASTAPI_ENV != "development"]
  → backend/app/main.py:19 sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)
```

`SENTRY_DSN` 的类型是 `HttpUrl | None`（`backend/app/core/config.py:30`），默认空。开发环境即使配置了 DSN 也不初始化，避免本地噪声。

## 2. 配置键

| 键 | 类型 | 默认 | 作用 |
|---|---|---|---|
| `SENTRY_DSN` | HttpUrl | 空 | 上报地址 |
| `enable_tracing` | bool | true | 启用性能追踪 |
| `FASTAPI_ENV` | 字面量 | 空 | 为 `development` 时跳过初始化 |

## 3. 事件边界

Sentry 只接收后端进程内的异常与追踪，不接收前端错误；前端没有 Sentry SDK。邮件内容、Token 和请求体是否上报取决于 Sentry 默认序列化，当前没有显式脱敏配置，属于隐私风险，见 [高危雷区](../../operations/pitfalls-and-adr.md)。

## 4. 失败与降级

| 场景 | 行为 | 影响 |
|---|---|---|
| 未配置 DSN | 跳过初始化 | 无 |
| DSN 非法 | Pydantic 启动校验失败 | 应用无法启动 |
| 网络不可达 | SDK 内部缓冲/丢弃 | 请求不受影响 |
| 开发环境 | 跳过 | 本地无上报 |

补充源码锚点：`backend/pyproject.toml:18`。

## 5. 共变耦合与修改清单

1. 改初始化条件：同步 `backend/app/main.py:18-19` 与 [配置手册](../../contracts/configuration.md)。
2. 加脱敏：在 `sentry_sdk.init` 增加 `before_send`，并补隐私说明。
3. 加前端上报：新建前端观测页并更新 [排障 Runbook](../../operations/runbook-and-observability.md)。
