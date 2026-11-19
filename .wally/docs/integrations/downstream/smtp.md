---
kind: downstream-contract
scope: smtp
status: draft
origin: generated
source_paths: [backend/app/utils.py, backend/app/core/config.py, backend/app/api/routes/users.py, backend/app/api/routes/login.py, backend/app/api/routes/utils.py]
symbols: [send_email, emails_enabled, create_user, recover_password, test_email]
upstream: [integrations/index.md]
downstream: [architecture/email-templates.md, business/password-recovery.md, contracts/configuration.md]
---
# SMTP 下游契约

邮件发送封装在 `backend/app/utils.py:34-57`，使用 `emails` 库的 `Message.send`。是否启用由 `emails_enabled` 决定；未配置 SMTP 时建号仍成功，但不会发信。

## 1. 调用方

| 调用方 | 触发 | 邮件 | 证据 |
|---|---|---|---|
| 管理员建号 | `POST /api/v1/users/` | 新账号凭据 | `backend/app/api/routes/users.py:54-79` |
| 密码找回 | `POST /api/v1/password-recovery/{email}` | 重置链接 | `backend/app/api/routes/login.py:53-75` |
| 测试邮件 | `POST /api/v1/utils/test-email/` | 测试模板 | `backend/app/api/routes/utils.py:11-27` |

## 2. SMTP 请求字典

| 键 | 来源 | 默认 | 说明 |
|---|---|---|---|
| `host` | `SMTP_HOST` | 无 | 为空则 `emails_enabled=false` |
| `port` | `SMTP_PORT` | 587 | 开发 Compose 用 1025 |
| `tls` | `SMTP_TLS` | true | 为真时写入 |
| `ssl` | `SMTP_SSL` | false | TLS 为假时才写入 |
| `user` | `SMTP_USER` | 无 | 非空才写入 |
| `password` | `SMTP_PASSWORD` | 无 | 非空才写入 |

## 3. 消息字段与返回

| 字段 | 来源 | 说明 |
|---|---|---|
| `subject` | `generate_*_email` | 包含项目名与收件人 |
| `html` | Jinja 渲染后的模板 | 来自 `backend/app/email-templates` |
| `mail_from` | `EMAILS_FROM_NAME` 与 `EMAILS_FROM_EMAIL` | 发件人显示名与地址 |
| `to` | 路由传入 | 单个收件人 |
| 返回 | `message.send` 响应 | 仅记录到日志，不参与业务事务 |

## 4. 失败语义

| 场景 | 行为 | 用户影响 |
|---|---|---|
| SMTP 未配置 | `assert emails_enabled` 失败 | 建号成功但 500；应先检查配置 |
| SMTP 拒绝 | `message.send` 抛错 | 请求 500；数据库写入已提交 |
| 模板缺失 | `render_email_template` 读文件失败 | 请求 500；需重新导出模板 |
| 收件人无效 | `EmailStr` 在入口校验 | 422，不进入发送 |

补充源码锚点：`backend/app/core/config.py:14`。

## 5. 共变耦合与修改清单

1. 改 SMTP 参数：同步 `backend/app/utils.py:47-55` 与 [配置手册](../../contracts/configuration.md)。
2. 改邮件模板：同步 `packages/react-email/` 与 [邮件模板组件](../../architecture/email-templates.md)。
3. 改失败策略：明确是否要事务回滚或异步重试，并补测试。
