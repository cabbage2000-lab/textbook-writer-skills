# 架构决策记录(ADR)

本目录记录本仓库影响深远、且曾有真实替代方案的架构决策:每篇回答"当时面对什么问题、为什么这么选、付出了什么代价"。[CLAUDE.md](../../CLAUDE.md) 和 [CONTRIBUTING.md](../../CONTRIBUTING.md) 描述**现状是什么**,ADR 补充**为什么是这样**——改动某项机制前先读对应 ADR,避免无意中推翻当初的取舍。

格式沿用 Michael Nygard 的四段式(状态 / 背景 / 决策 / 后果),文件按 `NNNN-英文短标题.md` 编号递增。已接受的 ADR 不改写历史:决策被推翻时新增一篇记录新决策,并在旧篇「状态」标注"已被 ADR NNNN 取代"。

## 索引

| 编号 | 标题 | 一句话 |
| ---- | ---- | ------ |
| [0001](0001-skill-composition-over-monolith.md) | 拆成 1 主 + 3 子的 skill 组合 | 否决"单 skill + 增量更新",用拆分从根上解决长教材上下文与复用问题 |
| [0002](0002-ubd-backward-design-with-dual-gates.md) | UbD 逆向设计内核与双 gate | 核心 gate 从"大纲"前移到"预期结果",教学设计驱动而非长文生成 |
| [0003](0003-single-authoritative-handoff-contract.md) | handoff-contract.md 契约单源 | 契约、落盘布局、状态机只在一处定义,字段名上下游逐字一致 |
| [0004](0004-context-isolation-for-chapters.md) | 单章写作的上下文隔离 | 跨章一致性只靠术语表、前章小结、UbD 五件套三个轻量载体 |
| [0005](0005-progress-state-machine-single-writer.md) | .progress.json 单一写者 | 状态只由主 skill 读写、逐阶段/逐章立即落盘,支撑中断可续 |
| [0006](0006-verified-computation-for-exercises.md) | 例题真算验证 | 验证状态二值化:✅ 已验证 / ⚠️ 需作者确认,无第三种 |
| [0007](0007-three-layer-quality-defense.md) | 三层质量防线 | 结构校验、单元测试进 CI;行为 evals 人工跑,不许改断言迁就产出 |
| [0008](0008-plugin-layout-and-distribution.md) | plugin 布局与整体分发 | 顶层 skills/ + 双清单入库,四个 skill 整体安装不可拆分 |
| [0009](0009-unified-skill-naming.md) | skill 命名统一为 textbook- 名词族 | 主 skill 名即公共前缀,补全聚族;动作语义由 description 承担,plugin 名不变 |

## 何时新增一篇 ADR

满足任一条即值得记录:推翻或修订上表中的既有决策;引入新的对外契约或落盘格式(牵动 MAJOR 版本语义);在多个可行方案中做出难以逆转的取舍。日常的指令措辞修正、references 内容补充不需要 ADR,走 [CHANGELOG](../../CHANGELOG.md) 即可。

新增时:取下一个顺延编号,遵循四段式,在「背景」写清被否决的替代方案,在「后果」写清代价与对未来提案的约束;完成后更新本索引。
