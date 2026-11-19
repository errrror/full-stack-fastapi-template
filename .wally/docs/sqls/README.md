# 数据库 / 持久化结构

> 本项目使用 PostgreSQL 18，表结构由 SQLModel 模型与 Alembic 迁移定义；没有单独的 DDL 文件。字段字典见 [用户模型](../business/domain-models/user.md) 与 [条目模型](../business/domain-models/item.md)，连接与事务见 [PostgreSQL 下游契约](../integrations/downstream/postgresql.md)。

> Source: `backend/app/models.py`、`backend/app/alembic/versions/`、`backend/app/core/db.py`
> Last-verified: 2026-11-19（静态核对，未连接数据库）

---

## 一、数据库清单

| DB | 用途 | 主要表 | 迁移来源 |
|---|---|---|---|
| PostgreSQL 18 | 业务数据 | `user`、`item` | `backend/app/alembic/versions/` |
| 本地测试库 | Pytest 与 Playwright | 同上 | `backend/scripts/prestart.sh` |

连接串来自 `DATABASE_URL`，`backend/app/core/config.py:34-40` 会把 `postgres://` 或 `postgresql://` 改写为 `postgresql+psycopg://`。

## 二、表结构摘要

| 表 | 主键 | 关键列 | 约束 |
|---|---|---|---|
| `user` | `id` UUID | `email`、`hashed_password`、`is_active`、`is_superuser`、`full_name`、`created_at` | 邮箱唯一且索引，密码非空 |
| `item` | `id` UUID | `title`、`description`、`owner_id`、`created_at` | `owner_id` 外键 `user.id`，级联删除，标题 1 至 255 |

`user` 与 `item` 是一对多关系，删除用户会级联删除其条目。字段定义见 `backend/app/models.py:13-101`。

## 三、迁移清单

| 版本 | 作用 |
|---|---|
| `e2412789c190` | 初始化 `user` 与 `item` |
| `d98dd8ec85a3` | 整数 ID 改为 UUID |
| `fe56fa70289e` | 增加 `created_at` |
| `9c0a54914c78` | 字符串最大长度 |
| `1a31ce608336` | 级联删除关系 |

执行 `alembic upgrade head` 应用迁移，见 `backend/scripts/prestart.sh:7`。迁移文件含 `downgrade()`，但仓库没有文档化的回滚流程。

## 四、维护规则

1. 修改 `backend/app/models.py` 后生成新迁移，不手改已应用迁移。
2. 更新本页表结构摘要与领域模型页。
3. 迁移变更必须补对应测试；删除字段前确认无路由或查询引用。
4. 不把生产数据或真实连接串写入本目录。
