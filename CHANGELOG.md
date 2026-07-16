# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与语义化版本（版本语义定义见 [CONTRIBUTING.md](CONTRIBUTING.md) 发版流程一节）。

## [Unreleased]

### Added

- plugin 化分发：`.claude-plugin/plugin.json` + `marketplace.json`，支持 `/plugin marketplace add` 安装
- GitHub Actions CI：push/PR 自动跑结构校验与单元测试
- `evals/`：M2–M5 验收场景固化为 5 个带客观断言的行为测试用例
- `CONTRIBUTING.md`：架构影响半径、DoD、skill↔eval 映射、新增 skill 清单、发版流程
- 校验脚本新增四类检查：plugin 清单一致性（name/version/description 同步）、SKILL.md 500 行预算、description 1024 字符上限、frontmatter 字段白名单
- 仓库健康检查：防止 `.claude-plugin` 被 .gitignore 忽略（分发清单必须入库）
- MIT LICENSE，plugin.json / marketplace.json 补充 `license` 字段并纳入一致性校验
- `docs/adr/`：8 篇架构决策记录（skill 组合拆分、UbD 双 gate、契约单源、上下文隔离、状态机单一写者、真算验证、三层防线、plugin 分发），固化核心决策的背景与取舍

### Changed

- README 按「解决什么问题 → 设计理念 → 使用场景」的读者视角重构，术语首次出现均配白话解释；skill 行为与安装方式无变化
- skills 从 `.claude/skills/` 迁至顶层 `skills/`（标准 plugin 布局，`.claude/skills` 改为本地软链）
- 单元测试从 8 个扩充到 20 个，覆盖全部新增校验逻辑
- **术语更名**：UbD 五件套相关表述统一改用仓库固有的描述性叫法（原隐喻沿自调研参照的开源项目，为避免误认沿袭而更换）。属**不兼容变更**：契约字段 `UbD五件套`，`00-教材设计.md` 落盘标题「## 二、UbD 五件套（已确认）」——旧标题落盘的存量教材项目重入前需手工改标题；独立模式改称"轻量版五件套"
- **skill 全线改名**：统一为 `textbook-` 名词族——`write-textbook` → `textbook`、`design-textbook-outline` → `textbook-outline`、`write-textbook-chapter` → `textbook-chapter`、`generate-textbook-exercises` → `textbook-exercises`（plugin 名 `textbook-writer` 不变，决策记录见 [ADR 0009](docs/adr/0009-unified-skill-naming.md)）。属**不兼容变更**：旧 skill 名不再存在，已安装用户升级后按新名触发；契约字段、`.progress.json` 与落盘布局均不变

### Fixed

- `.gitignore` 不再忽略 `.claude-plugin/`——此前该目录新增文件会被静默排除在版本控制外

### Eval 验收（handoff-contract 术语更名全案回归）

- 用例 1–4 重跑全部通过（各 5/5 断言，2026-07-14）：M2 双 gate、M3 单章+例题真算验证、M4 端到端含中断续写
- eval 4 中断可续经独立核验：重入后 01/02 章文件 SHA-1 与中断前指纹逐字一致（已完成章未被重写），状态机续点 `current_stage=4 → chapters.next=3` 定位准确；全书 7 章 58 题 `⚠️ 需作者确认` 残留 0 条

## [0.1.0] - 2026-07-14

### Added

- M1 骨架：4 个 skill（write-textbook 主 skill + design-textbook-outline / write-textbook-chapter / generate-textbook-exercises）
- 6 个 references：交接契约与状态机、UbD 框架、Bloom 层级表、章节模板、文体规范、例题设计规范
- 结构校验脚本 `scripts/validate_skills.py` 及其单元测试
- PRD、调研报告、实施计划（docs/）
- M1 验收：3 项行为冒烟测试通过，修正 15 处指令缺陷
