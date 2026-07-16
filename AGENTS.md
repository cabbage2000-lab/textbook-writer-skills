# AGENTS.md

本文件是 Codex CLI 在本仓库中的项目级指令入口，作用与 `CLAUDE.md` 面向 Claude Code 平行——`CLAUDE.md` 面向"改 skill 时的工程约束"，本文件面向"如何在本仓库启动并运行这套 skill"。

## 这是什么

本仓库是一套以 UbD 逆向设计为内核的 STEM 教材写作 skill 组合：1 个主 skill（`textbook`）编排 3 个子 skill，驱动"教学定位 → UbD 预期结果 gate → 章节树 gate → 逐章写作 → 审核定稿"五阶段流程；另有 1 个独立辅助 skill（`textbook-init`）负责动笔前的工作目录规划，不入调度链。5 个 skill 是一个整体组合，跨 skill 以相对路径互相引用，需整体使用，不得只启用其中一个而忽略其余。

## 触发路由：用户想做什么，就读哪个 SKILL.md

Codex 没有 Claude Code 的 plugin/Skill 工具机制，不会自动加载 skill 的 frontmatter。收到以下意图时，直接读取对应文件并严格遵循其指令执行：

| 用户意图（触发词示例） | 读取并遵循 |
| --- | --- |
| 写教材 / 写一本…教材 / 编写课程讲义 / 系统教材 | `skills/textbook/SKILL.md` |
| 设计教材大纲 / 教材规划 / 课程体系设计 | `skills/textbook-outline/SKILL.md` |
| 写第 X 章 / 按大纲写这一章 | `skills/textbook-chapter/SKILL.md` |
| 出几道题 / 给这一章生成例题 | `skills/textbook-exercises/SKILL.md` |
| 初始化教材项目 / 创建或规划教材工作目录 | `skills/textbook-init/SKILL.md` |

## 跨 skill 调用桥接

各 SKILL.md 内部已写明"使用 Skill 工具调用对方 skill；若 Skill 工具不可用或未注册，直接读取对方 SKILL.md 并严格遵循其指令执行"的降级路径（例：`skills/textbook/SKILL.md` 第 42、56 行，`skills/textbook-chapter/SKILL.md` 第 33 行）。Codex 没有 Skill 工具，天然命中这条降级分支：主 skill 调子 skill、子 skill 相互调用时，都直接读取被调用方的 SKILL.md 并遵循执行，无需任何额外适配。

## 三条红线（细节以对应 SKILL.md / `handoff-contract.md` 为准，此处只提醒不重述）

1. **双 gate 必须停**：阶段 2（UbD 五件套）、阶段 3（章节树+梯度报告）必须等作者明确确认才能推进，任何"流程优化"都不得绕过或自动确认。
2. **真算验证，不许假装**：STEM 例题与习题的计算类答案必须实际复算核对后才能输出；确实验证不了的，必须明确标注 `⚠️ 需作者确认`，绝不能在没有验证的情况下假装已验证。
3. **状态单一写者**：`.progress.json` 只由 `textbook`（主 skill）读写，子 skill（`textbook-outline`、`textbook-chapter`、`textbook-exercises`）一律不碰这个文件。

契约、落盘布局、状态机的完整权威定义见 [skills/textbook/references/handoff-contract.md](skills/textbook/references/handoff-contract.md)。
