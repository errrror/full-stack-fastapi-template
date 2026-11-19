---
kind: downstream-contract
scope: postgresql
status: draft
origin: generated
source_paths: [backend/app/core/db.py, backend/app/models.py, backend/app/crud.py, backend/app/alembic/env.py, backend/app/core/config.py]
symbols: [engine, Session, User, Item, run_migrations_online]
upstream: [integrations/index.md]
downstream: [business/domain-models/index.md, contracts/configuration.md, integrations/topology-and-mapping.md]
---
# PostgreSQL 下游契约

后端通过 SQLModel 与 psycopg 访问 PostgreSQL，连接串来自 `DATABASE_URL`。所有业务查询都经 `Session` 执行，没有裸 SQL 拼接；表结构由 Alembic 迁移维护。

## 1. 连接与驱动

| 项 | 值 | 来源 |
|---|---|---|
| 驱动 | `postgresql+psycopg` | `backend/app/core/config.py:34-40` 自动改写 |
| 连接池 | `pool_pre_ping=True` | `backend/app/core/db.py:7` |
| 迁移入口 | `alembic upgrade head` | `backend/scripts/prestart.sh:7` |
| 迁移环境 | `backend/app/alembic/env.py` | 读取 `settings.DATABASE_URL` |

## 2. 请求字典与字段

`DATABASE_URL` 是唯一连接配置，Compose 注入格式为 `postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/app`（`compose.yml:64`）。ORM 写入字段如下：

| 表 | 字段 | 类型 | 约束 | 证据 |
|---|---|---|---|---|
| user | `id` | UUID | 主键 | `backend/app/models.py:52` |
| user | `email` | str | 唯一、索引、最长 255 | `backend/app/models.py:14` |
| user | `hashed_password` | str | 非空 | `backend/app/models.py:53` |
| item | `id` | UUID | 主键 | `backend/app/models.py:88` |
| item | `owner_id` | UUID | 外键 user.id，级联删除 | `backend/app/models.py:90-92` |
| item | `title` | str | 1 至 255 | `backend/app/models.py:71` |

## 3. 查询与事务行为

- 用户查询：`backend/app/crud.py:34-37` 使用 `select(User).where(User.email == email)`，参数化绑定。
- 条目列表：`backend/app/api/routes/items.py:13-46` 按角色选择 count 与分页语句，普通用户强制 `owner_id` 过滤。
- 写事务：`backend/app/crud.py:10-17`、`backend/app/crud.py:20-31` 均 `commit` 后 `refresh`，异常会向上抛出并由 FastAPI 返回 500。
- 初始化：`backend/app/core/db.py:15-33` 只在缺失时创建首个超级用户，不建表。

## 4. 错误与恢复

| 场景 | 表现 | 处理 |
|---|---|---|
| 连接串错误 | 启动后首个请求 500 | 检查 `DATABASE_URL` 与 db 健康检查 |
| 迁移未执行 | 表不存在，查询报错 | 运行 `backend/scripts/prestart.sh` |
| 唯一键冲突 | 路由先查重，通常返回 400 | 并发下仍可能 500，需重试 |
| 迁移回滚 | Alembic 版本含 `downgrade()` | 无文档化流程，见 [高危雷区](../../operations/pitfalls-and-adr.md) |

## 5. 共变耦合与修改清单

1. 改模型：生成 Alembic 迁移，更新 [领域模型总览](../../business/domain-models/index.md) 与本页字段表。
2. 改连接：同步 `backend/app/core/config.py:31-40`、`.env` 与 [配置手册](../../contracts/configuration.md)。
3. 改查询：补对应 Pytest 用例并核对 N+1 风险。
