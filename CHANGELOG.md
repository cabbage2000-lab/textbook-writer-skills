# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与语义化版本（版本语义定义见 [CONTRIBUTING.md](CONTRIBUTING.md) 发版流程一节）。

## [Unreleased]

## [0.2.0] - 2026-07-16

### Added

- plugin 化分发：`.claude-plugin/plugin.json` + `marketplace.json`，支持 `/plugin marketplace add` 安装
- GitHub Actions CI：push/PR 自动跑结构校验与单元测试
- `evals/`：M2–M6 验收场景固化为 6 个带客观断言的行为测试用例
- `CONTRIBUTING.md`：架构影响半径、DoD、skill↔eval 映射、新增 skill 清单、发版流程
- 校验脚本新增四类检查：plugin 清单一致性（name/version/description 同步）、SKILL.md 500 行预算、description 1024 字符上限、frontmatter 字段白名单
- 仓库健康检查：防止 `.claude-plugin` 被 .gitignore 忽略（分发清单必须入库）
- MIT LICENSE，plugin.json / marketplace.json 补充 `license` 字段并纳入一致性校验
- `docs/adr/`：8 篇架构决策记录（skill 组合拆分、UbD 双 gate、契约单源、上下文隔离、状态机单一写者、真算验证、三层防线、plugin 分发），固化核心决策的背景与取舍
- Codex 基本支持：仓库根新增 `AGENTS.md` 作为入口指路文件（触发路由表 + 跨 skill 调用桥接说明 + 三条红线提醒），README 补充「在 Codex 中使用」小节；不改动任何 skill 行为与 `handoff-contract.md` 契约
- 新增 skill `textbook-init`（独立辅助，不入调度链）：动笔前规划并创建工作目录——一轮提问 + 方案停点确认后创建单本项目目录或多教材工作区，可选 git 版本管理（`.progress.json` 明确入库以支持换机续写）与 README 工作说明；只建目录骨架，绝不创建流水线文件（`.progress.json`/`00-教材设计.md`/`术语表.md`）。现有 4 个 skill 与契约零改动；配套 eval 6（M6）行为用例与各文档交叉引用同步
- GitHub Actions：push `v*` tag 时自动创建/更新对应的 GitHub Release，说明文字取自 CHANGELOG 对应版本段（`.github/workflows/release.yml` + `scripts/extract_changelog_notes.py`）

### Changed

- README 按「解决什么问题 → 设计理念 → 使用场景」的读者视角重构，术语首次出现均配白话解释；skill 行为与安装方式无变化
- skills 从 `.claude/skills/` 迁至顶层 `skills/`（标准 plugin 布局，`.claude/skills` 改为本地软链）
- 单元测试从 8 个扩充到 20 个，覆盖全部新增校验逻辑
- **术语更名**：UbD 五件套相关表述统一改用仓库固有的描述性叫法（原隐喻沿自调研参照的开源项目，为避免误认沿袭而更换）。属**不兼容变更**：契约字段 `UbD五件套`，`00-教材设计.md` 落盘标题「## 二、UbD 五件套（已确认）」——旧标题落盘的存量教材项目重入前需手工改标题；独立模式改称"轻量版五件套"
- **skill 全线改名**：统一为 `textbook-` 名词族——`write-textbook` → `textbook`、`design-textbook-outline` → `textbook-outline`、`write-textbook-chapter` → `textbook-chapter`、`generate-textbook-exercises` → `textbook-exercises`（plugin 名 `textbook-writer` 不变，决策记录见 [ADR 0009](docs/adr/0009-unified-skill-naming.md)）。属**不兼容变更**：旧 skill 名不再存在，已安装用户升级后按新名触发；契约字段、`.progress.json` 与落盘布局均不变
- **evals 用例 4/5 职责拆分**：eval 4 收窄为只验证中断-续写机制（写 1 章→中断→续 2 章即可判定，耗时从数小时降到 ~40-60 分钟），不再要求写完整本教材；「整本书写完 + 阶段 5 自检 + 交付摘要」的验收职责移交 eval 5。目的是让日常迭代改动契约时不必每次都陪跑一整本书的写作时间。详见 [evals/README.md](evals/README.md)；此前 2026-07-14 记录的 eval 4 通过结果对应收窄前的旧定义，已按新定义重新跑过（见下方 Eval 验收）

### Fixed

- `.gitignore` 不再忽略 `.claude-plugin/`——此前该目录新增文件会被静默排除在版本控制外

### Eval 验收（handoff-contract 术语更名全案回归）

- 用例 1–4 重跑全部通过（各 5/5 断言，2026-07-14）：M2 双 gate、M3 单章+例题真算验证、M4 端到端含中断续写
- eval 4 中断可续经独立核验：重入后 01/02 章文件 SHA-1 与中断前指纹逐字一致（已完成章未被重写），状态机续点 `current_stage=4 → chapters.next=3` 定位准确；全书 7 章 58 题 `⚠️ 需作者确认` 残留 0 条

### Eval 验收（eval 4 收窄后新定义首次运行）

- eval 4 按收窄后的新定义重跑通过（3/3 断言，2026-07-16）：判定见 `evals/workspace/2026-07-16-eval-4/outputs/judgment.md`
- 独立核验：中断前 `.progress.json` = `chapters.done=[1]/next=2`，续写后 = `done=[1,2]/next=3`；01 章文件 SHA-1 续写前后逐字一致（未被重写）；02 章引言正确衔接 01 章「本章小结」核心结论；术语表.md 由 7 条正确追加至 14 条
- eval 5（M5，全书完成 + 阶段 5 自检 + 交付摘要的新验收责任方）尚未运行，是发版 0.2.0 前唯一剩余的重量级验收项

## [0.1.0] - 2026-07-14

### Added

- M1 骨架：4 个 skill（write-textbook 主 skill + design-textbook-outline / write-textbook-chapter / generate-textbook-exercises）
- 6 个 references：交接契约与状态机、UbD 框架、Bloom 层级表、章节模板、文体规范、例题设计规范
- 结构校验脚本 `scripts/validate_skills.py` 及其单元测试
- PRD、调研报告、实施计划（docs/）
- M1 验收：3 项行为冒烟测试通过，修正 15 处指令缺陷
