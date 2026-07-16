# 贡献指南

本仓库是长期维护的 Claude Code skill 组合项目。skill 是"给模型看的程序"，改一行指令就可能改变运行行为，所以本项目用三层防线保证质量：**结构校验（CI 自动）→ 单元测试（CI 自动）→ 行为测试（evals 人工跑）**。

## 架构一览：改哪里，影响什么

```text
skills/
├── textbook/                          # 主 skill：五阶段调度 + .progress.json 状态机
│   └── references/handoff-contract.md # ⚠️ 全项目契约权威定义——5 个 skill 都依赖它
├── textbook-outline/                  # 阶段 1-3：教学定位 → UbD 五件套(gate) → 章节树(gate)
├── textbook-chapter/                  # 阶段 4：四段式单章写作
├── textbook-exercises/                # 被单章调用：三类题生成 + 真算验证
└── textbook-init/                     # 独立辅助（不入调度链）：动笔前规划并创建工作目录
```

改动的影响半径从大到小：

1. **handoff-contract.md**（契约/落盘布局/状态机/gate 判定）：牵动全部 5 个 skill，必须全量重跑 evals 用例 1–4；涉及第 3 节落盘布局时补跑 6（textbook-init 的方案呈现与 README 模板引用该节）；
2. **SKILL.md 的调用契约段**（输入/输出契约、两种调用模式）：牵动调用方与被调用方两侧，重跑双方用例；
3. **SKILL.md 的流程段 / references**：只影响本 skill，重跑对应用例即可；
4. **scripts/ tests/ docs/**：不影响 skill 行为，CI 绿即可。

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

1. `python3 scripts/validate_skills.py` 通过（frontmatter、引用完整性、无占位符、清单一致、SKILL.md ≤ 500 行——超限就把细节下沉到 `references/`）；
2. 单元测试全绿；
3. 按下表重跑受影响的 evals 用例（用例定义见 [evals/evals.json](evals/evals.json)，跑法见 [evals/README.md](evals/README.md)），assertions 逐条通过：

   | 改动位置 | 必跑用例 |
   | -------- | -------- |
   | textbook（含 handoff-contract.md） | 1, 2, 3, 4 |
   | textbook-outline | 1 |
   | textbook-chapter | 2, 3 |
   | textbook-exercises | 2 |
   | textbook-init | 6 |

   用例 4 只验证中断-续写机制（不写完全书），若改动专门涉及阶段 5 自检或交付摘要逻辑，额外补跑用例 5（该场景的验收职责已移交 eval 5，见 evals/README.md）。

4. 更新 [CHANGELOG.md](CHANGELOG.md) 的 Unreleased 段；
5. 行为语义有变化时（gate 规则、契约字段、验证纪律），同步更新 README 与受影响 skill 的交叉引用。

## 写 skill 的规范

- **frontmatter**：`name` 与目录名一致；`description` 承担全部触发职责——写清"何时用 + 干什么 + 何时不用"，带中文触发词示例，50–1024 字符；
- **渐进披露**：SKILL.md 只放工作流骨架（目标 ≤ 500 行），操作细节、模板、查表下沉到 `references/`，并在正文明确指路"何时读哪个文件"；
- **跨 skill 引用**：一律相对路径（`../<skill-name>/references/xxx.md`），校验脚本会检查存在性；5 个 skill 是整体组合，不得引入仓库外依赖；
- **解释为什么**：给模型的指令尽量讲清动机（"上下文膨胀会让长教材写不完"），而不是堆砌大写的 MUST；
- **无占位符**：TBD/TODO/FIXME/待补充 一律不准入库，校验脚本强制。

## 新增 skill 清单

1. 建 `skills/<new-skill>/SKILL.md`（+ 按需 `references/`），遵循上节规范；
2. 在 [evals/evals.json](evals/evals.json) 为它追加至少 1 个带 assertions 的用例，并更新上面的映射表；
3. 更新 README 架构图与目录结构小节；
4. 若纳入 textbook 调度链，须在 handoff-contract.md 定义其输入/输出契约；
5. 校验 + 测试 + 新用例跑通，CHANGELOG 记录。

## 发版流程

版本号语义：**MAJOR** = 契约或落盘格式不兼容变更（老项目的 `.progress.json` 不能续用）；**MINOR** = 新增 skill/新能力；**PATCH** = 指令修正与文档修补。

1. 同步升版 `.claude-plugin/plugin.json` 与 `marketplace.json` 的 `version`（两处不一致 CI 会拒绝）；
2. CHANGELOG 的 Unreleased 段落固化为版本号 + 日期；
3. 打 tag：`git tag v<version> && git push --tags`。
4. push tag 后 GitHub Actions（[.github/workflows/release.yml](.github/workflows/release.yml)）会自动创建对应的 GitHub Release，说明文字取自 CHANGELOG 对应版本段；若需要给历史 tag 补建或更新 Release，手动触发 `gh workflow run release.yml -f tag=v<version>`。

## 红线约束（源自 PRD，任何改动不得突破；PRD 原文为本地文档不纳入版本库，决策摘要见 [docs/adr/](docs/adr/README.md)）

- STEM 例题答案必须真算验证，验证不了的明确标注 `⚠️ 需作者确认`，绝不假装已验证；
- 阶段 2/3 双 gate 必须作者明确确认才放行，任何"优化"不得绕过；
- 单章写作只接收输入契约，不读其他章正文（上下文隔离）;
- `.progress.json` 只由主 skill 读写；
- 交付的 `.md` 不含占位符。
