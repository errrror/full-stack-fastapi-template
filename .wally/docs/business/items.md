---
kind: business-workflow
scope: items
status: draft
origin: generated
source_paths: [backend/app/api/routes/items.py, backend/app/models.py, backend/app/crud.py]
symbols: [read_items, read_item, create_item, update_item, delete_item]
upstream: [business/index.md]
downstream: [business/domain-models/item.md, contracts/api-reference.md, business/auth-and-users.md]
---
# 条目管理流程

条目是唯一按所有者隔离的业务资源。普通用户只能看到和修改自己的条目；超级用户可读取全部条目。接口提供列表、单条读取、创建、更新和删除五个操作。

## 1. 列表查询分支

```text
GET /api/v1/items/
  → backend/app/api/routes/items.py:13 read_items()
      ├─ [superuser] count(Item) + select(Item).order_by(created_at desc)
      └─ [普通用户] count(Item where owner_id=me) + select(... where owner_id=me)
  → offset(skip).limit(limit) 默认 0/100
  → ItemsPublic(data=[ItemPublic], count)
```

## 2. 单条与写操作

| 操作 | 入口 | 权限 | 关键行为 |
|---|---|---|---|
| 读取单条 | `GET /items/{id}` | 所有者或超级用户 | 不存在 404，越权 403 |
| 创建 | `POST /items/` | 登录用户 | 服务端写入 `owner_id` |
| 更新 | `PUT /items/{id}` | 所有者或超级用户 | 只更新传入字段 |
| 删除 | `DELETE /items/{id}` | 所有者或超级用户 | 直接删除并提交 |

## 3. 字段与约束

| 字段 | 类型 | 约束 | 来源 |
|---|---|---|---|
| `title` | str | 1 至 255 | `backend/app/models.py:71` |
| `description` | str 或空 | 最长 255 | `backend/app/models.py:72` |
| `owner_id` | UUID | 非空外键 | `backend/app/models.py:90-92` |
| `created_at` | datetime | 默认 UTC 当前时间 | `backend/app/models.py:89` |

## 4. 错误与边界

| 场景 | 状态 | 文案 | 证据 |
|---|---|---|---|
| 条目不存在 | 404 | Item not found | `backend/app/api/routes/items.py:52-53` |
| 非所有者读取 | 403 | Not enough permissions | `backend/app/api/routes/items.py:54-55` |
| 非所有者更新/删除 | 403 | Not enough permissions | `backend/app/api/routes/items.py:83-85` |
| 标题为空 | 422 | Pydantic 校验 | `backend/app/models.py:71` |

补充源码锚点：`backend/app/crud.py:63`。

## 5. 共变耦合与修改清单

1. 新增字段：同步 `backend/app/models.py:70-101`、Alembic 迁移、前端表单与 [条目模型](domain-models/item.md)。
2. 改分页：同步 `backend/app/api/routes/items.py:13-46` 与前端 DataTable 查询参数。
3. 改归属规则：同步 [认证与用户](auth-and-users.md) 与 Playwright items 用例。
