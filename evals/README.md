# 行为测试基线（evals）

[evals.json](evals.json) 把 README 里程碑 **M2–M5 的验收场景**固化为可重复执行的用例。结构校验（CI 里跑的 `validate_skills.py`）只能保证 skill 文件形态正确；skill 的真正质量在**行为**——gate 停不停、题目验没验、中断续不续——这些只能靠真实运行来检验，本目录就是这些检验的单一事实来源。

## 用例一览

| ID | 用例 | 里程碑 | 被测 skill | 预计耗时 |
| --- | ------ | ------ | ----------- | -------- |
| 1 | outline-double-gate | M2 | textbook-outline | ~10 分钟（含 2 次人工确认） |
| 2 | exercises-verified-generation | M3 | textbook-exercises | ~5 分钟（全自动） |
| 3 | chapter-four-part-structure | M3 | textbook-chapter | ~15 分钟（全自动） |
| 4 | e2e-resume-after-interrupt | M4 | textbook | 数小时（含人为中断步骤） |
| 5 | second-subject-rerun | M5 | textbook | 数小时 |

## 怎么跑

1. 按仓库 README「安装与使用」完成任一安装方式（本仓库内用软链方式）。
2. 新开一个 Claude Code 会话，输入用例的 `prompt` 原文。
3. 会话结束后，对照该用例的 `assertions` 逐条判定通过/不通过。
4. 运行产物（教材目录、会话记录、判定结果）放进 `evals/workspace/<日期>-eval-<ID>/`——该目录已 gitignore，不入库；判定结论回写到仓库 README 的里程碑表。

改动任何 SKILL.md 或 references 后，**至少重跑受影响 skill 的对应用例**（见 CONTRIBUTING.md 的映射表）。

## 判定纪律

- assertions 是客观断言：逐条给出 通过/不通过 + 证据（引用产物文件的具体位置），不许"总体感觉不错"；
- 任何一条不通过就是用例不通过——修 skill 后重跑，不许改 assertions 迁就产出（确需调整断言时单独提 PR 说明理由）；
- 用例 4 的中断步骤是硬要求：不真中断就没有验证"中断可续"。

## 增改用例

新场景（如 v2 文科支持、新学科复跑）按 evals.json 现有 schema 追加：`id` 递增、`name` 用描述性 kebab-case、`assertions` 写可判定的客观断言。用例定义入库，运行产物不入库。
