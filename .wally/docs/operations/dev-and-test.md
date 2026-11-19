---
kind: operations
scope: dev-and-test
status: draft
origin: generated
source_paths: [backend/scripts/test.sh, backend/scripts/lint.sh, frontend/package.json, .pre-commit-config.yaml, .github/workflows/test-backend.yml, .github/workflows/playwright.yml]
symbols: [coverage, pytest, mypy, ruff, biome, playwright]
upstream: [INDEX.md]
downstream: [unittest/unittest.md, integration_test/integration_test.md, contracts/configuration.md, operations/deployment-and-runtime.md]
---
# 构建、单测与集成测试

本页只记录仓库实际命令与映射，详细测试规范见外部权威页 [单元测试规范](../unittest/unittest.md) 与 [集成测试规范](../integration_test/integration_test.md)。

## 1. 本地命令

| 目的 | 命令 | 工作目录 | 证据 |
|---|---|---|---|
| 安装后端依赖 | `uv sync` | 仓库根或 `backend` | `backend/README.md` |
| 迁移与初始数据 | `uv run bash scripts/prestart.sh` | `backend` | `backend/scripts/prestart.sh:7-10` |
| 跑后端测试 | `uv run bash scripts/test.sh` | `backend` | `backend/scripts/test.sh:6-8` |
| 后端 lint | `uv run bash scripts/lint.sh` | `backend` | `backend/scripts/lint.sh:6-9` |
| 安装前端依赖 | `bun install` | 仓库根 | `frontend/README.md` |
| 前端构建 | `bun run --filter frontend build` | 仓库根 | `frontend/package.json:8` |
| 前端 E2E | `bunx playwright test` | `frontend` | `frontend/package.json:12` |
| 全量 pre-commit | `uv run prek run --all-files` | 仓库根 | `.pre-commit-config.yaml` |

## 2. 源码模块到必跑测试

| 源码 | 测试 | 说明 |
|---|---|---|
| `backend/app/api/routes/login.py` | `backend/tests/api/routes/test_login.py` | 登录、Token、找回 |
| `backend/app/api/routes/users.py` | `backend/tests/api/routes/test_users.py` | 用户 CRUD 与权限 |
| `backend/app/api/routes/items.py` | `backend/tests/api/routes/test_items.py` | 条目 CRUD |
| `backend/app/crud.py` | `backend/tests/crud/test_user.py` | 哈希、认证、更新 |
| `frontend/src/routes/` | `frontend/tests/*.spec.ts` | 页面级 E2E |

## 3. 覆盖率与门禁

`backend/scripts/test.sh:6` 用 `coverage run -m pytest tests/`，CI 在 `.github/workflows/test-backend.yml:44` 执行 `coverage report --fail-under=90`。Playwright 在 `.github/workflows/playwright.yml:81` 使用 4 分片与 `--fail-on-flaky-tests`，并在 CI 重试 2 次（`frontend/playwright.config.ts:21`）。

## 4. 测试环境依赖

后端测试需要 PostgreSQL 与 Mailpit；CI 在 `.github/workflows/test-backend.yml:28-29` 先 `docker compose up -d --wait db mailpit`。Playwright 需要完整 Compose 栈与 `.env` 中的超级用户凭据，见 `frontend/tests/config.ts`。当前沙箱没有 Python 3.14 与 Bun，未执行这些命令。

## 5. 共变耦合与修改清单

1. 改测试命令：同步 `backend/scripts/test.sh`、CI 工作流与本页。
2. 改覆盖率阈值：同步 `backend/pyproject.toml` 与 CI。
3. 改 E2E：同步 `frontend/playwright.config.ts`、`frontend/tests/` 与 [集成测试规范](../integration_test/integration_test.md)。
