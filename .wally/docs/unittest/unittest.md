# 单元测试规范（环境 / 生成 / 运行调试）

> 目标：能在本地安装依赖、编写 Pytest 用例、运行并定位失败。源码事实与调用链见 [构建与单测](../operations/dev-and-test.md)，认证流程见 [认证与用户](../business/auth-and-users.md)。

> Source: `backend/tests/`、`backend/scripts/test.sh`、`backend/pyproject.toml`、`.github/workflows/test-backend.yml`
> Last-verified: 2026-11-19（静态核对，未执行）

---

## 一、环境搭建

### 1. 前置依赖

| 项 | 要求 | 检查 |
|---|---|---|
| Python | 3.14 | `python3 --version` |
| uv | 任意近期版本 | `uv --version` |
| PostgreSQL | 18，Compose 服务 `db` | `docker compose up -d --wait db` |
| Mailpit | Compose 服务 `mailpit` | `docker compose up -d --wait mailpit` |

### 2. 安装与迁移

```bash
cd backend
uv sync
cd ..
docker compose up -d --wait db mailpit
cd backend
FASTAPI_ENV=development uv run bash scripts/prestart.sh
```

`backend/scripts/prestart.sh:7-10` 会执行 Alembic 迁移并创建初始超级用户。测试使用真实 Session，见 `backend/tests/conftest.py:14-24`，因此数据库必须先就绪。

## 二、生成规范

| 规范 | 要求 | 参考 |
|---|---|---|
| 目录 | 路由测试放 `backend/tests/api/routes/`，CRUD 放 `backend/tests/crud/` | 现有 5 个测试文件 |
| Fixture | 复用 `client`、`superuser_token_headers`、`normal_user_token_headers` | `backend/tests/conftest.py:27-44` |
| 断言 | 至少断言状态码与关键字段；错误分支断言 detail | `backend/tests/api/routes/test_login.py:13-35` |
| 数据 | 使用 `random_email()` 与 `random_lower_string()`，避免固定邮箱冲突 | `backend/tests/utils/utils.py` |
| 清理 | 会话级 fixture 在 yield 后删除 Item 与 User | `backend/tests/conftest.py:14-24` |
| Mock | 外部邮件用 `patch("app.utils.send_email")`，不真实发信 | `backend/tests/api/routes/test_users.py:41-46` |

## 三、运行与调试

```bash
# 全量测试 + 覆盖率
cd backend
uv run bash scripts/test.sh

# 单个文件
uv run pytest tests/api/routes/test_items.py -q

# 单个用例
uv run pytest tests/crud/test_user.py::test_create_user -q
```

`backend/scripts/test.sh:6` 使用 `coverage run -m pytest tests/`，随后输出终端覆盖率与 `htmlcov/index.html`。CI 在 `.github/workflows/test-backend.yml:44` 要求 `--fail-under=90`。

| 现象 | 排查 |
|---|---|
| 连接数据库失败 | 检查 `DATABASE_URL`、db 健康、迁移是否执行 |
| 401/403 | 检查 `superuser_token_headers` 与 `SECRET_KEY` |
| 邮件相关 500 | 确认已 patch `send_email` 或配置 Mailpit |
| 覆盖率不足 90 | 看 `htmlcov/index.html` 的未覆盖行，补异常分支 |

## 四、与源码的映射

| 源码 | 必跑测试 |
|---|---|
| `backend/app/api/routes/login.py` | `backend/tests/api/routes/test_login.py` |
| `backend/app/api/routes/users.py` | `backend/tests/api/routes/test_users.py` |
| `backend/app/api/routes/items.py` | `backend/tests/api/routes/test_items.py` |
| `backend/app/crud.py` | `backend/tests/crud/test_user.py` |
| `backend/app/api/routes/private.py` | `backend/tests/api/routes/test_private.py` |

新增源码模块时，在同一层级补测试文件，并在 [构建与单测](../operations/dev-and-test.md) 的映射表登记。
