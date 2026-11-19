---
kind: business-index
scope: workflows
status: draft
origin: generated
source_paths: [backend/app/api/routes/login.py, backend/app/api/routes/users.py, backend/app/api/routes/items.py, backend/app/models.py]
symbols: [login_access_token, register_user, read_items, User, Item]
upstream: [INDEX.md]
downstream: [business/auth-and-users.md, business/items.md, business/password-recovery.md, business/domain-models/index.md]
---
# 业务流程总表

仓库的业务面很小，但权限分支集中：登录、用户管理、条目 CRUD、密码找回。四条流程都围绕 `User` 与 `Item` 两个实体，任何一条改动都可能影响鉴权或前端路由。

## 1. 全量 WF 总表

| WF | 名称 | 触发 | 主要入口 | 结果 | 详情 |
|---|---|---|---|---|---|
| WF-AUTH | 登录与令牌 | 邮箱密码 | `backend/app/api/routes/login.py:23` | JWT Bearer Token | [认证与用户](auth-and-users.md) |
| WF-USER | 用户管理 | 注册或管理员操作 | `backend/app/api/routes/users.py:54` | 用户记录与公开视图 | [认证与用户](auth-and-users.md) |
| WF-ITEM | 条目 CRUD | 登录用户 | `backend/app/api/routes/items.py:13` | 所有者隔离的条目 | [条目流程](items.md) |
| WF-RESET | 密码找回 | 邮箱 | `backend/app/api/routes/login.py:53` | 重置令牌与邮件 | [密码找回](password-recovery.md) |

## 2. 角色与入口交叉

| 入口 | 匿名 | 普通用户 | 超级用户 |
|---|---|---|---|
| `/login/access-token` | 允许 | 允许 | 允许 |
| `/users/signup` | 允许 | 允许 | 允许 |
| `/users/me` | 拒绝 | 本人 | 本人 |
| `/users/` | 拒绝 | 拒绝 | 全部 |
| `/items/` | 拒绝 | 本人 | 全部 |
| `/utils/test-email/` | 拒绝 | 拒绝 | 允许 |
| `/utils/health-check/` | 允许 | 允许 | 允许 |

## 3. 业务实体与不变量

| 实体 | 关键约束 | 违反后果 | 证据 |
|---|---|---|---|
| User | 邮箱唯一、密码哈希、超级用户不可自删 | 400/403 | `backend/app/models.py:13-57` |
| Item | 必须属于用户、标题非空 | 403/404 | `backend/app/models.py:70-101` |
| Token | 8 天过期、HS256 签名 | 403 | `backend/app/core/config.py:25` |

## 4. 错误与流程交叉索引

| 错误 | 常见流程 | 处理入口 |
|---|---|---|
| 400 Incorrect email or password | WF-AUTH | `backend/app/api/routes/login.py:34-40` |
| 403 Not enough permissions | WF-ITEM | `backend/app/api/routes/items.py:48-59` |
| 404 Item not found | WF-ITEM | `backend/app/api/routes/items.py:48-59` |
| 409 User with this email already exists | WF-USER | `backend/app/api/routes/users.py:81-101` |

## 5. 共变耦合与修改清单

1. 新增流程：在 `business/` 新建页，补 [接口全集](../contracts/api-reference.md) 与测试。
2. 改权限矩阵：同步 [认证与用户](auth-and-users.md)、[领域模型](domain-models/index.md) 与前端守门。
3. 改错误语义：同步 [错误码字典](../contracts/error-codes.md)。
