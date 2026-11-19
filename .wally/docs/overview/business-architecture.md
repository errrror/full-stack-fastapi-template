---
kind: panorama
scope: business-architecture
status: draft
origin: generated
source_paths: [backend/app/models.py, backend/app/api/routes/users.py, backend/app/api/routes/items.py, backend/app/api/routes/login.py]
symbols: [User, Item, register_user, read_items, login_access_token]
upstream: [INDEX.md]
downstream: [business/index.md, business/domain-models/index.md, overview/glossary.md]
---
# 业务架构全景

系统只包含两个业务实体：`User` 与 `Item`。用户通过邮箱密码登录，获得 JWT；普通用户管理自己的条目，超级用户可管理全部用户与条目。密码找回走邮件令牌，注册与管理员建号共用同一套哈希与唯一性约束。

## 1. 触发角色与权限域

| 角色 | 识别方式 | 可见能力 | 源码锚点 |
|---|---|---|---|
| 匿名访客 | 无 Bearer Token | 登录、注册、密码找回、健康检查 | `backend/app/api/routes/login.py:23-98` |
| 普通用户 | JWT `sub` 对应用户且 `is_active` | 本人资料、本人条目 CRUD | `backend/app/api/deps.py:30-49` |
| 超级用户 | `is_superuser=true` | 用户列表、建号、改删任意用户、测试邮件 | `backend/app/api/deps.py:52-57` |
| 开发环境内部调用 | `FASTAPI_ENV=development` | `/private/users/` 直接建号 | `backend/app/api/main.py:13-14` |

## 2. 业务域与流程总表

| 流程 ID | 业务域 | 入口 | 结果 | 详细文档 |
|---|---|---|---|---|
| WF-AUTH | 登录与令牌 | `POST /api/v1/login/access-token` | 返回 Bearer Token | [认证与用户](../business/auth-and-users.md) |
| WF-USER | 用户生命周期 | `/api/v1/users` 与 `/signup` | 用户创建、更新、删除 | [认证与用户](../business/auth-and-users.md) |
| WF-ITEM | 条目管理 | `/api/v1/items` | 所有者隔离的 CRUD | [条目流程](../business/items.md) |
| WF-RESET | 密码找回 | `/api/v1/password-recovery` 与 `/reset-password` | 邮件令牌重置密码 | [密码找回](../business/password-recovery.md) |

## 3. 全局不变量

- 邮箱唯一：`backend/app/models.py:14` 对 `email` 设置 `unique=True`，路由在建号前再次查询并返回 400。
- 条目归属：`backend/app/models.py:87-95` 的 `owner_id` 为非空外键，删除用户时级联删除条目。
- 密码不明文存储：`backend/app/crud.py:10-17` 建号即哈希；`backend/app/models.py:21-23` 只在输入模型出现明文。
- 超级用户不可自删：`backend/app/api/routes/users.py:132-143` 与 `backend/app/api/routes/users.py:214-230` 均显式拒绝。

## 4. 角色与数据的交叉矩阵

| 操作 | 匿名 | 普通用户 | 超级用户 | 约束 |
|---|---|---|---|---|
| 注册 | 允许 | 允许 | 允许 | 邮箱已存在返回 400 |
| 查看本人资料 | 拒绝 | 允许 | 允许 | 需要有效 Token |
| 查看他人资料 | 拒绝 | 拒绝 | 允许 | 非超级用户返回 403 |
| 条目读取 | 拒绝 | 仅本人 | 全部 | `owner_id` 过滤 |
| 条目写入 | 拒绝 | 仅本人 | 任意 | 非本人返回 403 |

补充源码锚点：`backend/app/api/routes/items.py:13`。

## 5. 共变耦合与修改清单

1. 新增业务实体：同步 `backend/app/models.py`、Alembic 迁移、`backend/app/crud.py` 与 [接口全集](../contracts/api-reference.md)。
2. 调整角色：同步 `backend/app/api/deps.py:52-57`、前端路由守卫 `frontend/src/routes/_layout/admin.tsx:20-30` 与 [术语表](glossary.md)。
3. 调整级联删除：同步 `backend/app/models.py:51-57`、`backend/app/models.py:87-95` 与 `backend/app/api/routes/users.py:214-230`。
