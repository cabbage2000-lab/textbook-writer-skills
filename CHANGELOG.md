# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与语义化版本（版本语义定义见 [CONTRIBUTING.md](CONTRIBUTING.md) 发版流程一节）。

## [Unreleased]

## [0.3.0] - 2026-08-03

### Added

- `writing-style.md` 新增第 13 节「数学公式规范」：定界符唯一约定（行内 `$...$`、行间 `$$...$$`，禁用 `\(...\)`、GitHub 专属 math 代码块、`align` 等渲染器方言）、行内与行间的选择判据（分式/求和/矩阵一律行间）、公式编号体例（沿用图注 `*图 N-M*` 的写法作 `*式 N-M*`，不用依赖渲染器扩展的 `\tag{}`）、矩阵环境全书统一 `bmatrix`、多行推导用 `aligned`、公式内不写中文（理由写在公式外的正文句子里）、中文与行内公式之间加空格。动机：交付物是 `.md`，公式写法直接决定它在 GitHub/Obsidian/Typora/Pandoc 能否渲染；而上下文隔离让各章在不同会话写成，术语表只管符号语义、管不到公式语法，无约定必然跨章漂移
- 新增 reference `textbook-outline/references/performance-task-rubric.md`：表现性任务的 GRASPS 六要素（情境须是教材没直接教过的）与评价标准（rubric）写法——维度 3–5 个 × 水平 3–4 级，维度必须从持久理解或迁移目标推出（禁用"完整性/条理性"这类通用作文评分项），至少一个维度对准迁移，每格写可观察的表现描述而非程度副词；附与例题习题计划、Bloom 梯度的分工说明及 gate 呈现前自查清单。动机：UbD 阶段二的标准配置是「表现性任务 + 评价标准 + 其他证据」三件，本组合的"其他证据"由三类题承担得很充分，缺口一直在评价标准——而表现性任务是迁移目标在全书唯一的检验落点，任务不可评等于迁移目标不可验
- 教材项目落盘布局新增 `99-表现性任务.md`（契约第 3 节）：阶段 5 由主 skill 从 `00-教材设计.md`「## 四、表现性任务」派生生成的**学生可读版**——任务说明 + 评价标准表，去掉迁移目标编号一类教学设计元信息。单一来源仍是「## 四」，两处出入以「## 四」为准。属增量变更而非不兼容变更：v0.2.0 及更早创建的存量项目重入时此文件不存在，阶段 5 补生成即可，不影响续写
- 阶段 5 自检从 5 项增至 7 项：新增「学习目标覆盖矩阵」（输出「学习目标 × 章」矩阵，零覆盖的目标逐条列出并给补题建议——此前只查"持久理解 ↔ 章"与 Bloom 层级分布，后者统计的是层级不是目标，看不出哪条学习目标没题检验）与「表现性任务复核与落盘」（迁移目标覆盖 + 评价标准齐备核对，通过后派生生成 `99-表现性任务.md`）
- 新增英文版 README（`README.en.md`），与中文版结构对等；两版顶部互加语言切换链接。开头显著说明「产出为中文教材」这一事实——章节标题在 `chapter-template.md` 中硬编码为中文且规定不得改名、Bloom 动词表与排版规则均为中文，改成英文输出等于 fork 整个 `references/` 层而非切一个开关，不写清楚会让英文用户误装

### Changed

- `chapter-template.md` 章内自查清单从 6 条增至 7 条（新增公式规范自查）；其 3.1 节与 `textbook-chapter/SKILL.md` 的文体条款列举同步补入「数学公式规范」，使其在主入口可见而非仅存于 reference 深处
- `exercise-design.md` 第 6 节补入跨 skill 引用：题干、解答与提示中的公式同样遵循公式规范——此前 textbook-exercises 不读 `writing-style.md`，题目里的公式不受任何约束，与正文形成两套语法
- `textbook-outline/SKILL.md` 阶段 3 第 4 项：表现性任务从"注明对应哪条迁移目标"扩充为"GRASPS 六要素 + 评价标准表 + 呈现前自查"，并写明动机
- `ubd-framework.md` 第 1 节三阶段表的「阶段二 确定评估证据」一行补入指向 `performance-task-rubric.md` 的链接（该文档自我定位为阶段 2 内核依据，表现性任务属阶段 3 产物，故独立成文而非塞入其中）
- eval 1、eval 2 断言各从 5 条增至 6 条，分别新增表现性任务评价标准与数学公式规范的客观判定项（此前记录的 eval 1/2 通过结果对应加断言前的定义）
- `handoff-contract.md` 第 2 节：阶段 3 → 阶段 4 契约的「表现性任务每项注明对应的迁移目标」补入「并附评价标准表」；第 3 节落盘布局新增 `99-表现性任务.md` 及其派生规则与存量项目兼容说明
- `textbook/SKILL.md`：工作流总览表的阶段 5 产出、交付摘要（新增学习目标覆盖率、表现性任务数与迁移目标覆盖情况）、交付物清单同步
- `textbook-init/SKILL.md` 与 `workspace-layout.md`：流水线文件清单、目录树、README 模板的文件构成表补入 `99-表现性任务.md`——init 对它同样一律不建
- eval 5 断言从 5 条增至 7 条（七项自检齐全、学习目标覆盖矩阵、`99-表现性任务.md` 落盘与内容）；eval 6 的「未创建任何流水线文件」断言补入 `99-表现性任务.md`

### Fixed

- 中文 README 的 version badge 此前停留在 0.1.0（v0.2.0 发版时漏更新，与 `plugin.json`/`marketplace.json` 及 CHANGELOG 三处均不一致），本次随发版一并同步至 0.3.0

本轮三步（数学公式规范 → 表现性任务评价标准 → 交付闭环与学习目标覆盖）合并发布。`.progress.json` 状态机与既有契约字段名均未改动，落盘布局为增量新增而非不兼容变更。影响半径覆盖全部 5 个 skill：按 CONTRIBUTING.md 映射表需重跑 **eval 1–6 全部六个用例**（触及契约第 3 节落盘布局故补跑 6，触及阶段 5 自检与交付摘要故补跑 5）。

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
