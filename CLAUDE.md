# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库性质

这是一个 agent skills/plugin 仓库（目标宿主：Claude Code / Codex / WorkBuddy）：产品本身是 `skills/` 下的 5 个 Markdown skill（"给模型看的程序"），没有传统应用代码。**改一行指令就可能改变 skill 的运行行为**，而结构校验和单元测试只能保证文件形态正确，行为质量必须靠 evals 真实运行来检验——这是本仓库三层防线设计的出发点。Python 只出现在质量保障脚本中（零第三方依赖，3.10+ 标准库）。

领域：以 UbD 逆向设计为内核的教材写作流水线（学科无关内核 + 可插拔学科档案；内置 `stem`、`humanities`、`economics` 三份档案，`humanities` 的大纲与单章两条路径已由 eval 7、8 实跑验证，`economics` 的 eval 9、10 待跑）。设计依据源自 PRD 与前期调研（本地 `docs/` 目录留存，不纳入版本库）；版本库内可查的架构决策摘要见 [docs/adr/](docs/adr/README.md)。

## 常用命令

```bash
python3 scripts/validate_skills.py       # ① 结构校验（skills 内容 + plugin 清单一致性 + 仓库健康）
python3 -m unittest discover -s tests    # ② 单元测试（校验逻辑本身）

# 单跑一个测试
python3 -m unittest tests.test_validate_skills.ValidateSkillsTest.test_valid_skill_passes

# 本地试跑 skill：软链为项目级 skills，改动即时生效（.claude/ 已 gitignore）
mkdir -p .claude && ln -s ../skills .claude/skills
```

③ 第三道防线是行为测试（evals），**无法自动化**：在新开的会话中（Claude Code 为基线宿主，跨宿主复跑口径见 [evals/README.md](evals/README.md)）输入 [evals/evals.json](evals/evals.json) 用例的 `prompt` 原文真实运行，对照 `assertions` 逐条客观判定（通过/不通过 + 产物证据），任何一条不通过即用例不通过，不许改断言迁就产出。运行产物放 `evals/workspace/`（已 gitignore，用例定义入库、运行产物不入库）。

## 架构

1 个主 skill + 3 个子 skill + 1 个独立辅助 skill 构成整体组合（跨 skill 以 `../<skill-name>/references/xxx.md` 相对路径互引，需整体安装，不得引入仓库外依赖）：

```text
textbook（orchestrator）  五阶段调度 + .progress.json 状态机（中断可续）
  ├─ textbook-outline     阶段 1–3：教学定位 → UbD 五件套(核心 gate) → 章节树+梯度(次要 gate)
  ├─ textbook-chapter     阶段 4：四段式单章写作（stem 档案：概念讲解→示范例题→引导练习→独立习题）
  └─ textbook-exercises   被单章 skill 调用：三类题生成 + 每题验证（手段取自学科档案）

textbook-init（独立辅助）  不入调度链：动笔前规划并创建工作目录（可选 git 与 README 工作说明），产出交接给 textbook
```

**[skills/textbook/references/handoff-contract.md](skills/textbook/references/handoff-contract.md) 是全项目唯一权威定义**——阶段间交接契约、教材项目落盘布局、`.progress.json` 状态机与重入规则、进度打印/gate 停点格式、上下文隔离原则，全部以它为准。5 个 SKILL.md 一律引用它，不得各自重复定义；契约字段名上下游**逐字一致**，同义改写（如"章节树"写成"章节列表"）即破坏契约。

学科差异不在上述任何位置分支，而是收拢在**学科档案**里，规格见 [skills/textbook/references/subject-profile-spec.md](skills/textbook/references/subject-profile-spec.md)：随学科变化的只有四个可变点——题型集、验证手段、认知动词与层级示例、章内段义与载体扩展；每份档案 `profiles/<id>.md` 固定四节、每节恰有一个消费者（阶段 1 / exercises / outline / chapter）。**内核只写学科无关规则，档案只写本学科增量**（通用 Bloom 动词、三类题支撑纪律、四段式脚手架逻辑、通用文体规范都留内核，档案不复制）。支持新学科 = 加一份档案 + 索引登记一行 + **回头改相邻档案第 1 节的分流规则**（新学科此前多半被某份档案当作"边界学科"收编了，旧规则还指着老去处，阶段 1 就会读到两套矛盾口径；校验脚本查不出这种矛盾），内核零改动；要改内核才能容纳的新学科，说明四点划分不够，先讨论再动手。

理解运行时行为的关键机制（详见契约文档）：

- **双 gate**：阶段 2（UbD 五件套）、阶段 3（章节树+梯度报告）必须作者明确确认才放行；"确认，但把 X 改一下"按修改分支处理，修改优先于确认；
- **状态机**：`.progress.json` 只由主 skill 读写（子 skill 一律不碰），每完成一阶段/一章立即写盘；重入按契约文档第 4 节规则表定位续点；
- **上下文隔离**：单章写作不读其他章正文，跨章一致性只靠术语表、前章小结、UbD 五件套三个轻量载体传递——这是 10+ 章长教材不爆上下文的根本保证；
- **学科档案**：阶段 1 判定一次 → 落盘 `.progress.json` 的 `subject_profile` → 逐章原样透传，中途不重判（换档案等于换验证纪律与段式，已写的章会与后写的章不是一本书）；存量项目无此字段按 `stem` 处理，不阻塞续写；
- **子 skill 调用方式**：Skill 工具优先，不可用时降级为直接读对方 SKILL.md 并遵循执行。

## 分发与跨宿主

目标宿主三个，Claude Code 是 evals 的基线宿主。仓库根的清单文件让**仓库自身成为插件市场**，三个宿主都能一键装：

| 宿主 | 清单文件 | 用户侧入口 | 散装目录（用户级 / 项目级） |
| ---- | -------- | ---------- | ---- |
| Claude Code | `.claude-plugin/plugin.json` + `marketplace.json` | `/plugin marketplace add cabbage2000-lab/textbook-writer-skills` | `~/.claude/skills/` / `.claude/skills/` |
| Codex | `.codex-plugin/plugin.json` + `.agents/plugins/marketplace.json` | `codex plugin marketplace add cabbage2000-lab/textbook-writer-skills` | `~/.codex/skills/` / `.codex/skills/`、`.agents/skills/` |
| WorkBuddy | `.codebuddy-plugin/plugin.json` + `marketplace.json` | `/plugin marketplace add cabbage2000-lab/textbook-writer-skills` | `~/.workbuddy/skills/` / `.codebuddy/skills/`（注意项目级不是 `.workbuddy/`） |

第四个分发渠道 **SkillHub**（[skillhub.cn](https://skillhub.cn)）不走清单，走 CLI 逐个上传，元数据读的是 SKILL.md frontmatter 里的 `slug` / `displayName` / `version`（缺一个就拒绝发布）。它与上面三个宿主的差别有两处要记住：

- **一次只发一个 skill 文件夹**，本仓库要发 5 次，且 SkillHub 侧没有"整体安装"的概念。而本仓库有 45 条跨 skill 的 `../<skill-name>/references/` 引用、5 个 skill 构成全网状依赖，**用户只装其中一两个就会读到不存在的路径**。CLI 安装落盘为 `<install_root>/<slug>/`（同级目录），所以 `slug` 必须与目录名逐字相同、5 份 summary 都写明"需与其余 skill 同级安装"——这两条是断链的唯一防线，改 slug 等于批量制造坏安装；
- 发布前用 `skillhub publish skills/<name> --dry-run` 本地预检（不发 HTTP 请求，无需登录）。发布本身要求账号已实名认证 + API Token，且**限频约每分钟 3 次**（连发 3 个后剩下的报 429，隔 80 秒重试即成功）。平台列表页展示的 description 取自 frontmatter 的 `summary` 而非 `description`——断链警告写在 `summary` 里才对用户可见。

2026-09-02 已上架 v0.6.0 全部 5 个（`@user_6733bad6` 命名空间），端到端实测通过：18 条唯一跨 skill 引用全部解析、装回来的内容与仓库逐字一致。安装侧有一个没写在官方文档里的坑：`skillhub install` **加 `--namespace` 会多套一层 `@<handle>/` 目录**，宿主只扫 `skills/*/SKILL.md` 这一层，多一层就一个都发现不到且无报错。详见 [ADR 0011](docs/adr/0011-skillhub-distribution-and-frontmatter-metadata.md)。

三套清单**不能合并**：Codex 的 plugin.json 多要 `skills: "./skills/"` 指针与一整块 `interface`（displayName / shortDescription / longDescription / developerName / category / capabilities / defaultPrompt 全必填），marketplace 条目的 `source` 是对象且必带 `policy`；CodeBuddy 与 Claude 版结构同构（skills 靠 plugin 根下的 `skills/` 自动发现），但清单目录、`owner.name` 必填这两点不同。六份清单的公共字段由 `validate_skills.py` 的 `validate_manifests` 守住不漂——发版时带 `version` 的**十处一起升版**：六份清单里的五处（`.agents/plugins/marketplace.json` 按 Codex 规范不带 version）+ 5 个 SKILL.md 的 frontmatter（SkillHub 从这里读版本号）。后 5 处由 `validate_skill_versions` 钉在 `.claude-plugin/plugin.json` 上，漏升即校验失败。

实测记录：Codex 侧 2026-08-03 在 codex-cli 0.146.0 上跑通（隔离 `CODEX_HOME` 做本地路径市场 → `codex plugin add` → 5 个 SKILL.md 与 8 个 references 全部装载，官方预检脚本 `~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py` 通过）；WorkBuddy 侧清单格式**已由作者在其他项目实测可用**，本仓库按同一格式编写（本仓库的清单未单独复测，差异仅在 name/description 等元信息）。

**跨宿主中立**是设计约束：skill 的核心路径只依赖通用 agent skills 标准（SKILL.md frontmatter + `references/` 分层加载 + 相对路径互引 + 无仓库外依赖）。宿主专有能力只能作可选增强，且必须写明纯文本降级路径——现存两处：Skill 工具调子 skill（降级为直接读对方 SKILL.md）、AskUserQuestion 一轮提问（降级为编号提问等文本回复）。要加第三处前先问一句：没有这个能力的宿主会不会退化到不可用。plugin 清单是增量增强，`skills/` 散装主体原样保留，任何宿主照常按 SKILL.md 装载。

## 改动影响半径与必跑 evals

影响半径从大到小：handoff-contract.md / subject-profile-spec.md（各牵动全部 5 个 skill）＞ SKILL.md 的调用契约段（牵动调用方与被调用方两侧）＞ SKILL.md 流程段 / references / 单份档案（只影响本 skill 或用该档案的教材）＞ scripts/tests/docs（不影响 skill 行为，CI 绿即可）。

| 改动位置 | 必跑用例 |
| -------- | -------- |
| textbook（含 handoff-contract.md、subject-profile-spec.md） | 1, 2, 3, 4（涉及契约第 3 节落盘布局时补跑 6） |
| textbook-outline | 1 |
| textbook-chapter | 2, 3 |
| textbook-exercises | 2 |
| textbook-init | 6 |
| `profiles/stem.md` | 1, 2, 3 |
| `profiles/humanities.md` | 7, 8 |
| `profiles/economics.md` | 9, 10 |

用例 4 只验证中断-续写机制（写 1 章即中断、续 1 章即可判定，不写完全书），耗时 ~40-60 分钟；「整本书写完 + 阶段 5 自检 + 交付摘要」的验收职责在用例 5（数小时）。若改动专门涉及阶段 5 自检或交付摘要逻辑，额外补跑用例 5。

## 校验脚本强制的硬约束（改 skill 前先知道）

- SKILL.md ≤ 500 行——超限把细节下沉到 `references/`（渐进披露：SKILL.md 只放工作流骨架，并明确指路"何时读哪个文件"）；
- frontmatter：`name` 与目录名一致；`description` 50–1024 字符，承担全部触发职责（写清"何时用 + 干什么 + 何时不用"，带中文触发词示例）；仅允许白名单字段——前 7 个是三宿主读的（name/description/version/license/allowed-tools/compatibility/metadata），后 3 个是 SkillHub 发布要的（slug/displayName/summary），白名单外的字段处处被静默忽略；`version` 必须与 `.claude-plugin/plugin.json` 一致（`validate_skill_versions` 守着，见下条）；
- `skills/` 下所有 .md 禁止占位符词（TBD、TODO、FIXME、XXX、待补充、占位）；
- `references/` 及其子目录下每个 .md ≥ 500 字节；**所有** .md 引用的 references 路径（含多级 `../` 跨 skill）必须真实存在；
- 学科档案：每份 `profiles/<id>.md` 含规格第 3 节的四个固定小节；第 2 节题型表表头固定为 `| 题型 | 示例 | 验证手段 | 无法验证时的降级 |` 且**「验证手段」列不得为空或写"无"**（红线的结构性保障）；规格第 5 节索引表与实际档案文件一一对应；
- 三宿主六份清单的 name/version/description/license 必须一致，Codex 侧另查 `skills` 指针、`interface` 必填字段、marketplace 条目的 source/policy 形状，CodeBuddy 侧另查 `owner.name` 与条目 `source: "./"`；另有 `validate_skill_versions` 把 5 个 SKILL.md 的 `version` 钉在 `.claude-plugin/plugin.json` 上——发版时这十处一起升版；
- `.gitignore` 不得忽略 `.claude-plugin`、`.codex-plugin`、`.codebuddy-plugin`、`.agents`（分发清单必须入库）；三个 `.*-plugin/` 里只放清单文件，`skills/` 必须在仓库根（放错位置装上后一个 skill 都加载不到）。

写给模型的指令尽量讲清动机（"上下文膨胀会让长教材写不完"），而不是堆砌大写的 MUST。

## 红线（源自 PRD，任何改动不得突破）

- 例题答案必须按所用学科档案第 2 节定义的手段验证（`stem` 档案 = 真算复核），验证不了的明确标注 `⚠️ 需作者确认`，绝不假装已验证——档案能定义"用什么方式验证"，不能定义"是否需要验证"；
- 阶段 2/3 双 gate 必须作者明确确认才放行，任何"优化"不得绕过；
- 单章写作只接收输入契约，不读其他章正文；
- `.progress.json` 只由主 skill 读写；
- 交付的 .md 不含占位符。

## 修改 skill 的完成标准（DoD）

结构校验通过 → 单元测试全绿 → 按上表重跑受影响的 evals 用例 → 更新 [CHANGELOG.md](CHANGELOG.md) 的 Unreleased 段 → 行为语义有变化时（gate 规则、契约字段、验证纪律）同步更新 README 与受影响 skill 的交叉引用。

新增 skill 清单、发版流程（版本语义：MAJOR = 契约或落盘格式不兼容变更）见 [CONTRIBUTING.md](CONTRIBUTING.md)。
