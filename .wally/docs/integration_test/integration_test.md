# 集成测试规范

> 本项目的集成测试是 Playwright 端到端测试，覆盖浏览器、FastAPI、PostgreSQL 与 Mailpit 的完整交互。环境部署见 [测试环境部署](../devops/test-env-deploy.md)，业务入口见 [业务流程总表](../business/index.md)。

> Source: `frontend/tests/`、`frontend/playwright.config.ts`、`.github/workflows/playwright.yml`、`compose.override.yml`
> Last-verified: 2026-11-19（静态核对，未执行）

---

## 一、环境与依赖

| 项 | 要求 | 来源 |
|---|---|---|
| 运行器 | Playwright 1.64.1 | `frontend/package.json` |
| 浏览器 | Chromium（配置仅启用 chromium） | `frontend/playwright.config.ts:45-55` |
| 应用栈 | Compose 的 backend、db、mailpit | `compose.override.yml` |
| 鉴权 | `.env` 的 `FIRST_SUPERUSER` 与 `FIRST_SUPERUSER_PASSWORD` | `frontend/tests/config.ts:15-22` |
| 前置迁移 | `backend/scripts/prestart.sh` | `.github/workflows/playwright.yml:77-79` |
| 健康检查 | `http://backend:8000/api/v1/utils/health-check/` | `compose.override.yml` |

测试数据来自本地 `.env`，不得把测试指向生产域名或使用真实用户凭据。`frontend/tests/config.ts:9-13` 在缺少变量时直接抛错。

## 二、用例设计

| 文件 | 覆盖 |
|---|---|
| `frontend/tests/login.spec.ts` | 登录表单、成功/失败、Token |
| `frontend/tests/sign-up.spec.ts` | 注册与重复邮箱 |
| `frontend/tests/reset-password.spec.ts` | 找回密码与 Mailpit 邮件 |
| `frontend/tests/admin.spec.ts` | 超级用户用户管理 |
| `frontend/tests/items.spec.ts` | 条目 CRUD 与所有者隔离 |
| `frontend/tests/user-settings.spec.ts` | 资料、改密、删号 |
| `frontend/tests/auth.setup.ts` | 登录并保存 storageState |

断言应覆盖页面结果与副作用，例如条目创建后列表出现新行、删除后消失；不能只断言 HTTP 200。共享登录态由 `playwright/.auth/user.json` 提供，测试之间通过独立数据与 `docker compose down -v` 清理隔离。

## 三、执行与判定

```bash
# 启动依赖并迁移
docker compose run --rm backend bash scripts/prestart.sh
docker compose up -d --wait backend

# 运行全部 E2E
docker compose run --rm playwright bunx playwright test --fail-on-flaky-tests

# 本地 UI 模式
cd frontend
bunx playwright test --ui
```

CI 在 `.github/workflows/playwright.yml:50-51` 使用 4 个分片，`.github/workflows/playwright.yml:81` 加 `--fail-on-flaky-tests` 与失败 trace。成功判据：退出码 0、失败数 0、无 flaky；报告在 `frontend/playwright-report`，失败 trace 在 `frontend/test-results`。

## 四、隔离、清理与缺陷 A/B

- 每次运行前 `docker compose down -v --remove-orphans` 清空数据库卷，避免残留用户或条目。
- 测试创建的用户使用随机邮箱，避免与初始超级用户冲突。
- 缺陷复现：先保留失败用例与 trace，修复后重跑同一用例；性能问题记录基线版本、样本与耗时，不把一次通过当作稳定结论。
- 邮件断言通过 Mailpit 的 `MAILPIT_HOST` 读取，不依赖真实邮件服务。

## 五、与 CI 的差异

本地默认 `reuseExistingServer` 为 true，CI 下为 false；本地重试 0 次，CI 重试 2 次。CI 的多分片与报告合并不改变用例本身，但会让单分片日志不完整，排障时应下载合并后的 HTML 报告。
