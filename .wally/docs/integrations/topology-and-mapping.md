---
kind: integrations-index
scope: field-mapping
status: draft
origin: generated
source_paths: [backend/app/api/routes/login.py, backend/app/api/routes/users.py, backend/app/api/routes/utils.py, backend/app/utils.py, backend/app/models.py]
symbols: [recover_password, create_user, test_email, send_email, UserCreate]
upstream: [integrations/index.md]
downstream: [integrations/downstream/smtp.md, integrations/downstream/postgresql.md, contracts/api-reference.md]
---
# 参数组装与字段映射

本页追踪一个请求字段如何从 HTTP 入参变成下游调用参数。重点在“三明治夹心层”：路由完成校验后，业务函数重新组装邮件 context 或 ORM 字段，不能只看底层 `send_email` 或 `Session`。

## 1. 上游 DTO 到后端字段

| 上游字段 | 入参模型 | 中间变量 | 下游字段 | 转换规则 | 证据 |
|---|---|---|---|---|---|
| `email` | `UserCreate.email` | `user_in.email` | `User.email` | EmailStr 校验并唯一 | `backend/app/api/routes/users.py:57-79` |
| `password` | `UserCreate.password` | `user_in.password` | `User.hashed_password` | 8 至 128 字符，Argon2 哈希 | `backend/app/crud.py:10-17` |
| `title` | `ItemCreate.title` | `item_in.title` | `Item.title` | 1 至 255 字符 | `backend/app/models.py:70-74` |
| `email_to` | `EmailStr` | `email_to` | SMTP `to` | 直接透传 | `backend/app/api/routes/utils.py:11-27` |

## 2. 邮件请求字典

`backend/app/utils.py:34-57` 组装的发送参数如下，键名就是下游库实际读取的键：

| 字典 | 键 | 值来源 | 条件 |
|---|---|---|---|
| Message | `subject` | 各 `generate_*_email` 拼装 | 总是 |
| Message | `html` | `render_email_template` 输出 | 总是 |
| Message | `mail_from` | `(EMAILS_FROM_NAME, EMAILS_FROM_EMAIL)` | 总是 |
| send | `to` | 路由传入的 `email_to` | 总是 |
| smtp | `host` | `SMTP_HOST` | 总是 |
| smtp | `port` | `SMTP_PORT` | 总是 |
| smtp | `tls` | `SMTP_TLS` | 为真时 |
| smtp | `ssl` | `SMTP_SSL` | TLS 为假且 SSL 为真时 |
| smtp | `user` | `SMTP_USER` | 非空时 |
| smtp | `password` | `SMTP_PASSWORD` | 非空时 |

## 3. 数据库字段映射

`backend/app/models.py:51-57` 的 `User` 表把 `email/full_name/is_active/is_superuser/hashed_password/created_at` 映射为列；`backend/app/models.py:87-95` 的 `Item` 表把 `title/description/owner_id/created_at` 映射为列。`owner_id` 不是客户端字段，而是 `backend/app/api/routes/items.py:61-73` 从 `CurrentUser` 注入。

## 4. 失败翻译

| 上游结果 | 触发 | 下游影响 | 用户可见 |
|---|---|---|---|
| 建号成功但邮件失败 | `send_email` 抛错 | 用户已提交，邮件未发 | 请求返回 500，需重试发信 |
| 邮件开关关闭 | `emails_enabled=false` | 不调用 SMTP | 建号成功，无邮件 |
| 数据库不可用 | `Session` 创建或查询失败 | 请求失败 | 500，无业务写入 |

补充源码锚点：`backend/app/api/routes/login.py:23`。

## 5. 共变耦合与修改清单

1. 新增邮件变量：同步 `backend/app/utils.py:60-102`、`packages/react-email/emails/*.tsx` 与导出 HTML。
2. 新增下游字段：同步本页映射表、[下游契约](downstream/smtp.md) 与 [配置手册](../contracts/configuration.md)。
3. 改错误翻译：同步 [错误码字典](../contracts/error-codes.md)。
