---
kind: glossary
scope: terminology
status: draft
origin: generated
source_paths: [backend/app/models.py, backend/app/core/config.py, backend/app/api/deps.py, frontend/src/hooks/useAuth.ts]
symbols: [User, Item, CurrentUser, isLoggedIn, emails_enabled]
upstream: [INDEX.md]
downstream: [business/domain-models/index.md, contracts/configuration.md, overview/business-architecture.md]
---
# 领域术语与代码符号映射

自然语言需求里的“用户”“条目”“登录态”“超级管理员”在本仓库都有唯一代码符号。先把术语对齐，再读业务流程，可以避免把前端展示名当成后端字段名。

## 1. 核心术语表

| 业务术语 | 代码符号 | 类型 | 定义与边界 |
|---|---|---|---|
| 用户 | `User` (`backend/app/models.py:51-57`) | SQLModel 表 | 以 UUID 为主键，邮箱唯一，含 `is_active` 与 `is_superuser` |
| 条目 | `Item` (`backend/app/models.py:87-95`) | SQLModel 表 | 必属某个 `User`，删除用户时级联删除 |
| 当前用户 | `CurrentUser` (`backend/app/api/deps.py:49`) | 依赖别名 | 由 Bearer Token 解析并校验激活状态 |
| 超级用户 | `is_superuser` (`backend/app/models.py:16`) | 布尔字段 | 拥有用户管理与全量条目读取能力 |
| 登录态 | `access_token` (`frontend/src/hooks/useAuth.ts:15`) | localStorage 键 | 仅表示存在 Token，不校验过期 |
| 邮件开关 | `emails_enabled` (`backend/app/core/config.py:59-62`) | 计算属性 | `SMTP_HOST` 与 `EMAILS_FROM_EMAIL` 同时存在才为真 |

## 2. 输入模型与输出模型

| 场景 | 输入符号 | 输出符号 | 差异 |
|---|---|---|---|
| 管理员建号 | `UserCreate` (`backend/app/models.py:21-23`) | `UserPublic` (`backend/app/models.py:59-62`) | 输入含密码，输出永不含哈希 |
| 自助注册 | `UserRegister` (`backend/app/models.py:25-29`) | `UserPublic` | 注册不接受 `is_superuser` |
| 更新用户 | `UserUpdate` (`backend/app/models.py:32-38`) | `UserPublic` | 全部字段可选，密码单独哈希 |
| 更新本人 | `UserUpdateMe` (`backend/app/models.py:40-43`) | `UserPublic` | 只允许姓名与邮箱 |
| 条目创建 | `ItemCreate` (`backend/app/models.py:76-77`) | `ItemPublic` (`backend/app/models.py:97-101`) | `owner_id` 由服务端写入 |

## 3. 状态与角色

| 状态 | 取值来源 | 影响 |
|---|---|---|
| 用户激活 | `User.is_active` (`backend/app/models.py:15`) | 未激活登录返回 400，Token 校验返回 400 |
| 超级用户 | `User.is_superuser` (`backend/app/models.py:16`) | 决定用户管理与跨用户条目读取 |
| 开发模式 | `FASTAPI_ENV` (`backend/app/core/config.py:27`) | 决定是否挂载 `/private`、是否只告警默认密钥 |
| 邮件可用 | `emails_enabled` (`backend/app/core/config.py:59-62`) | 决定建号后是否尝试发信 |

## 4. 命名陷阱

- `username` 在登录表单里实际承载邮箱；`backend/app/api/routes/login.py:24-30` 直接把 `form_data.username` 传给 `crud.authenticate(email=...)`。
- `password` 只存在于输入模型；数据库字段名是 `hashed_password` (`backend/app/models.py:53`)。
- 前端 `isLoggedIn` 只检查 localStorage 是否有值，不能代表 Token 有效；真正的校验发生在 `backend/app/api/deps.py:30-46`。

## 5. 共变耦合与修改清单

1. 重命名字段：同步 `backend/app/models.py`、`backend/app/crud.py`、Alembic 迁移与 [接口全集](../contracts/api-reference.md)。
2. 改角色语义：同步 `backend/app/api/deps.py`、[业务架构](business-architecture.md) 与前端 `frontend/src/routes/_layout/admin.tsx`。
3. 改配置语义：同步 `backend/app/core/config.py` 与 [配置手册](../contracts/configuration.md)。
