---
kind: component
scope: email-package
status: draft
origin: generated
source_paths: [packages/react-email/emails/new_account.tsx, packages/react-email/emails/reset_password.tsx, packages/react-email/emails/test_email.tsx, packages/react-email/ui/Layout.tsx, backend/app/utils.py]
symbols: [NewAccount, ResetPassword, TestEmail, Layout, generate_new_account_email]
upstream: [integrations/downstream/smtp.md]
downstream: [architecture/index.md, business/password-recovery.md, integrations/topology-and-mapping.md]
---
# emails（React Email 模板包）

`packages/react-email` 是构建期库，不参与运行时。它把 React 组件渲染为 HTML，导出到 `backend/app/email-templates`，后端再用 Jinja2 把这些 HTML 当模板渲染变量并发送。

## 1. 包结构与模板

| 模板 | 组件 | 变量 | 用途 |
|---|---|---|---|
| 新账号 | `NewAccount` (`packages/react-email/emails/new_account.tsx:15`) | `project_name/username/password/link` | 管理员建号后发送凭据 |
| 重置密码 | `ResetPassword` (`packages/react-email/emails/reset_password.tsx:14`) | `project_name/username/email/link/valid_hours` | 密码找回 |
| 测试邮件 | `TestEmail` (`packages/react-email/emails/test_email.tsx:11`) | `project_name/email` | 超级用户测试 SMTP |

共享组件位于 `packages/react-email/ui/`：`Layout` (`packages/react-email/ui/Layout.tsx:14`)、`Heading`、`Button`、`Link`、`Callout`。它们只负责邮件排版，不访问网络。

## 2. 占位符契约

模板 props 的默认值是 Jinja 占位符，例如 `packages/react-email/emails/new_account.tsx:8-13` 声明 `password = "{{ password }}"`。后端 `backend/app/utils.py:87-102` 的 `generate_new_account_email` 负责构造同名 context；新增占位符必须同时改组件 props 与后端 context，否则运行时会渲染为空。

## 3. 生成与导出链

```text
packages/react-email/emails/*.tsx
  → bun run email:export
  → email export --outDir ../../backend/app/email-templates (packages/react-email/package.json:9)
  → backend/app/email-templates/*.html
  → backend/app/utils.py:25 render_email_template()
  → backend/app/utils.py:34 send_email()
```

导出的 HTML 是提交物，不应手工编辑；修改模板后必须重新导出并检查 diff。

## 4. 与后端的耦合边界

邮件包不知道收件人、SMTP 或重试策略；这些都在后端。反过来，后端只按文件名读取 HTML，不导入 React 组件。安全上要注意 `new_account.tsx` 当前把明文密码放进邮件正文，这是已确认的高风险设计，见 [高危雷区](../operations/pitfalls-and-adr.md)。

## 5. 共变耦合与修改清单

1. 改模板变量：同步 `.tsx` props、`backend/app/utils.py` 的 context 与导出 HTML。
2. 改邮件样式：只改 `packages/react-email/ui/`，重新导出并检查三类邮件。
3. 改 SMTP 发送：与模板解耦，转到 [SMTP 契约](../integrations/downstream/smtp.md)。
