---
name: write-textbook-chapter
description: Use when writing one textbook chapter following the fixed 四段式 structure (概念讲解 → 示范例题 → 引导练习 → 独立习题) from an outline slice plus UbD anchor — e.g. "写第三章"、"按大纲写这一章". Usually orchestrated by write-textbook; can run standalone for a deep-dive technical article with worked examples. Not for designing outlines or whole-book orchestration.
---

# write-textbook-chapter

按四段式模板写一章教材正文：概念讲解 → 示范例题 → 引导练习 → 独立习题，外加章引言与本章小结。章结构的权威来源是 [references/chapter-template.md](references/chapter-template.md)，文体规范是 [references/writing-style.md](references/writing-style.md)。

## 何时不触发

- 设计教材大纲（用 design-textbook-outline）
- 全书多章调度（用 write-textbook）
- 只要题目不要正文（用 generate-textbook-exercises）

## 两种调用模式

- **被 write-textbook 调度**（常规）：输入 = 契约 `{章号, 章标题, 该章大纲切片, UbD五件套, 术语表, 前章小结}`（字段定义见 [../write-textbook/references/handoff-contract.md](../write-textbook/references/handoff-contract.md) 第 2 节；第 1 章的前章小结为空）。
- **独立触发**（写深度技术文章）：一轮问清 `{主题, 读者水平, 篇幅}`；自拟**轻量版五件套**（只取两件）——1 条持久理解（"读者将理解：……"句式）+ 1 个核心问题，向用户展示后开写（不设 gate，展示即可）；无外部术语表时自建（格式同契约文档第 3 节的术语表列定义），无前章小结则引言直接从动机切入。

## 上下文隔离纪律（不可违反）

只接收上述输入契约，**不读入其他章正文**。跨章一致性靠三个轻量载体：术语表、前章小结、UbD 五件套（契约文档第 6 节）。"顺便读一下前几章找感觉"是违规——上下文膨胀会让长教材写不完。

## 写作流程

1. **打印进度**：被调度时打印 `▶ 第 N/M 章：<章标题>`；独立触发时打印章标题。
2. **起草章骨架**：按 [references/chapter-template.md](references/chapter-template.md) 第 2 节的完整模板起草——

   - 引言：从前章小结的核心结论衔接进入，呼应五件套中的一条核心问题，先"为什么"再"学什么"；
   - `## N.1 概念讲解`：按大纲切片中该章定位与承载的持久理解展开，每个概念走"动机 → 定义 → 直观解释 → 关系"链条；
   - 全程遵循 [references/writing-style.md](references/writing-style.md)：叙事散文、认知负荷控制（一段一个新概念）、配图双轨（抽象概念用 mermaid/SVG，纯概念章至少一图）、措辞禁忌（禁"显然/易得"跳步）、中文排版。
3. **生成三类题**：使用 Skill 工具调用 `generate-textbook-exercises`（传入契约 `{章上下文, 题目计划, 术语表}`，其中章上下文的概念清单与学习目标从大纲切片提取）；若 Skill 工具不可用或未注册，直接读取 [../generate-textbook-exercises/SKILL.md](../generate-textbook-exercises/SKILL.md) 并严格遵循其指令执行。将返回题目按类型放入 `## N.2 示范例题`、`## N.3 引导练习`、`## N.4 独立习题`，保持验证状态与复算代码块原样，不改动已验证解答的数值。
4. **写本章小结**：按 chapter-template.md 3.5 节固定三件——核心结论（3–5 条，面向下一章作者）、与持久理解的呼应（一句话说明本章推进了哪条）、下一章预告（1 句）。
5. **落盘与自查**：写入 `NN-<章标题>.md`（NN 为两位章号）；按 chapter-template.md 第 5 节章内自查清单逐项自查，不过的当场修正后再交付。

## 输出

回报契约 `{章文件路径, 新增术语[], Bloom标注回写[]}`：

- **新增术语**：本章首次引入的概念，按术语表格式（`| 术语（中文） | 英文 | 定义/约定 | 首次出现章节 |`）写好词条——调用方负责追加进术语表.md，独立触发时直接更新自建术语表；
- **Bloom标注回写**：本章每道题的 `{题目编号, 类型, Bloom层级}`，供主 skill 阶段 5 复核实际梯度；
- 撰写中若发现大纲切片的题目计划有明显缺口（如某学习目标无题覆盖），在回报中附建议，由调用方/作者决定，不擅自加题。

## 真实性约束

- 概念讲解中的事实性内容基于大纲切片与已确认的教材设计，不虚构学科结论；拿不准的表述从保守（"通常""在本书讨论的范围内"），或在回报中注明请作者确认；
- 例题验证责任在 generate-textbook-exercises，本 skill **不得改动已验证解答的数值**；如需改写题目文字表述，改后必须请 generate-textbook-exercises 重新验证。
