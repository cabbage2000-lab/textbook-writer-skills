# 贡献指南

本仓库是长期维护的 agent skill 组合项目（目标宿主：Claude Code / Codex / WorkBuddy）。skill 是"给模型看的程序"，改一行指令就可能改变运行行为，所以本项目用三层防线保证质量：**结构校验（CI 自动）→ 单元测试（CI 自动）→ 行为测试（evals 人工跑）**。

## 架构一览：改哪里，影响什么

```text
skills/
├── textbook/                          # 主 skill：五阶段调度 + .progress.json 状态机
│   └── references/
│       ├── handoff-contract.md        # ⚠️ 全项目契约权威定义——5 个 skill 都依赖它
│       ├── subject-profile-spec.md    # ⚠️ 学科档案规格：四个可变点的收口处
│       └── profiles/                  # 学科档案（可插拔，加一个学科 = 加一个文件）
│           ├── stem.md                #   数学/物理/计算机…：答案可复算
│           ├── humanities.md          #   历史/哲学/文学…：答案靠论证，引文与史实可核查
│           └── economics.md           #   经济学/金融学…：模型题复算 + 数据题核来源，两类交织
├── textbook-outline/                  # 阶段 1-3：教学定位 → UbD 五件套(gate) → 章节树(gate)
├── textbook-chapter/                  # 阶段 4：四段式单章写作
├── textbook-exercises/                # 被单章调用：三类题生成 + 每题验证
└── textbook-init/                     # 独立辅助（不入调度链）：动笔前规划并创建工作目录
```

**内核与档案的分界**：随学科变化的只有四处——题型集、验证手段、认知动词与层级示例、章内段义与载体扩展，一律收在档案里；其余（五阶段、双 gate、状态机、UbD 五件套、Bloom 六层骨架与通用动词、三类题支撑纪律、四段式脚手架逻辑、验证状态二值化）属内核，档案不得重复定义或覆盖。判断法：一段话换个学科照样成立，它就属于内核。

改动的影响半径从大到小：

1. **handoff-contract.md**（契约/落盘布局/状态机/gate 判定）：牵动全部 5 个 skill，必须全量重跑 evals 用例 1–4；涉及第 3 节落盘布局时补跑 6（textbook-init 的方案呈现与 README 模板引用该节）；
2. **subject-profile-spec.md**（档案规格：四节结构、消费关系、内核边界）：牵动全部 5 个 skill 与所有档案，同 1 处理；**改某一份档案**只影响用该档案的教材，重跑该档案对应的用例；
3. **SKILL.md 的调用契约段**（输入/输出契约、两种调用模式）：牵动调用方与被调用方两侧，重跑双方用例；
4. **SKILL.md 的流程段 / references**：只影响本 skill，重跑对应用例即可；
5. **scripts/ tests/ docs/**：不影响 skill 行为，CI 绿即可。

## 本地开发

```bash
git clone <repo> && cd textbook-writer-skills
mkdir -p .claude && ln -s ../skills .claude/skills   # 软链为项目级 skills，改动即时生效
python3 scripts/validate_skills.py                    # 结构校验
python3 -m unittest discover -s tests                 # 单元测试
```

零第三方依赖（Python 3.10+ 标准库）。`.claude/` 已 gitignore，软链不入库。

## 修改 skill 的完成标准（DoD）

一次 skill 改动要合入，需满足：

1. `python3 scripts/validate_skills.py` 通过（frontmatter、引用完整性、无占位符、清单一致、学科档案四节结构与验证手段列非空、SKILL.md ≤ 500 行——超限就把细节下沉到 `references/`）；
2. 单元测试全绿；
3. 按下表重跑受影响的 evals 用例（用例定义见 [evals/evals.json](evals/evals.json)，跑法见 [evals/README.md](evals/README.md)），assertions 逐条通过：

   | 改动位置 | 必跑用例 |
   | -------- | -------- |
   | textbook（含 handoff-contract.md、subject-profile-spec.md） | 1, 2, 3, 4 |
   | textbook-outline | 1 |
   | textbook-chapter | 2, 3 |
   | textbook-exercises | 2 |
   | textbook-init | 6 |
   | `profiles/stem.md` | 1, 2, 3 |
   | `profiles/humanities.md` | 7, 8 |
   | `profiles/economics.md` | 9, 10 |

   用例 4 只验证中断-续写机制（不写完全书），若改动专门涉及阶段 5 自检或交付摘要逻辑，额外补跑用例 5（该场景的验收职责已移交 eval 5，见 evals/README.md）。

4. 更新 [CHANGELOG.md](CHANGELOG.md) 的 Unreleased 段；
5. 行为语义有变化时（gate 规则、契约字段、验证纪律），同步更新 README 与受影响 skill 的交叉引用。

## 写 skill 的规范

- **frontmatter**：`name` 与目录名一致；`description` 承担全部触发职责——写清"何时用 + 干什么 + 何时不用"，带中文触发词示例，50–1024 字符；另有 SkillHub 上架要的 `slug`（**必须逐字等于目录名**，它同时是用户机器上的安装目录名）、`displayName`、`version`（与 `.claude-plugin/plugin.json` 一致）、`summary`（写明"需与其余 skill 同级安装"），取舍见 [ADR 0011](docs/adr/0011-skillhub-distribution-and-frontmatter-metadata.md)；白名单外的字段一概不写；
- **渐进披露**：SKILL.md 只放工作流骨架（目标 ≤ 500 行），操作细节、模板、查表下沉到 `references/`，并在正文明确指路"何时读哪个文件"；
- **跨 skill 引用**：一律相对路径（`../<skill-name>/references/xxx.md`），校验脚本会检查存在性；5 个 skill 是整体组合，不得引入仓库外依赖；
- **跨宿主中立**：核心路径只依赖通用 agent skills 标准（SKILL.md frontmatter + `references/` 分层加载 + 相对路径互引）。宿主专有能力只能作可选增强，且必须写明纯文本降级路径——现存两处是 Skill 工具调子 skill（降级为直接读对方 SKILL.md）与 AskUserQuestion 一轮提问（降级为编号提问）。三个宿主的装法与六份分发清单见 [README](README.md) 与 CLAUDE.md 的「分发与跨宿主」一节；
- **解释为什么**：给模型的指令尽量讲清动机（"上下文膨胀会让长教材写不完"），而不是堆砌大写的 MUST；
- **无占位符**：TBD/TODO/FIXME/待补充 一律不准入库，校验脚本强制。

## 新增 skill 清单

1. 建 `skills/<new-skill>/SKILL.md`（+ 按需 `references/`），遵循上节规范；
2. 在 [evals/evals.json](evals/evals.json) 为它追加至少 1 个带 assertions 的用例，并更新上面的映射表；
3. 更新 README 架构图与目录结构小节；
4. 若纳入 textbook 调度链，须在 handoff-contract.md 定义其输入/输出契约；
5. 校验 + 测试 + 新用例跑通，CHANGELOG 记录；
6. 要一并上架 SkillHub 的，用 `skillhub publish skills/<new-skill> --dry-run` 预检后单独发一次（平台一次只收一个 skill 文件夹），并确认它引用的其他 skill 都已上架——否则用户装了它却读不到 `../<skill-name>/references/`。

## 新增学科档案清单

支持一个新学科门类**不需要新增 skill、不需要改内核**，只需加一份档案：

1. 按 [subject-profile-spec.md](skills/textbook/references/subject-profile-spec.md) 第 3 节写 `skills/textbook/references/profiles/<id>.md`，四节齐全，第 2 节每个题型都填出验证手段（填不出的题型不写进档案）；
2. 在规格第 5 节索引表登记一行；
3. **回头改相邻档案第 1 节的分流规则**——新学科此前多半被某份档案当作"边界学科"收编了（`economics` 落地前，stem 与 humanities 第 1 节都写着经济学怎么分流）。索引里多一份档案、旧分流规则却还指着老去处，阶段 1 就会读到两套互相矛盾的判定口径。校验脚本查不出这种矛盾，只能靠这一步；
4. 跑校验（会查四节结构、表头、验证手段非空、索引与文件一一对应）；
5. 在 evals.json 追加用例，断言锚定**形式性可判定项**（每题有验证状态行、题目数等于验证行数、开放题附参考要点、四段标题与档案一致），不要写"内容质量好不好"这类无法客观判定的断言；
6. 若发现必须改内核才能容纳新学科，说明四个可变点的划分不够——先讨论再动手，不要在内核里加学科分支。

## 发版流程

版本号语义：**MAJOR** = 契约或落盘格式不兼容变更（老项目的 `.progress.json` 不能续用）；**MINOR** = 新增 skill/新能力；**PATCH** = 指令修正与文档修补。

1. 同步升版带 `version` 的**十处**：三宿主六份清单里的五处——`.claude-plugin/{plugin,marketplace}.json`、`.codex-plugin/plugin.json`、`.codebuddy-plugin/{plugin,marketplace}.json`（`.agents/plugins/marketplace.json` 按 Codex 规范不带 version，无需改）——加上 5 个 `skills/*/SKILL.md` 的 frontmatter（SkillHub 从这里读版本号，见 [ADR 0011](docs/adr/0011-skillhub-distribution-and-frontmatter-metadata.md)）。任一处不一致 CI 会拒绝。README 的 version badge 也是同一份事实，但**没有脚本守着**——v0.2.0 发版时它漏改过一次，别再漏；
2. CHANGELOG 的 Unreleased 段落固化为版本号 + 日期；
3. 打 tag：`git tag v<version> && git push --tags`。
4. push tag 后 GitHub Actions（[.github/workflows/release.yml](.github/workflows/release.yml)）会自动创建对应的 GitHub Release，说明文字取自 CHANGELOG 对应版本段；若需要给历史 tag 补建或更新 Release，手动触发 `gh workflow run release.yml -f tag=v<version>`。

## 红线约束（源自 PRD，任何改动不得突破；PRD 原文为本地文档不纳入版本库，决策摘要见 [docs/adr/](docs/adr/README.md)）

- 例题答案必须按所用学科档案第 2 节定义的手段验证（`stem` 档案 = 真算复核），验证不了的明确标注 `⚠️ 需作者确认`，绝不假装已验证——档案能定义"用什么方式验证"，不能定义"是否需要验证"；
- 阶段 2/3 双 gate 必须作者明确确认才放行，任何"优化"不得绕过；
- 单章写作只接收输入契约，不读其他章正文（上下文隔离）;
- `.progress.json` 只由主 skill 读写；
- 交付的 `.md` 不含占位符。
