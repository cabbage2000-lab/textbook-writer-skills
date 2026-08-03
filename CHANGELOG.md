# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与语义化版本（版本语义定义见 [CONTRIBUTING.md](CONTRIBUTING.md) 发版流程一节）。

## [Unreleased]

## [0.3.0] - 2026-08-03

### Added

- **Codex 与 WorkBuddy 支持**：三个宿主都能一键装。新增 Codex 的两份分发清单——`.codex-plugin/plugin.json`（除公共元信息外还有 Codex 摄取必需的 `skills: "./skills/"` 指针与整块 `interface`）与 `.agents/plugins/marketplace.json`（条目的 `source` 是对象、必带 `policy`），装法 `codex plugin marketplace add cabbage2000-lab/textbook-writer-skills` + `codex plugin add textbook-writer@textbook-writer-skills`；新增 WorkBuddy（CodeBuddy 内核）的两份清单 `.codebuddy-plugin/{plugin,marketplace}.json`（结构与 Claude 版同构，skills 靠 plugin 根下的 `skills/` 自动发现），装法与 Claude Code 相同的 `/plugin marketplace add` + `/plugin install`；复制安装同时保留，三宿主的用户级/项目级目录对照写进 README（WorkBuddy 项目级是 `.codebuddy/skills/` 而非 `.workbuddy/`）。动机：跨宿主中立一直是设计约束（skill 只依赖 SKILL.md + `references/` + 相对路径这套通用标准，两处宿主专有能力都带纯文本降级），但**装法上没兑现**——此前只有 Claude Code 能一键装，Codex 侧靠 `AGENTS.md` 在仓库内兜底、WorkBuddy 连目录说明都没有。三套清单格式不同、合不成一份，只能各写一份 + 用校验守住不漂
- 校验脚本 `validate_manifests` 从守两份清单扩展为守**三宿主六份清单**：公共字段（name/version/description/license）跨宿主逐字一致，外加各宿主专有要求——Codex 的 `skills` 指针必须指向 `./skills/`（指错则一个命令都不出现）、`interface` 七个必填字段齐全（缺任一项官方摄取校验判整个 plugin 非法）、marketplace 条目为 `source: local` + `path: ./` 且 `policy.installation: AVAILABLE`；CodeBuddy 的 marketplace 必填 `owner.name`、条目 `source` 为 `./`。仓库健康检查同步扩展：`.gitignore` 不得忽略 `.codex-plugin`、`.codebuddy-plugin` 与 `.agents`，且三个 `.*-plugin/` 目录只放清单文件（`skills/` 必须留在仓库根，塞进清单目录会导致装上后一个 skill 都加载不到）。配套单元测试 14 项，总数 24 → 38
- 实测记录（2026-08-03）：Codex 侧在 codex-cli 0.146.0 上跑通完整安装链路——用隔离的 `CODEX_HOME` 添加本地路径市场、`codex plugin add` 装入，5 个 SKILL.md 与 8 个 references 全部装载、版本识别为 0.3.0，官方预检脚本 `plugin-creator/scripts/validate_plugin.py` 亦通过；Claude Code 侧沿用既有清单不受影响；**WorkBuddy 侧清单格式已由作者在其他项目实测可用**，本仓库按官方 `plugin-marketplaces.md` 规范、同一格式编写（本仓库清单未单独复测，与已验证版本的差异仅在 name/description 等元信息）；若装上后一个 skill 都不出现，先查 `skills/` 是否被误塞进 `.codebuddy-plugin/` 而非留在仓库根
- `evals/README.md` 新增「在哪个宿主跑」：Claude Code 是基线宿主（现有通过记录全部跑自它），同一套用例可在 Codex / WorkBuddy 原样复跑，判定口径相同——assertions 判的是行为红线（gate 停没停、题目验没验、续点定位对不对、落盘齐不齐）而非逐字文本，判定记录须写明宿主与版本；跨宿主结果不一致时先定位是谁错，别默认第二宿主错
- CLAUDE.md 新增「分发与跨宿主」一节：三宿主的清单文件、一键装入口与散装目录对照表、三套清单为何不能合并、跨宿主中立约束及现存两处可选增强的降级路径（Skill 工具 → 直接读对方 SKILL.md；AskUserQuestion → 编号提问等文本回复），并留下上述实测记录
- README「工作原理」补两张互补的原理图，中英各一版（`images/how-it-works.svg`、`images/skill-composition.svg` 及 `.en.svg`）。**作者视角图**以一条时间线串起「作者一句话 → 教学定位 → UbD 五件套 → 停点 1 → 章节树与 Bloom 梯度 → 停点 2 → 四段式逐章写作 → 通读定稿 → 交付目录」，把两处 gate、例题真算复核、上下文隔离、每章存盘可续写四个作者能感知的承诺画在流程上；**skill 视角图**画调度关系与三条硬约束——textbook 独占读写 `.progress.json`、textbook-chapter 只收四件轻量输入且不读别章正文、textbook-exercises 由 chapter 调用且每题真算复核，`handoff-contract.md` 作为地基横贯其下，textbook-init 以虚线框游离于调度链外。动机：原「工作原理」只有一棵 ASCII 调度树，既答不了作者最关心的"我会经历什么、哪里轮到我拍板"，也画不出契约与状态单写者这两条运行时约束。手写 SVG 而非截图，改文案即改图、可 diff、无二进制包袱
- `writing-style.md` 新增第 13 节「数学公式规范」：定界符唯一约定（行内 `$...$`、行间 `$$...$$`，禁用 `\(...\)`、GitHub 专属 math 代码块、`align` 等渲染器方言）、行内与行间的选择判据（分式/求和/矩阵一律行间）、公式编号体例（沿用图注 `*图 N-M*` 的写法作 `*式 N-M*`，不用依赖渲染器扩展的 `\tag{}`）、矩阵环境全书统一 `bmatrix`、多行推导用 `aligned`、公式内不写中文（理由写在公式外的正文句子里）、中文与行内公式之间加空格。动机：交付物是 `.md`，公式写法直接决定它在 GitHub/Obsidian/Typora/Pandoc 能否渲染；而上下文隔离让各章在不同会话写成，术语表只管符号语义、管不到公式语法，无约定必然跨章漂移
- 新增 reference `textbook-outline/references/performance-task-rubric.md`：表现性任务的 GRASPS 六要素（情境须是教材没直接教过的）与评价标准（rubric）写法——维度 3–5 个 × 水平 3–4 级，维度必须从持久理解或迁移目标推出（禁用"完整性/条理性"这类通用作文评分项），至少一个维度对准迁移，每格写可观察的表现描述而非程度副词；附与例题习题计划、Bloom 梯度的分工说明及 gate 呈现前自查清单。动机：UbD 阶段二的标准配置是「表现性任务 + 评价标准 + 其他证据」三件，本组合的"其他证据"由三类题承担得很充分，缺口一直在评价标准——而表现性任务是迁移目标在全书唯一的检验落点，任务不可评等于迁移目标不可验
- 教材项目落盘布局新增 `99-表现性任务.md`（契约第 3 节）：阶段 5 由主 skill 从 `00-教材设计.md`「## 四、表现性任务」派生生成的**学生可读版**——任务说明 + 评价标准表，去掉迁移目标编号一类教学设计元信息。单一来源仍是「## 四」，两处出入以「## 四」为准。属增量变更而非不兼容变更：v0.2.0 及更早创建的存量项目重入时此文件不存在，阶段 5 补生成即可，不影响续写
- 阶段 5 自检从 5 项增至 7 项：新增「学习目标覆盖矩阵」（输出「学习目标 × 章」矩阵，零覆盖的目标逐条列出并给补题建议——此前只查"持久理解 ↔ 章"与 Bloom 层级分布，后者统计的是层级不是目标，看不出哪条学习目标没题检验）与「表现性任务复核与落盘」（迁移目标覆盖 + 评价标准齐备核对，通过后派生生成 `99-表现性任务.md`）
- 新增英文版 README（`README.en.md`），与中文版结构对等；两版顶部互加语言切换链接。开头显著说明「产出为中文教材」这一事实——章节标题在 `chapter-template.md` 中硬编码为中文且规定不得改名、Bloom 动词表与排版规则均为中文，改成英文输出等于 fork 整个 `references/` 层而非切一个开关，不写清楚会让英文用户误装

### Changed

- **双语 README 按统一骨架重排**，与姊妹项目 paper-tutor-skills 的组织逻辑对齐——读者的问题按顺序答完：这是什么 → 你凭什么这么设计 → 边界在哪 → 一张表看全 → 怎么装怎么跑 → 我该怎么开口、会拿到什么 → 凭什么信它 → 代码在哪。具体：①标题从裸仓库名改为 `Textbook-Writer-Skills 教材写作套件`，徽章上移到语言切换之前，首段补规模数字（5 个 skill = 1 主调度 + 3 子 + 1 独立辅助）、当前版本与契约文档指路；②新增「✅ 能做的 / ⛔ 不做的」双栏对照表——此前边界只有使用场景末尾一句「v1 明确不覆盖……」，读者带着错误期待读完全文才发现；③新增「五阶段流水线 × skill 能力」总表（阶段 / 执行 skill / 做什么 / 产出 / Gate / 验收用例六列），把此前散落在两张 SVG 的 alt 文字、工作原理正文与里程碑表里的信息合成一张，阶段名、执行者、产出、Gate 四列逐字取自 `textbook/SKILL.md` 的「工作流总览」，产物文件名取自契约第 3 节；④「使用场景」升级为「怎么开口说：不用背 skill 名」三列表，补上此前缺失的「你会拿到」列（读者原本无从知道产物长什么样），并新增「这些请求会被挡下——但每条都有出口」对照表与「串起来看：一本教材从头到尾」的 0→6 全景流程块；⑤原「质量保障」升格为「为什么可信」，把五条红线转成读者视角的信任论据后再接三层防线命令块，中文版补上此前只有英文版有的「第三层无法自动化」说明段；⑥「解决什么问题」三个坑压缩约四成（3 张截图原位保留，跟在对应的坑后面），「工作原理」两张 SVG 与契约说明保留；⑦里程碑表删去 `evals/workspace/…/judgment.md` 内部验收路径（对外部读者是噪音，判定证据改为一句话指向 `evals/README.md`），仓库布局代码块压成一段散文并独立为「仓库结构」一节，「贡献」与「许可」各自独立成节。动机：README 的内容一直是扎实的，缺的是组织——边界埋在末尾、能力表不写产出、没有全流程总表，读者要自己把信息从五处拼起来。两版结构逐节一一对应，后续维护不必再对着两份不同骨架改。纯编辑性改动，不涉及任何 `skills/` 文件，不触发 evals 重跑
- 双语 README 的「快速开始」改写为三宿主视角，且**安装方式全部改为提示词优先**：新增「安装」一节，给出 Claude Code / Codex / WorkBuddy 三段可直接复制粘贴给智能体的提示词（英文版为英文）——克隆到临时目录 → 把 `skills/` 下全部 5 个子目录复制进该宿主的 skills 目录 → 删临时目录 → 回报装到哪里、5 个装齐没有，读者不必敲任何命令；提示词内逐条写明 5 个 skill 以相对路径互引、漏装即断链，同名目录覆盖即更新，以及"别清空目录、别动其他来源的 skill"，WorkBuddy 那段另加「别把整个 `skills/` 目录套一层」的命名陷阱提醒。四条附注覆盖项目级安装（WorkBuddy 项目级是 `.codebuddy/skills/` 而非 `.workbuddy/`）、换用别的宿主、为何不能只装一个（`textbook-exercises` 也要读 outline 的 Bloom 动词表与 textbook 的交接契约）、以及 `AGENTS.md` 免安装路径；装错位置的表现是 skill 一个都不出现且无任何报错。原插件式一键安装（三宿主命令）与仓库内软链试跑降级为「更喜欢自己敲命令？」子节保留，并注明 WorkBuddy 插件清单的格式已由作者在其他项目实测可用。动机：目标读者是想把知识写成教材的教师、学生与内容创作者，不是命令行熟手——「按对照表把 `skills/*` 复制到正确目录、一个都不能漏」要求读者自己判断路径、自己保证完整性，是新手门槛最高的一步，而这步恰恰是智能体自己就能干的。顶部加 host badge，首段与使用场景表由「Claude Code」改为宿主中立表述；仓库布局补 `.codex-plugin/`、`.codebuddy-plugin/` 与 `AGENTS.md`
- `.claude-plugin/plugin.json` 补 `homepage` / `repository`，与另两个宿主的 plugin 清单同源
- `AGENTS.md` 重新定位为「未安装时的兜底路径」——已装插件或已复制 `skills/` 的宿主会自行加载 5 个 skill，不必依赖它的路由表；同时不再把降级路径写成 Codex 专属，并补上 AskUserQuestion 的降级说明
- `workspace-layout.md` 的 README 工作说明模板去掉写死的宿主名（「配合 Claude Code 的 textbook skill 组合使用」→ 宿主中立表述）——textbook-init 生成的教材目录 README 会被 Codex / WorkBuddy 用户看到，写死宿主名会误导。本轮唯一一处 skill 内容改动，按映射表需重跑 **eval 6**；其余改动只涉及分发清单、校验脚本与文档，不影响任何 skill 的运行行为
- CONTRIBUTING 发版流程：升版从「两处清单」改为「六份清单里带 version 的五处 + README badge」，并新增「跨宿主中立」写作规范条目
- 双语 README 的「工作原理」改为「作者视角图 → skill 视角图 → 契约说明」的顺序，原 ASCII 调度树由 skill 视角图取代（树的信息已被图完整覆盖，且图额外画出了状态单写者与契约地基）
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

- **题目验证状态行缺失（eval 5 首跑发现）**：`exercise-design.md` 第 3 节第 4 条原文只写「验证状态标注只有两种」，全文从未写死「每道题无一例外都必须带验证状态行」，加之流程第 2 条只强调「**计算类**必须独立复算」，模型据此形成「计算题标验证、概念题给参考答案即可」的误读。M5 首跑实测：全书 80 题中 **26 题（全为概念型独立习题）无任何验证状态标注**，违反契约第 2 节「验证状态 ∈ 已验证／需作者确认，无第三种」——漏行构成了事实上的第三种状态。四处收紧：`exercise-design.md` 第 3 节第 4 条改为「每道题都必须带验证状态行，无一例外」并给出非计算题的具体方式（概念与记忆理解类写 `✅ 已验证（核对定义来源：…）`，开放探究类写 `⚠️ 需作者确认（开放题，不设标准答案）`）；`chapter-template.md` 自查第 3 条补可操作判据「逐题数一遍，题目数必须等于验证行数」；`textbook-exercises/SKILL.md` 纪律段由「每题必有 Bloom 标注」扩为「Bloom 标注**与验证状态行**，漏任一即不完整」；`textbook/SKILL.md` 阶段 5 自检项 4 增加清点，缺行须报为**不通过项**而非合规项。配套 eval 2 增第 7 条、eval 5 增第 8 条断言固化「题目数 = 验证行数」
- 中文 README 的 version badge 此前停留在 0.1.0（v0.2.0 发版时漏更新，与 `plugin.json`/`marketplace.json` 及 CHANGELOG 三处均不一致），本次随发版一并同步至 0.3.0

本轮三步（数学公式规范 → 表现性任务评价标准 → 交付闭环与学习目标覆盖）合并发布。`.progress.json` 状态机与既有契约字段名均未改动，落盘布局为增量新增而非不兼容变更。影响半径覆盖全部 5 个 skill：按 CONTRIBUTING.md 映射表需重跑 **eval 1–6 全部六个用例**（触及契约第 3 节落盘布局故补跑 6，触及阶段 5 自检与交付摘要故补跑 5）——**六个用例已全部跑完并通过，见下节**。

### Eval 验收（0.3.0 全案回归，2026-08-03，宿主 Claude Code）

**六个用例全部通过**，其中 M5、M6 是首次拿到实测结果（此前长期为「⏳ 待跑」）：

| 用例 | 结果 | 关键证据 |
| --- | --- | --- |
| 1 | 6/6 | 三个表现性任务各具完整 GRASPS 六要素，情境显式声明「教材从未讲过」；rubric 维度取自学科理解（如「无解情形的处理」）而非通用作文项，程度副词命中 0；3 条迁移目标全被带评价标准的任务覆盖 |
| 2 | 7/7 | 公式规范六项检查全 0 违规（`\(` / math 代码块 / `pmatrix` / 公式内中文 / 中文紧邻 `$` 无空格 / `\text` 均为 0，`bmatrix` 统一）；`verify.py` 由判定方独立复现「全部通过」 |
| 3 | 5/5 | 四段式标题逐字一致；9 题 9 验证行；唯一 `⚠️ 需作者确认` 为开放题，符合红线 |
| 4 | 3/3 | 续写行 `▶ 续写：线性代数入门，从第 2 章继续` 逐字匹配契约第 5 节；01 章 SHA-1 中断前后均为 `678dcad0…` **逐字节一致**；术语表 13 → 24 条追加而非覆盖 |
| 5 | 8/8 | 规划 11 章实写 11 章；**全书 85 题 / 85 验证行零漏标**；阶段 5 七项自检齐全；学习目标覆盖 14/14；`99-表现性任务.md` 落盘且 TG 编号出现 0 次 |
| 6 | 6/6 | 两层结构正确；`.git` 在工作区层，首次提交信息与规范逐字一致；四个流水线文件（含新增 `99-表现性任务.md`）均未被 init 预建；宿主中立表述已落到产物 README |

**过程中发现并修复一个既有缺陷**（详见 Fixed 段第一条）：eval 5 首跑判定**不通过**——断言 4，全书 80 题中 26 题缺验证状态行。该缺陷非 0.3.0 引入，因 M5 从未运行而长期潜伏。修复后重跑对照：

| 指标 | 首跑 | 修复后重跑 |
| --- | --- | --- |
| 题目总数 | 80 | 85 |
| 带验证状态行 | 54 | **85** |
| 缺验证行 | **26（32.5%）** | **0** |
| `⚠️ 需作者确认` | **0** | **3**（开放题） |

同一学科、同一条「主 skill → chapter → exercises」三层调用链、同等规模，唯一变量是四处规范收紧。另一处印证：阶段 5 第 7 项自检**抓到了 rubric 里的 3 处软表述**（「解释可读」「主要操作」「主要方法」），即 `performance-task-rubric.md` 第 3 节所禁止的写法——新规范在产出端与审核端两侧均已生效。

**新发现的待办（未在本版处理）**：11 章中 8 章的「核心结论」写了 6–7 条，超出 `chapter-template.md` 3.5 节规定的 3–5 条，系统性偏差。成因与上述缺陷同源——模板给了数字却未给可数判据，章内自查第 4 条只问「小结三件齐全」、不问条数。建议下一版按同一思路收紧。

**两条判定局限，如实记录**：

1. **盲测性质不完整**：用例由独立子代理执行（与主会话无上下文继承），但代理具备仓库全部文件读取权限，eval 6 首跑的记录显示它自行读取过 `evals.json` 的断言。后续重跑已加禁读约束。所有关键判据（SHA-1、题目数与验证行数、公式规范、TG 编号计数）均由判定方在主会话独立脚本化复核，不依赖代理自述。
2. **三处分支未覆盖**：① 「确认，但把 X 改一下」的 gate 修改分支（本轮四次 gate 均只回「确认」）；② 阶段 5「作者要求修复不通过项」的修订回路（本轮均按「作者决定不修」处理）；③ 断言「缺验证行须被阶段 5 报为不通过项」的后半条件——因全书零漏标而无正样本触发，该兜底逻辑目前仅经代码路径推理、未经实测。

判定记录（逐条断言 + 产物证据）保存在 `evals/workspace/2026-08-03-*/`，已 gitignore 不入库。

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
