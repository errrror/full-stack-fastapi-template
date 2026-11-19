---
kind: domain-model
scope: item
status: draft
origin: generated
source_paths: [backend/app/models.py, backend/app/crud.py, backend/app/api/routes/items.py]
symbols: [Item, ItemCreate, ItemUpdate, ItemPublic, create_item]
upstream: [business/domain-models/index.md]
downstream: [business/items.md, integrations/downstream/postgresql.md, contracts/api-reference.md]
---
# Item 数据模型

`Item` 是用户拥有的简单内容记录，表名推导为 `item`。它只有标题、描述、创建时间与所有者，没有状态机或软删除。

## 1. 字段字典

| 字段 | 类型 | 必填 | 约束 | 含义 |
|---|---|---|---|---|
| `id` | UUID | 是 | 主键，默认 uuid4 | 条目标识 |
| `title` | str | 是 | 1 至 255 | 标题 |
| `description` | str 或空 | 否 | 最长 255 | 描述 |
| `created_at` | datetime 或空 | 否 | 默认 UTC | 创建时间 |
| `owner_id` | UUID | 是 | 外键 user.id，级联删除 | 所有者 |

字段定义见 `backend/app/models.py:70-95`。

## 2. 输入/输出视图

`ItemCreate` 只接受 `title` 与 `description`；`ItemUpdate` 两者可选；`ItemPublic` 额外返回 `id`、`owner_id`、`created_at`。`owner_id` 永远由服务端写入，见 `backend/app/api/routes/items.py:61-73`。

## 3. 读写路径

| 操作 | 函数 | 关键条件 |
|---|---|---|
| 列表 | `backend/app/api/routes/items.py:13-46` | 普通用户过滤 `owner_id` |
| 单条 | `backend/app/api/routes/items.py:48-59` | 所有者或超级用户 |
| 创建 | `backend/app/api/routes/items.py:61-73` | 注入当前用户 |
| 更新 | `backend/app/api/routes/items.py:75-97` | `exclude_unset` |
| 删除 | `backend/app/api/routes/items.py:99-111` | 直接删除 |

## 4. 约束与边界

标题为空会被 Pydantic 拒绝为 422；描述可为空；越权读取或写入返回 403；不存在返回 404。删除用户时数据库外键级联删除该用户全部条目，路由也显式执行 `delete(Item)` 作为双保险。

补充源码锚点：`backend/app/crud.py:63`。

## 5. 共变耦合与修改清单

1. 新增字段：同步模型、迁移、前端表单、`ItemPublic` 与 [条目流程](../items.md)。
2. 改归属：同步 `backend/app/api/routes/items.py` 与 [认证与用户](../auth-and-users.md)。
3. 改删除：同步 `backend/app/models.py:90-92` 与用户删除路由。
