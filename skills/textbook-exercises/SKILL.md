---
name: textbook-exercises
description: Use when generating verified STEM exercises with Bloom-level tags — 示范例题（完整解题过程）、引导练习（带提示）、独立习题（附参考答案）— e.g. "出几道矩阵乘法的练习题"、"给这一章生成例题". Every computational answer is actually verified (真算核对) before output. Usually called by textbook-chapter; can run standalone. Not for 文科论述题 (v2) or exam paper assembly.
---

# textbook-exercises

为 STEM 教材生成三类题（示范例题/引导练习/独立习题），每道题带 Bloom 层级标注，**每个计算答案都经过真算验证才输出**。设计与验证规范的权威来源是 [references/exercise-design.md](references/exercise-design.md)。

## 何时不触发

- 文科论述题、案例分析题（v1 不支持；被要求时说明属 v2 范围，可改出概念辨析题替代）
- 组卷/试卷排版（本 skill 只产题目内容）
- 非 STEM 内容的一般性问答

## 两种调用模式

- **被 textbook-chapter 调用**（常规）：输入 = 契约 `{章上下文, 题目计划, 术语表}`（字段定义见 [../textbook/references/handoff-contract.md](../textbook/references/handoff-contract.md) 第 2 节）。按题目计划逐条生成，不多不少。
- **独立触发**：一轮问清 `{主题, 读者水平, 三类题各要几道, 期望 Bloom 层级分布}`（用户已说明的不重复问），术语自拟并保持内部一致；编号中的章号默认取 1，用户指定章号则从之。

## 生成流程（每道题走完 1–4 才算完成一道）

1. **设计题面**：按 [references/exercise-design.md](references/exercise-design.md) 第 4 节对应题类的要点设计，对照题目计划的主题与 Bloom 层级；层级判定标准查 [../textbook-outline/references/bloom-levels.md](../textbook-outline/references/bloom-levels.md) 第 4 节（同题多问取最高层，歧义就低不就高）。
2. **同步写完整解答**：示范例题 = 逐步推导每步一行理由；引导练习 = 提示阶梯（提示 1 方向 → 提示 2 关键步骤）+ 完整解答；独立习题 = 参考答案或含关键中间结果的解题路径。禁止先攒题后补答案。
3. **真算验证（红线，不可省略）**：按 exercise-design.md 第 2 节选验证方式——

   - 数值计算/符号推导类：写一段**与解答路径不同**的 Python（sympy/numpy）复算代码，用 Bash 实际执行，比对结果；
   - 代码题：实际运行代码核对输出；
   - 证明题：逐步核验每步依据（引用的定义/定理是否成立且已在教材前文出现）；
   - 概念辨析：核对定义来源；
   - 当前环境无法执行 Python 时：手算两遍交叉核对，验证状态注明"手算交叉核对"。
4. **处理验证结果**：复算一致 → 标 `✅ 已验证（<方式>）`；不一致 → 修题或修解答后重新验证；**连续 2 次验证失败 → 弃题换题**。确实无法机器验证且手算不可行（如开放性数值实验）→ 标 `⚠️ 需作者确认（<原因>）`，绝不假装已验证。

## 输出

- 按契约逐题给出 `{编号, 类型, 题干, 解答或提示, Bloom层级, 验证状态}`；
- 正文格式遵循 exercise-design.md 第 6 节（编号规则 `例 N-M` / `习题 N-M`，引导练习计入"例"序列加后缀）；
- **验证用的复算代码随题附上**（放在"验证"行后的代码块中），供作者复查；
- 术语用词严格对照传入的术语表；独立触发时保持自拟术语的内部一致。

## 纪律（违反任何一条即返工）

- 绝不输出未验证的计算答案——"应该没错"不是验证；
- 开放题给参考要点并标注"开放题"，不编造标准答案；
- 每题必有 Bloom 标注，漏标即不完整；
- "留给读者作为练习"式悬空 = 违规（exercise-design.md 第 3 节第 6 条）；
- 出题偏离题目计划的主题或层级时，须在输出中注明偏离原因（如"该主题在应用层无自然题型，改为分析层"），由调用方决定是否接受。
