---
name: write-textbook
description: Use when the user wants to write a complete multi-chapter textbook or systematic course material with exercises — e.g. "写教材"、"写一本教材"、"编写课程讲义"、"系统教材"、"textbook". Orchestrates a five-stage UbD-driven pipeline (教学定位 → UbD 预期结果 gate → 章节树 gate → 逐章写作 → 审核定稿) with resumable progress via .progress.json. Not for single tutorials (use tutorial-writer), single chapters (use write-textbook-chapter), or exercise-only requests (use generate-textbook-exercises).
---

# write-textbook

写教材的主 skill（orchestrator）：驱动五阶段流程，管理 `.progress.json` 状态实现中断可续，在阶段间传递交接契约，最终交付一本有主线、有梯度、可评估的多章节 Markdown 教材。契约、落盘布局、状态机的权威定义见 [references/handoff-contract.md](references/handoff-contract.md)（下称"契约文档"）。

## 何时不触发

- 单篇教程/图文教程（用 tutorial-writer）
- 只写一章或一篇深度文章（用 write-textbook-chapter）
- 只要例题/习题（用 generate-textbook-exercises）
- 只做大纲不写正文（直接用 design-textbook-outline）

## 工作流总览

| 阶段 | 名称 | 执行者 | 产出 | Gate? |
| ------ | ------ | -------- | ------ | ------- |
| 1 | 教学定位确认 | design-textbook-outline | 学科/读者起点/深度/篇幅 → 00-教材设计.md | 否（一轮提问） |
| 2 | UbD 预期结果设计 | design-textbook-outline | UbD 五件套 | **是（核心 gate）** |
| 3 | 评估与章节设计 | design-textbook-outline | 章节树+例题计划+梯度报告+表现性任务 | 是（次要 gate） |
| 4 | 章节正文编写 | write-textbook-chapter（逐章） | NN-章.md × N + 术语表增量 | 否 |
| 5 | 审核定稿 | 本 skill | 自检报告 + 交付摘要 | 否 |

gate 之外的阶段只打印一行进度（格式见契约文档第 5 节），不打断作者。

## 启动与重入（每次触发的第一件事）

1. **确定教材项目目录**：用户指定则用之；未指定则询问一次（默认 `./<教材名>/`）。
2. **找 `.progress.json`**：

   - 不存在 → 全新项目：确认教材名 → 建目录 → 初始化 `.progress.json`（schema 见契约文档第 4 节，`current_stage=1`，gates 全 false）→ 从阶段 1 开始；
   - 存在 → 按契约文档第 4 节**重入规则表**定位续点，打印续写行：阶段 4 用 `▶ 续写：<教材名>，从第 N 章继续`，其余阶段用 `▶ 续写：<教材名>，从阶段 N 继续`。特别地：`current_stage=2/3` 且对应 gate 未确认时，从 `00-教材设计.md` 读出已有产出（阶段 2 为五件套、阶段 3 为章节树/例题习题计划/梯度报告/表现性任务四项）**重新呈现并等确认**，不推倒重做；作者提出修改时委托 design-textbook-outline 执行修改与再确认循环。
3. **状态纪律**：`.progress.json` 只由本 skill 读写（子 skill 一律不碰）；每完成一个阶段、每完成一章**立即更新写盘**，绝不批量延迟。

## 阶段 1–3：委托 design-textbook-outline

打印 `▶ 阶段 1/5：教学定位确认`（阶段 2、3 进入时同格式）。

使用 Skill 工具调用 `design-textbook-outline`（传入 `{教材项目目录, 教材名}`）；若 Skill 工具不可用或未注册，直接读取 [../design-textbook-outline/SKILL.md](../design-textbook-outline/SKILL.md) 并严格遵循其指令执行。

- 其内部两个 gate 就是本流程的 gate——**gate 由该子 skill 面向作者执行，本 skill 绝不越过未确认的 gate 推进状态**；
- 阶段 2 确认后：置 `gates.stage2_ubd_confirmed=true`、`current_stage=3`，写盘；
- 阶段 3 确认后：置 `gates.stage3_outline_confirmed=true`、`current_stage=4`、`chapters.total=章节树章数`、`chapters.next=1`，写盘。

## 阶段 4：逐章循环

打印 `▶ 阶段 4/5：章节正文编写`。

对 章号 N 从 `chapters.next` 到 `chapters.total` 逐章执行（严格顺序，前章完成才写后章）：

1. **提取该章大纲切片**：从 `00-教材设计.md` 的「## 三、章节树与梯度规划（已确认）」取该章的章节树条目 + 例题习题计划；
2. **读跨章载体**：术语表.md 当前版 + 前一章文件的「## 本章小结」全节（N=1 时前章小结为空）；
3. **组装输入契约调用 write-textbook-chapter**：`{章号, 章标题, 该章大纲切片, UbD五件套, 术语表, 前章小结}`（五件套从「## 二、UbD 五件套（已确认）」提取 `{大概念[], 持久理解[], 核心问题[]}`）。调用方式同上：Skill 工具优先，降级读 [../write-textbook-chapter/SKILL.md](../write-textbook-chapter/SKILL.md)；
4. **收输出契约** `{章文件路径, 新增术语[], Bloom标注回写[]}`：新增术语追加进术语表.md；Bloom 标注回写记入 `00-教材设计.md` 该章例题习题计划条目旁的"实际"标注（与"计划"并排，供阶段 5 对比）；
5. **更新状态**：`chapters.done` 加入 N、`chapters.next=N+1`，写盘 `.progress.json`。

全部章完成后置 `current_stage=5`，写盘。任何一章中途中断，重入时从 `chapters.next` 无缝继续，已完成章不重写。

## 阶段 5：审核定稿（自检清单，非 gate，必须全跑）

打印 `▶ 阶段 5/5：审核定稿`。逐项检查并输出报告，每项给出：通过/不通过 + 具体位置 + 修改建议。

1. **章节对齐走查**：逐章读「## 本章小结」的"与持久理解的呼应"，对照 `00-教材设计.md` 的承载计划——每章至少承载一条持久理解，每条持久理解至少被一章实际承载；
2. **Bloom 梯度复核（看实际不看计划）**：用各章"实际"标注重算层级×章节矩阵，按 [../design-textbook-outline/references/bloom-levels.md](../design-textbook-outline/references/bloom-levels.md) 第 5 节三条规则复核，输出第 6 节格式的报告；
3. **术语一致性**：对照术语表.md 抽查各章（每章至少查引言与小结两处）用词与符号是否一致，发现不一致列出位置；
4. **例题验证残留**：全书搜索 `⚠️ 需作者确认`，汇总成清单呈现——带此标注是合规的（红线允许"明确标注不能验证"），但必须让作者全部看见；
5. **循序渐进走查**：逐章检查引言是否衔接前章小结、是否使用了后文才定义的概念（前置知识跳跃）。

报告完毕后：不通过项由**作者决定修不修**；作者要求修 → 定位到章，重新组装该章输入契约调用 write-textbook-chapter 修订（修订后相关项复查）。全部处理完写盘 `stage5_passed`：无遗留不通过项（全过或均已修复）置 `true`；作者决定不修的不通过项仍存在置 `false`，并在交付摘要中列明遗留项。

## 交付

输出交付摘要：章数 / 三类题总数 / 已验证题数 / `⚠️ 需作者确认` 条数 / 梯度复核结论 / 未修复项清单（如有）。

交付物为教材项目完整目录（布局见契约文档第 3 节）：`00-教材设计.md`、`NN-<章标题>.md × N`、`术语表.md`、`.progress.json`。

**边界说明**（须向作者说明）：定稿指文字与结构层面完成；若正文含人工截图标注块，需作者按标注自行补图后才算可发布。
