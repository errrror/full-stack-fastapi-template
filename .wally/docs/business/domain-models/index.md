---
kind: business-index
scope: domain-models
status: draft
origin: generated
source_paths: [backend/app/models.py, backend/app/alembic/versions/fe56fa70289e_add_created_at_to_user_and_item.py, backend/app/alembic/versions/1a31ce608336_add_cascade_delete_relationships.py]
symbols: [User, Item, UserPublic, ItemPublic, upgrade]
upstream: [business/index.md]
downstream: [business/domain-models/user.md, business/domain-models/item.md, integrations/downstream/postgresql.md]
---
# 领域模型总览

持久化模型只有两张表：`user` 与 `item`。两者是一对多关系，用户删除时条目级联删除。其余类都是请求/响应 DTO，不落库。

## 1. 实体关系

| 左 | 基数 | 右 | 关系字段 | 删除行为 |
|---|---|---|---|---|
| User | 1 对多 | Item | `Item.owner_id` | 级联删除 |

`backend/app/models.py:56` 的 `items` 关系声明 `cascade_delete=True`，`backend/app/models.py:90-92` 的外键声明 `ondelete="CASCADE"`，迁移 `backend/app/alembic/versions/1a31ce608336_add_cascade_delete_relationships.py:30` 提供 `downgrade()`。

## 2. 表与 DTO 对照

| 用途 | 表模型 | 创建 DTO | 更新 DTO | 输出 DTO |
|---|---|---|---|---|
| 用户 | `User` (`backend/app/models.py:51`) | `UserCreate` (`:21`) | `UserUpdate` (`:32`) | `UserPublic` (`:59`) |
| 条目 | `Item` (`backend/app/models.py:87`) | `ItemCreate` (`:76`) | `ItemUpdate` (`:81`) | `ItemPublic` (`:97`) |

## 3. 迁移历史

| 版本 | 作用 | 文件 |
|---|---|---|
| `e2412789c190` | 初始化模型 | `backend/app/alembic/versions/e2412789c190_initialize_models.py` |
| `d98dd8ec85a3` | 整数 ID 改 UUID | `backend/app/alembic/versions/d98dd8ec85a3_edit_replace_id_integers_in_all_models_.py` |
| `fe56fa70289e` | 增加 `created_at` | `backend/app/alembic/versions/fe56fa70289e_add_created_at_to_user_and_item.py` |
| `9c0a54914c78` | 字符串最大长度 | `backend/app/alembic/versions/9c0a54914c78_add_max_length_for_string_varchar_.py` |
| `1a31ce608336` | 级联删除关系 | `backend/app/alembic/versions/1a31ce608336_add_cascade_delete_relationships.py` |

## 4. 写入者与读取者

| 表 | 写入者 | 读取者 |
|---|---|---|
| user | `backend/app/crud.py:10-31`、`backend/app/api/routes/users.py` | `backend/app/api/routes/users.py`、`backend/app/api/deps.py` |
| item | `backend/app/api/routes/items.py:61-107`、`backend/app/crud.py:63-68` | `backend/app/api/routes/items.py:13-59` |

## 5. 共变耦合与修改清单

1. 改字段：生成新 Alembic 迁移，更新本页、[用户模型](user.md)/[条目模型](item.md) 与 [PostgreSQL 契约](../../integrations/downstream/postgresql.md)。
2. 改关系：同步 `backend/app/models.py:51-95` 与删除路由。
3. 改迁移：验证 `downgrade()` 可执行，并补迁移测试。
