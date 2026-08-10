# 行为测试基线（evals）

[evals.json](evals.json) 把 README 里程碑 **M2–M7 的验收场景**固化为可重复执行的用例。结构校验（CI 里跑的 `validate_skills.py`）只能保证 skill 文件形态正确；skill 的真正质量在**行为**——gate 停不停、题目验没验、中断续不续——这些只能靠真实运行来检验，本目录就是这些检验的单一事实来源。

## 用例一览

| ID | 用例 | 里程碑 | 被测 skill | 预计耗时 |
| --- | ------ | ------ | ----------- | -------- |
| 1 | outline-double-gate | M2 | textbook-outline | ~10 分钟（含 2 次人工确认） |
| 2 | exercises-verified-generation | M3 | textbook-exercises | ~5 分钟（全自动） |
| 3 | chapter-four-part-structure | M3 | textbook-chapter | ~15 分钟（全自动） |
| 4 | e2e-resume-after-interrupt | M4 | textbook | ~40-60 分钟（只测中断-续写机制：写 1 章→中断→续 2 章即可判定，不写完全书） |
| 5 | second-subject-rerun | M5 | textbook | 数小时（本用例是「整本书写完 + 阶段 5 自检 + 交付摘要」的验收责任方） |
| 6 | init-workspace-scaffold | M6 | textbook-init | ~5 分钟（含 1 次人工确认） |
| 7 | humanities-outline-profile-routing | M7 | textbook-outline | ~10 分钟（含 2 次人工确认） |
| 8 | humanities-chapter-citation-discipline | M7 | textbook-chapter | ~15 分钟（全自动） |
| 9 | economics-outline-profile-routing | M8 | textbook-outline | ~10 分钟（含 2 次人工确认） |
| 10 | economics-chapter-mixed-verification | M8 | textbook-chapter | ~15 分钟（全自动） |

用例 7、8 走 `humanities` 学科档案，验证同一套内核在非 STEM 学科下的行为；用例 9、10 走 `economics` 档案，验证**复算与核对来源两类手段在同一本教材里并存**——这是该档案区别于前两份的核心，因此用例 9 有一条断言专查题型分布是否同时覆盖两类，用例 10 的 prompt 硬性要求含一道真实统计数据题（不要求它就可能整章只出可复算的模型题，验不到新增的那半边）。判定时**不要用内容质量代替形式项**（见本文末「增改用例」）。

## 怎么跑

1. 按仓库 README「快速开始」完成任一安装方式（本仓库内用软链方式）。
2. 新开一个会话，输入用例的 `prompt` 原文。
3. 会话结束后，对照该用例的 `assertions` 逐条判定通过/不通过。
4. 运行产物（教材目录、会话记录、判定结果）放进 `evals/workspace/<日期>-eval-<ID>/`——该目录已 gitignore，不入库；判定结论回写到仓库 README 的里程碑表。

**在哪个宿主跑**：**Claude Code 是基线宿主**——README 里程碑表已记录的通过结果全部跑自它。同一套用例可以在 Codex、WorkBuddy 上原样复跑（prompt 一字不改，装法见仓库 README 的宿主目录表），判定口径完全相同：assertions 判的是行为红线（gate 停没停、题目验没验、续点定位对不对、落盘文件齐不齐），不是逐字文本，措辞与题目内容因宿主而异属正常。判定记录里必须写明**宿主与版本**，否则复跑结果无法归因。跨宿主不一致时先定位是谁错，别默认第二宿主错——基线宿主同样可能是偏离的那一方。

**用例 6 必须在本仓库之外运行**（如 `/tmp/eval6-<日期>/`），跑完再把产物 `cp -a` 回 `evals/workspace/` 存档。原因：`textbook-init` 按 `workspace-layout.md` 第 3 节第 1 条先做 git 判重——`git rev-parse --show-toplevel` 有输出就跳过 `git init`。在 `evals/workspace/` 里跑，判重必然命中被测仓库，skill 会正确地跳过 git 初始化，导致「git 仓库初始化于工作区根且有首次提交」这条断言**永远不可能通过**。这是运行位置与用例定义的冲突，不是 skill 缺陷，**不要为此修改断言**（2026-08-03 首跑 M6 时踩过一次，判定记录见 `workspace/2026-08-03-eval-6-rerun/judgment.md`）。

改动任何 SKILL.md 或 references 后，**至少重跑受影响 skill 的对应用例**（见 CONTRIBUTING.md 的映射表）。

## 判定纪律

- assertions 是客观断言：逐条给出 通过/不通过 + 证据（引用产物文件的具体位置），不许"总体感觉不错"；
- 任何一条不通过就是用例不通过——修 skill 后重跑，不许改 assertions 迁就产出（确需调整断言时单独提 PR 说明理由）；
- 用例 4 的中断步骤是硬要求：不真中断就没有验证"中断可续"；
- **短链路用例通过 ≠ 长链路没问题**：用例 2/3 是单 skill 直接调用，用例 5 是「主 skill → chapter → exercises」三层调用的 10 章长链路。2026-08-03 的「26/80 题缺验证状态行」缺陷只在用例 5 暴露，2/3 完全正常——涉及出题纪律、逐章一致性一类会沿调用链衰减的改动，别用 2/3 的通过替代 5 的验收；
- 用例 4/5 的验收职责按 M4/M5 拆分，不重叠：4 只验证「中断-续写机制」（写 1 章即中断，续写 1 章即可判定，无需写完全书），「整本书写完 + 阶段 5 自检 + 交付摘要」的验收全部下沉到 5——这样日常迭代改动契约时不必每次都写完一整本书才能判定。若改动专门涉及阶段 5 自检或交付摘要逻辑，额外补跑用例 5。

## 增改用例

新场景（如新增学科档案、同一档案换学科复跑）按 evals.json 现有 schema 追加：`id` 递增、`name` 用描述性 kebab-case、`assertions` 写可判定的客观断言。用例定义入库，运行产物不入库。

新增一份**学科档案**时，断言要锚定**形式性可判定项**——每题是否有验证状态行、题目数是否等于验证行数、开放题是否附参考要点、四段标题是否与档案第 4 节逐字一致、题型是否都在档案题型集内——而不是"内容写得好不好"。学科越偏论述，内容质量越难客观判定，把断言压在形式项上，第三道防线才不会在新学科上失效。
