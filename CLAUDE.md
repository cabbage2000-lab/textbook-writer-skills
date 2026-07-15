# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库性质

这是一个 Claude Code skills/plugin 仓库：产品本身是 `skills/` 下的 4 个 Markdown skill（"给模型看的程序"），没有传统应用代码。**改一行指令就可能改变 skill 的运行行为**，而结构校验和单元测试只能保证文件形态正确，行为质量必须靠 evals 真实运行来检验——这是本仓库三层防线设计的出发点。Python 只出现在质量保障脚本中（零第三方依赖，3.10+ 标准库）。

领域：以 UbD 逆向设计为内核的 STEM 教材写作流水线。设计依据源自 PRD 与前期调研（本地 `docs/` 目录留存，不纳入版本库）；版本库内可查的架构决策摘要见 [docs/adr/](docs/adr/README.md)。

## 常用命令

```bash
python3 scripts/validate_skills.py       # ① 结构校验（skills 内容 + plugin 清单一致性 + 仓库健康）
python3 -m unittest discover -s tests    # ② 单元测试（校验逻辑本身）

# 单跑一个测试
python3 -m unittest tests.test_validate_skills.ValidateSkillsTest.test_valid_skill_passes

# 本地试跑 skill：软链为项目级 skills，改动即时生效（.claude/ 已 gitignore）
mkdir -p .claude && ln -s ../skills .claude/skills
```

③ 第三道防线是行为测试（evals），**无法自动化**：在新开的 Claude Code 会话中输入 [evals/evals.json](evals/evals.json) 用例的 `prompt` 原文真实运行，对照 `assertions` 逐条客观判定（通过/不通过 + 产物证据），任何一条不通过即用例不通过，不许改断言迁就产出。运行产物放 `evals/workspace/`（已 gitignore，用例定义入库、运行产物不入库）。

## 架构

1 个主 skill + 3 个子 skill 构成整体组合（跨 skill 以 `../<skill-name>/references/xxx.md` 相对路径互引，需整体安装，不得引入仓库外依赖）：

```text
write-textbook（orchestrator）        五阶段调度 + .progress.json 状态机（中断可续）
  ├─ design-textbook-outline          阶段 1–3：教学定位 → UbD 五件套(核心 gate) → 章节树+梯度(次要 gate)
  ├─ write-textbook-chapter           阶段 4：四段式单章写作（概念讲解→示范例题→引导练习→独立习题）
  └─ generate-textbook-exercises      被单章 skill 调用：三类题生成 + 真算验证
```

**[skills/write-textbook/references/handoff-contract.md](skills/write-textbook/references/handoff-contract.md) 是全项目唯一权威定义**——阶段间交接契约、教材项目落盘布局、`.progress.json` 状态机与重入规则、进度打印/gate 停点格式、上下文隔离原则，全部以它为准。4 个 SKILL.md 一律引用它，不得各自重复定义；契约字段名上下游**逐字一致**，同义改写（如"章节树"写成"章节列表"）即破坏契约。

理解运行时行为的关键机制（详见契约文档）：

- **双 gate**：阶段 2（UbD 五件套）、阶段 3（章节树+梯度报告）必须作者明确确认才放行；"确认，但把 X 改一下"按修改分支处理，修改优先于确认；
- **状态机**：`.progress.json` 只由主 skill 读写（子 skill 一律不碰），每完成一阶段/一章立即写盘；重入按契约文档第 4 节规则表定位续点；
- **上下文隔离**：单章写作不读其他章正文，跨章一致性只靠术语表、前章小结、UbD 五件套三个轻量载体传递——这是 10+ 章长教材不爆上下文的根本保证；
- **子 skill 调用方式**：Skill 工具优先，不可用时降级为直接读对方 SKILL.md 并遵循执行。

## 改动影响半径与必跑 evals

影响半径从大到小：handoff-contract.md（牵动全部 4 个 skill）＞ SKILL.md 的调用契约段（牵动调用方与被调用方两侧）＞ SKILL.md 流程段 / references（只影响本 skill）＞ scripts/tests/docs（不影响 skill 行为，CI 绿即可）。

| 改动位置 | 必跑用例 |
| -------- | -------- |
| write-textbook（含 handoff-contract.md） | 1, 2, 3, 4 |
| design-textbook-outline | 1 |
| write-textbook-chapter | 2, 3 |
| generate-textbook-exercises | 2 |

## 校验脚本强制的硬约束（改 skill 前先知道）

- SKILL.md ≤ 500 行——超限把细节下沉到 `references/`（渐进披露：SKILL.md 只放工作流骨架，并明确指路"何时读哪个文件"）；
- frontmatter：`name` 与目录名一致；`description` 50–1024 字符，承担全部触发职责（写清"何时用 + 干什么 + 何时不用"，带中文触发词示例）；仅允许白名单字段（name/description/version/license/allowed-tools/compatibility/metadata），其余会被静默忽略；
- `skills/` 下所有 .md 禁止占位符词（TBD、TODO、FIXME、XXX、待补充、占位）；
- `references/` 下每个 .md ≥ 500 字节；SKILL.md 引用的 references 路径（含跨 skill）必须真实存在；
- `plugin.json` 与 `marketplace.json` 的 name/version/description/license 必须一致——发版时两处同步升版；
- `.gitignore` 不得忽略 `.claude-plugin`（分发清单必须入库）。

写给模型的指令尽量讲清动机（"上下文膨胀会让长教材写不完"），而不是堆砌大写的 MUST。

## 红线（源自 PRD，任何改动不得突破）

- STEM 例题答案必须真算验证，验证不了的明确标注 `⚠️ 需作者确认`，绝不假装已验证；
- 阶段 2/3 双 gate 必须作者明确确认才放行，任何"优化"不得绕过；
- 单章写作只接收输入契约，不读其他章正文；
- `.progress.json` 只由主 skill 读写；
- 交付的 .md 不含占位符。

## 修改 skill 的完成标准（DoD）

结构校验通过 → 单元测试全绿 → 按上表重跑受影响的 evals 用例 → 更新 [CHANGELOG.md](CHANGELOG.md) 的 Unreleased 段 → 行为语义有变化时（gate 规则、契约字段、验证纪律）同步更新 README 与受影响 skill 的交叉引用。

新增 skill 清单、发版流程（版本语义：MAJOR = 契约或落盘格式不兼容变更）见 [CONTRIBUTING.md](CONTRIBUTING.md)。
