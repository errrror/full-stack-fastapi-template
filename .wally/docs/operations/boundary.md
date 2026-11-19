---
kind: operations
scope: boundary
status: draft
origin: generated
source_paths: [.gitignore, .dockerignore, .fastapicloudignore, hooks/post_gen_project.py, .agents/skills/library-skills/SKILL.md, img/dashboard.png]
symbols: [post_gen_project, library-skills]
upstream: [INDEX.md]
downstream: [architecture/index.md, operations/deployment-and-runtime.md, overview/system-architecture.md]
---
# 认知边界与仓库外黑盒

本知识库只覆盖当前工作树的已提交源码与配置，不包含部署环境、真实数据、第三方服务内部实现或未提交的本地改动。以下边界用于防止 Agent 把推测当成事实。

## 1. 快照与工作树边界

基线是 `master` @ `77e550a`。本次初始化新增的 `.wally/`、`AGENTS.md`、`CODEBUDDY.md`、`CLAUDE.md`、`.codebuddy/` 等尚未提交，不计入源码基线；`.wally/docs/.wiki-meta.json` 因而保留空 `commitHash`，下次全量检查。

## 2. 仓库外黑盒

| 外部对象 | 本仓已知 | 本仓未知 |
|---|---|---|
| PostgreSQL | 连接串、ORM 模型、迁移 | 实际数据、备份策略、慢查询 |
| SMTP | 主机、端口、TLS、账号变量 | 服务商、退信策略、配额 |
| Sentry | DSN 变量、初始化条件 | 项目配置、采样率、保留期 |
| FastAPI Cloud | 部署工作流与 secret 名 | 实际环境、域名、资源规格 |
| Traefik | Compose 配置与证书卷 | 证书状态、上游网络 |

## 3. 生成物与第三方代码

`frontend/src/client/**` 与 `frontend/src/routeTree.gen.ts` 是生成文件，不应手工编辑；`frontend/src/components/ui/**` 是 shadcn/ui 组件；`backend/app/email-templates/*.html` 由 React Email 导出。它们的行为以其生成器为准，本库只描述入口与耦合。

## 4. 未覆盖范围

- 未执行真实构建、测试、部署或数据库迁移；本库是静态阅读与配置核对的结果。
- 未读取任何生产数据、日志或密钥；`.env` 只按变量名与默认值记录。
- 未覆盖 Cookiecutter 生成流程在模板仓库之外的行为；`hooks/post_gen_project.py` 只作为模板钩子登记。
- 未覆盖 `.agents`、`.claude` 中指向 `.venv` 的 skill 软链内容；当前工作树没有 `.venv`，链接不可用。

补充源码锚点：`.gitignore:1`、`.dockerignore:1`、`.fastapicloudignore:1`、`.agents/skills/library-skills/SKILL.md:1`、`img/dashboard.png:1`。

## 5. 共变耦合与修改清单

1. 新增外部服务：在 [集成总览](../integrations/index.md) 建下游页，并更新本页黑盒表。
2. 新增生成文件：在 [架构总表](../architecture/index.md) 的 Tier 3 表登记，注明生成器。
3. 提交 `.wally/` 后：更新 `.wiki-meta.json` 的 `commitHash` 与基线说明。
