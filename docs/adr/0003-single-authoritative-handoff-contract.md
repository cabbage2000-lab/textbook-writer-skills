# ADR 0003:handoff-contract.md 是契约与状态机的唯一权威定义

## 状态

已接受。

## 背景

拆分([ADR 0001](0001-skill-composition-over-monolith.md))之后,4 个 skill 之间存在七道交接:阶段 1→2、2→3、3→4 的产物传递,主 skill 与单章 skill 的双向调用,单章 skill 与例题 skill 的双向调用。

skill 是"给模型看的程序",契约靠字面匹配生效。如果契约散落在各 SKILL.md 里各自定义,会出现两类漂移:**字段名同义改写**(上游写"章节树"、下游写"章节列表",人读无碍,模型按字面对接即断链)和**规则不同步**(gate 判定措辞、落盘标题、重入规则改了一处漏了三处)。

## 决策

- [skills/write-textbook/references/handoff-contract.md](../../skills/write-textbook/references/handoff-contract.md) 是全项目唯一权威定义,覆盖五块:阶段间交接契约、教材项目落盘布局、`.progress.json` 状态机与重入规则、进度打印与 gate 停点格式、上下文隔离原则;
- 4 个 SKILL.md 一律引用该文件,不得各自复述或改写字段定义;
- 契约字段名上下游**逐字一致**,同义改写即视为破坏契约;
- 标注"已确认"的产出必须经过作者 gate 确认后才可向下游传递;
- `00-教材设计.md` 的二级标题是固定锚点(重入与阶段 5 走查按标题定位),不随 gate 状态改名。

## 后果

该文件的改动影响半径全项目最大:牵动全部 4 个 skill,按 [CONTRIBUTING.md](../../CONTRIBUTING.md) 必须全量重跑 evals 用例 1–4;契约字段或落盘格式的不兼容变更即 MAJOR 版本(老教材项目的 `.progress.json` 与落盘标题不能续用)。

收益是跨 skill 行为的一致性有了单一事实来源:review 契约类改动只需盯一个文件,新增 skill 若要纳入调度链,必须先在该文件定义其输入/输出契约,再写自己的 SKILL.md。
