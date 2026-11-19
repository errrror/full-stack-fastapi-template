---
kind: domain-model
scope: user
status: draft
origin: generated
source_paths: [backend/app/models.py, backend/app/crud.py, backend/app/api/routes/users.py]
symbols: [User, UserCreate, UserUpdate, UserPublic, create_user]
upstream: [business/domain-models/index.md]
downstream: [business/auth-and-users.md, integrations/downstream/postgresql.md, contracts/api-reference.md]
---
# User 数据模型

`User` 是账号与权限的唯一载体，表名由 SQLModel 从类名推导为 `user`。邮箱唯一且索引，密码只存哈希，`created_at` 默认 UTC。

## 1. 字段字典

| 字段 | 类型 | 必填 | 约束 | 含义 |
|---|---|---|---|---|
| `id` | UUID | 是 | 主键，默认 uuid4 | 用户标识 |
| `email` | EmailStr | 是 | 唯一、索引、最长 255 | 登录名 |
| `is_active` | bool | 是 | 默认 true | 是否允许登录 |
| `is_superuser` | bool | 是 | 默认 false | 是否拥有管理权限 |
| `full_name` | str 或空 | 否 | 最长 255 | 展示名 |
| `hashed_password` | str | 是 | 非空 | Argon2/bcrypt 哈希 |
| `created_at` | datetime 或空 | 否 | 默认 UTC | 创建时间 |

字段定义见 `backend/app/models.py:13-57`。

## 2. 输入/输出视图

`UserCreate` 增加 8 至 128 字符的 `password`；`UserUpdate` 所有字段可选；`UserPublic` 移除 `hashed_password`。`backend/app/models.py:59-62` 只暴露 id、email、is_active、is_superuser、full_name、created_at。

## 3. 写入与读取路径

| 操作 | 函数 | 事务 |
|---|---|---|
| 创建 | `backend/app/crud.py:10-17` | add、commit、refresh |
| 更新 | `backend/app/crud.py:20-31` | 可选重哈希，commit、refresh |
| 按邮箱查 | `backend/app/crud.py:34-37` | 只读 |
| 删除 | `backend/app/api/routes/users.py:132-143`、`:214-230` | 先删条目再删用户 |

## 4. 生命周期与约束

注册或管理员建号时校验邮箱唯一；登录时 `authenticate` 校验哈希并在算法升级时回写；删除时超级用户不可自删，普通用户删除会级联删除条目。`created_at` 由迁移 `fe56fa70289e` 引入。

相关页面：[业务总表](../index.md)、[认证与用户](../auth-and-users.md)。

## 5. 共变耦合与修改清单

1. 新增字段：同步 `backend/app/models.py:13-62`、Alembic、`UserPublic` 与前端设置页。
2. 改密码规则：同步 `backend/app/models.py:21-47`、`backend/app/core/security.py` 与测试。
3. 改删除规则：同步 `backend/app/api/routes/users.py` 与 [条目模型](item.md)。
