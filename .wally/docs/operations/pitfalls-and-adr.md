---
kind: operations
scope: pitfalls
status: draft
origin: generated
source_paths: [backend/app/api/deps.py, backend/app/core/db.py, backend/app/main.py, backend/app/core/config.py, backend/app/utils.py, frontend/src/hooks/useAuth.ts]
symbols: [get_current_user, engine, sentry_sdk.init, Settings, send_email]
upstream: [INDEX.md]
downstream: [operations/runbook-and-observability.md, business/auth-and-users.md, architecture/email-templates.md]
---
# 高危雷区与设计取舍

本页记录已确认的缺陷、容易误改的设计和未挂载代码。它不是推测清单，每条都有源码位置。

## 1. 已确认的 P0 缺陷

`backend/app/api/deps.py:36` 写作 `except InvalidTokenError, ValidationError:`。这不是合法 Python 3 语法，`compile()` 会报 `multiple exception types must be parenthesized`。由于 `app.main` 导入 `api_router`，该行会让整个后端无法导入，所有路由与测试都不可用。正确写法是 `except (InvalidTokenError, ValidationError):`。修复后必须补一个导入冒烟测试，防止再次合入。

## 2. 高风险设计

| 风险 | 位置 | 影响 | 建议 |
|---|---|---|---|
| 新账号邮件含明文密码 | `backend/app/utils.py:87-102` 与 `packages/react-email/emails/new_account.tsx:8-35` | 凭据可被邮件系统留存 | 改为一次性邀请/重置链接 |
| Token 存 localStorage | `frontend/src/hooks/useAuth.ts:45` | XSS 可窃取会话 | 评估 httpOnly Cookie 与 CSP |
| Sentry 无显式脱敏 | `backend/app/main.py:18-19` | 可能上报请求体 | 增加 `before_send` 过滤 |
| 超级用户可改他人密码 | `backend/app/api/routes/users.py:182-212` | 管理面权限过大 | 审计与二次确认 |

## 3. 容易误改的取舍

- `backend/app/core/db.py:16-22` 的 `create_all` 被注释，表结构只由 Alembic 管理；取消注释会绕过迁移版本。
- `backend/app/main.py:18` 在 development 环境跳过 Sentry，这是有意为之，不是配置失效。
- `backend/app/api/main.py:13-14` 的 private 路由只在 development 挂载，生产不可用是预期行为。
- 前端 `isLoggedIn` 只检查 localStorage 是否存在，不能作为安全边界。

## 4. 未挂载与历史代码

未发现整段未挂载的业务函数。`backend/app/api/routes/private.py` 是条件挂载而非死代码；`frontend/playwright.config.ts` 中被注释的 firefox/webkit/mobile 项目是模板选项，不是运行路径。

补充源码锚点：`backend/app/core/config.py:14`。

## 5. 共变耦合与修改清单

1. 修 deps.py：同步 [认证流程](../business/auth-and-users.md)、[错误码](../contracts/error-codes.md) 与导入测试。
2. 改邮件凭据：同步 `backend/app/utils.py`、`packages/react-email` 与 [SMTP 契约](../integrations/downstream/smtp.md)。
3. 改 Token 存储：同步 `frontend/src/hooks/useAuth.ts`、`frontend/src/main.tsx` 与 E2E。
