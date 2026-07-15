# 写教材 Skill 组合（textbook-writer-skills）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按 [PRD](../../write-textbook-skill-PRD.md) 落地 M1——建成 4 个 skill（write-textbook 主 skill + design-textbook-outline / write-textbook-chapter / generate-textbook-exercises 三个子 skill）+ 6 个 references + 结构校验脚本，使其在本项目内可被 Claude Code 触发，为 M2 试跑做好准备。

**Architecture:** 以 UbD 逆向设计为内核的 skill 组合。主 skill 驱动五阶段流程并靠 `.progress.json` 落盘状态实现中断可续；三个子 skill 分别承担大纲设计（含两个 gate）、单章四段式写作、例题真算验证。skill 全部放 `.claude/skills/`（项目级自动发现），references 按主要归属放各 skill 的 `references/` 下，跨 skill 用 `../<skill-name>/references/` 相对路径引用。

**Tech Stack:** Claude Code skill（Markdown SKILL.md + YAML frontmatter）、Python 3 标准库（校验脚本 + unittest 测试，零第三方依赖）、git。

## Global Constraints

以下约束来自 PRD，对所有任务生效（任务正文不再重复）：

- **学科范围 v1 锁 STEM 概念型**；遇文科题型标注"v2 支持"并降级处理（PRD §0、§9）。
- **产出物是 Markdown 教材文件**，不做 LMS/在线平台（PRD §2.2）。
- **不自动生成插图**：真实界面截图走人工标注块，抽象流程走 mermaid/SVG 代码块，均需作者确认（PRD §2.2）。
- **教材正文默认中文**，技术术语中英对照后统一用一种（PRD §6）。
- **真实性红线**：STEM 例题答案必须真算验证，算不对的不能输出；习题必须附参考答案或解题路径；不能验证的明确标注"需作者确认"（PRD §5.6）。
- **阶段 2 是核心 gate、阶段 3 是次要 gate**，均须作者明确确认后放行；其余阶段只打印一行进度不打断（PRD §5.1、§5.2）。
- **单章写作输入只含必要切片**（该章大纲切片 + UbD 五件套 + 术语表 + 前章小结），不传其他章正文（PRD §5.4、§6）。
- 所有交付的 `.md` 文件**不得含占位符**（TBD/TODO/FIXME/待补充/占位），由校验脚本强制（PRD M1 验收标准）。
- skill 文档语言：中文为主体，frontmatter description 参照 tutorial-writer 惯例用英文主体 + 中文触发词。

---

## 全局接口定义（所有任务共享，出现分歧以本节为准）

### A. 目录布局

```
textbook-writer-skills/
├── .claude/skills/
│   ├── write-textbook/
│   │   ├── SKILL.md
│   │   └── references/handoff-contract.md
│   ├── design-textbook-outline/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── ubd-framework.md
│   │       └── bloom-levels.md
│   ├── write-textbook-chapter/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── chapter-template.md
│   │       └── writing-style.md
│   └── generate-textbook-exercises/
│       ├── SKILL.md
│       └── references/exercise-design.md
├── scripts/validate_skills.py
├── tests/test_validate_skills.py
├── docs/…（已有 PRD、调研、本计划）
├── .gitignore
└── README.md
```

跨 skill 引用一律写相对路径，如在 `generate-textbook-exercises/SKILL.md` 中引用 `../design-textbook-outline/references/bloom-levels.md`。

### B. 四个 skill 的 frontmatter（原文，不得改动）

**write-textbook：**

```yaml
name: write-textbook
description: Use when the user wants to write a complete multi-chapter textbook or systematic course material with exercises — e.g. "写教材"、"写一本教材"、"编写课程讲义"、"系统教材"、"textbook". Orchestrates a five-stage UbD-driven pipeline (教学定位 → UbD 预期结果 gate → 章节树 gate → 逐章写作 → 审核定稿) with resumable progress via .progress.json. Not for single tutorials (use tutorial-writer), single chapters (use write-textbook-chapter), or exercise-only requests (use generate-textbook-exercises).
```

**design-textbook-outline：**

```yaml
name: design-textbook-outline
description: Use when a textbook project needs its teaching design — 教学定位、UbD 预期结果五件套（大概念/持久理解/核心问题/迁移目标/学习目标）、章节树与例题 Bloom 梯度规划 — e.g. "设计教材大纲"、"教材规划"、"课程体系设计". Usually orchestrated by write-textbook; can run standalone to produce 00-教材设计.md. Not for writing chapter prose or generating exercises.
```

**write-textbook-chapter：**

```yaml
name: write-textbook-chapter
description: Use when writing one textbook chapter following the fixed 四段式 structure (概念讲解 → 示范例题 → 引导练习 → 独立习题) from an outline slice plus UbD anchor — e.g. "写第三章"、"按大纲写这一章". Usually orchestrated by write-textbook; can run standalone for a deep-dive technical article with worked examples. Not for designing outlines or whole-book orchestration.
```

**generate-textbook-exercises：**

```yaml
name: generate-textbook-exercises
description: Use when generating verified STEM exercises with Bloom-level tags — 示范例题（完整解题过程）、引导练习（带提示）、独立习题（附参考答案）— e.g. "出几道矩阵乘法的练习题"、"给这一章生成例题". Every computational answer is actually verified (真算核对) before output. Usually called by write-textbook-chapter; can run standalone. Not for 文科论述题 (v2) or exam paper assembly.
```

### C. Bloom 层级标准名与标注格式

- 六层级唯一写法（低→高）：**记忆、理解、应用、分析、评价、创造**。首次出现处注英文（remembering / understanding / applying / analyzing / evaluating / creating），其后只用中文。
- 题目标注格式（行内、紧跟标题）：`【Bloom：应用】`。
- 学习目标标注格式：目标句 + `（Bloom：应用）`。

### D. 四段式段名（章内二级标题固定文案）

`## N.1 概念讲解`、`## N.2 示范例题`、`## N.3 引导练习`、`## N.4 独立习题`（N 为章号）。章首有引言段（无标题），章尾固定 `## 本章小结`（供下一章作"前章核心结论摘要"输入）。

### E. 阶段间交接契约（字段名以此为准）

- 阶段 1 → 2：`{学科, 读者认知起点, 教材深度, 篇幅规模}`（篇幅规模为章数区间，如 8–12 章）
- 阶段 2 → 3（须作者确认后）：`{大概念[], 持久理解[], 核心问题[], 迁移目标[], 学习目标[]}`（学习目标每条带 Bloom 层级）
- 阶段 3 → 4（须作者确认后）：`{章节树[], 例题习题计划[], 表现性任务[], 梯度报告}`
  - 章节树每项：`{章号, 章标题, 一句话定位, 承载的持久理解编号[]}`
  - 例题习题计划每项：`{章号, 示范例题[], 引导练习[], 独立习题[]}`，每题条目 `{主题, Bloom层级}`
- 主 skill → write-textbook-chapter（逐章调用）：`{章号, 章标题, 该章大纲切片, UbD五件套, 术语表, 前章小结}`
  - UbD五件套 = `{大概念[], 持久理解[], 核心问题[]}`；第 1 章的前章小结为空
- write-textbook-chapter → 主 skill：`{章文件路径, 新增术语[], Bloom标注回写[]}`
  - Bloom标注回写每项：`{题目编号, 类型, Bloom层级}`（类型 ∈ 示范例题/引导练习/独立习题）
- write-textbook-chapter → generate-textbook-exercises：`{章上下文, 题目计划, 术语表}`
  - 章上下文 = `{章号, 章标题, 本章概念清单, 本章学习目标}`；题目计划 = 该章例题习题计划条目
- generate-textbook-exercises → write-textbook-chapter：`{题目[]}`，每题 `{编号, 类型, 题干, 解答或提示, Bloom层级, 验证状态}`

### F. 教材项目落盘布局（skill 运行时产出）

```
<教材名>/
├── 00-教材设计.md      # 固定二级标题：## 一、教学定位 / ## 二、UbD 五件套（已确认）/ ## 三、章节树与梯度规划（已确认）/ ## 四、表现性任务
├── 01-<章标题>.md       # 章文件命名 NN-<章标题>.md，NN 从 01 起两位数字
├── 02-<章标题>.md
├── 术语表.md            # 表格列：| 术语（中文） | 英文 | 定义/约定 | 首次出现章节 |
└── .progress.json
```

### G. `.progress.json` schema（主 skill 维护，子 skill 不写）

```json
{
  "textbook_name": "线性代数入门",
  "subject": "线性代数",
  "created_at": "2026-07-14",
  "updated_at": "2026-07-15",
  "current_stage": 4,
  "gates": {
    "stage2_ubd_confirmed": true,
    "stage3_outline_confirmed": true
  },
  "chapters": {
    "total": 10,
    "done": [1, 2, 3],
    "next": 4
  },
  "stage5_passed": null
}
```

字段规则：`current_stage` ∈ 1–5，表示"当前待完成的阶段"；阶段完成即推进并立即写盘；`chapters.next` = 最小未完成章号；`stage5_passed` ∈ null/true/false。

重入规则表（主 skill 启动时执行）：

| 读到的状态 | 动作 |
|-----------|------|
| 无 `.progress.json` | 全新项目：问教材名 → 建目录 → 从阶段 1 开始 |
| `current_stage=2` 且 `stage2_ubd_confirmed=false` | 从 `00-教材设计.md` 读出五件套重新呈现，等确认 |
| `current_stage=3` 且 `stage3_outline_confirmed=false` | 重新呈现章节树+梯度报告，等确认 |
| `current_stage=4` | 从 `chapters.next` 继续逐章写作 |
| `current_stage=5` | 重跑阶段 5 自检 |

### H. Bloom 梯度告警规则（bloom-levels.md 定义，阶段 3 与阶段 5 共用）

统计口径：全书所有例题+习题按 Bloom 层级计数（示范例题/引导练习/独立习题都算）。

- **规则 1（单层堆积）**：任一层级占比 ≥60% → 告警：`⚠️ 梯度告警：<层级> 层占比 N%，题目过度堆积`，并列出建议补题的章。
- **规则 2（缺高层）**：应用 + 分析两层合计 = 0 题 → 告警：`⚠️ 梯度告警：全书没有"应用/分析"层题目，缺认知阶梯上段`。
- **规则 3（缺低层入门，提示级）**：记忆 + 理解两层合计 = 0 题 → 提示：`ℹ️ 全书没有低层级入门题，确认读者起点是否足够高`。

梯度报告固定格式：层级 × 章节计数矩阵表 + 合计行 + 占比行 + 告警/提示块。

### I. 例题/习题正文格式（chapter-template 与 exercise-design 共用）

```markdown
#### 例 3-1：矩阵乘法的行视角【Bloom：理解】
**题目**：……
**解**：（逐步推导，每步一行理由）
**验证**：✅ 已验证（Python/sympy 复算，结果一致）

#### 习题 3-2【Bloom：应用】
**题目**：……
**参考答案**：……（或 **解题路径**：关键步骤 1 → 2 → 3）
```

- 编号规则：`例 <章号>-<序号>`、`习题 <章号>-<序号>`，章内各自从 1 连续编号（引导练习计入"例"编号序列，标题后缀"（引导练习）"）。
- 验证状态仅两种：`✅ 已验证（<方式>）` / `⚠️ 需作者确认（<原因>）`。

### J. 进度打印格式（可观测性）

- 阶段级：`▶ 阶段 N/5：<名称>`
- 章级：`▶ 第 N/M 章：<章标题>`
- gate 停点必须显式说明：`⏸ 等待确认：<等什么>（回复"确认"进入下一阶段，或直接提出修改）`

### K. skill 间调用方式（SKILL.md 统一写法）

主/上游 skill 调用下游 skill 时的指令模板：

> 使用 Skill 工具调用 `<skill-name>`（传入上文契约定义的输入）；若当前环境 Skill 工具不可用或未注册该 skill，直接读取本 skill 目录同级的 `../<skill-name>/SKILL.md` 并严格遵循其指令执行。

---

## 任务总览

| # | 任务 | 交付物 |
|---|------|--------|
| 1 | 项目初始化 + 校验脚本（TDD） | git 仓库、目录骨架、`validate_skills.py` + 测试 |
| 2 | ubd-framework.md | UbD 内核 reference |
| 3 | bloom-levels.md | Bloom 内核 reference |
| 4 | chapter-template.md | 章节四段式模板 reference |
| 5 | exercise-design.md | 例题设计与验证规范 reference |
| 6 | writing-style.md | 教材文体规范（复用改造） |
| 7 | handoff-contract.md | 交接契约 + 状态机规范 reference |
| 8 | design-textbook-outline SKILL.md | 子 skill 1（阶段 1–3、双 gate） |
| 9 | generate-textbook-exercises SKILL.md | 子 skill 3（真算验证） |
| 10 | write-textbook-chapter SKILL.md | 子 skill 2（四段式单章） |
| 11 | write-textbook SKILL.md | 主 skill（调度 + 状态机 + 阶段 5） |
| 12 | 综合验证 + README + 冒烟测试 | M1 验收 + M2 试跑指引 |

---

### Task 1: 项目初始化 + 结构校验脚本

**Files:**
- Create: `.gitignore`
- Create: `scripts/validate_skills.py`
- Create: `tests/test_validate_skills.py`

**Interfaces:**
- Consumes: 无（首任务）
- Produces: `python3 scripts/validate_skills.py [skills_root]` —— 校验通过 exit 0 并打印 `✅ 校验通过：N 个 skill，M 个 markdown 文件`；失败 exit 1 并逐行打印 `❌ <位置>: <问题>`。后续每个任务用它做验收。默认 `skills_root` 为脚本所在仓库的 `.claude/skills/`。

**Steps:**

- [ ] **Step 1: git init + 目录骨架 + .gitignore**

```bash
cd /Users/blingabc/PycharmProjects/textbook-writer-skills
git init
mkdir -p .claude/skills/write-textbook/references \
         .claude/skills/design-textbook-outline/references \
         .claude/skills/write-textbook-chapter/references \
         .claude/skills/generate-textbook-exercises/references \
         scripts tests
```

`.gitignore` 内容：

```gitignore
.DS_Store
__pycache__/
*.pyc
```

- [ ] **Step 2: 写失败测试**

`tests/test_validate_skills.py`（unittest，零第三方依赖）：

```python
#!/usr/bin/env python3
"""validate_skills.py 的单元测试。用临时目录构造好/坏 skill 结构，验证校验逻辑。"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from validate_skills import validate  # noqa: E402

GOOD_DESC = (
    "Use when generating verified STEM exercises with Bloom-level tags "
    "— e.g. 出几道练习题. Not for essay questions."
)


def make_skill(root: Path, name: str, *, frontmatter_name: str | None = None,
               description: str = GOOD_DESC, body: str = "# 正文\n内容充实。\n",
               refs: dict[str, str] | None = None) -> Path:
    d = root / name
    (d / "references").mkdir(parents=True, exist_ok=True)
    fm_name = frontmatter_name if frontmatter_name is not None else name
    (d / "SKILL.md").write_text(
        f"---\nname: {fm_name}\ndescription: {description}\n---\n\n{body}",
        encoding="utf-8",
    )
    for ref_name, ref_content in (refs or {}).items():
        (d / "references" / ref_name).write_text(ref_content, encoding="utf-8")
    return d


class ValidateSkillsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_valid_skill_passes(self):
        make_skill(self.root, "good-skill",
                   body="# 说明\n详见 [规范](references/style.md)。\n",
                   refs={"style.md": "# 规范\n" + "实质内容。" * 100})
        self.assertEqual(validate(self.root), [])

    def test_missing_skill_md(self):
        (self.root / "empty-skill").mkdir()
        errors = validate(self.root)
        self.assertTrue(any("缺少 SKILL.md" in e for e in errors))

    def test_frontmatter_name_mismatch(self):
        make_skill(self.root, "skill-a", frontmatter_name="skill-b")
        errors = validate(self.root)
        self.assertTrue(any("与目录名不一致" in e for e in errors))

    def test_short_description_rejected(self):
        make_skill(self.root, "skill-a", description="太短")
        errors = validate(self.root)
        self.assertTrue(any("description" in e for e in errors))

    def test_placeholder_detected(self):
        make_skill(self.root, "skill-a", body="# 正文\nTODO: 待补充这里。\n")
        errors = validate(self.root)
        self.assertTrue(any("占位符" in e for e in errors))

    def test_broken_reference_link(self):
        make_skill(self.root, "skill-a", body="见 [不存在](references/nope.md)。\n")
        errors = validate(self.root)
        self.assertTrue(any("nope.md" in e for e in errors))

    def test_cross_skill_reference_resolved(self):
        make_skill(self.root, "skill-a",
                   body="见 [邻居](../skill-b/references/core.md)。\n")
        make_skill(self.root, "skill-b",
                   refs={"core.md": "# 核心\n" + "实质内容。" * 100})
        self.assertEqual(validate(self.root), [])

    def test_thin_reference_rejected(self):
        make_skill(self.root, "skill-a", refs={"thin.md": "薄"})
        errors = validate(self.root)
        self.assertTrue(any("过短" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: 运行测试确认失败**

Run: `cd /Users/blingabc/PycharmProjects/textbook-writer-skills && python3 -m unittest tests.test_validate_skills -v 2>&1 | head -5`
Expected: FAIL —— `ModuleNotFoundError: No module named 'validate_skills'`

- [ ] **Step 4: 实现 validate_skills.py**

`scripts/validate_skills.py`：

```python
#!/usr/bin/env python3
"""校验 .claude/skills/ 下所有 skill 的结构完整性（M1 验收工具）。

检查项：
1. 每个 skill 目录含 SKILL.md，frontmatter 的 name 与目录名一致、description ≥ 50 字符
2. 所有 .md 文件不含占位符（TBD/TODO/FIXME/XXX/待补充/占位）
3. SKILL.md 中引用的 references/ 相对路径（含 ../ 跨 skill）都存在
4. references 下每个 .md 实质内容 ≥ 500 字节

用法：python3 scripts/validate_skills.py [skills_root]
"""
import re
import sys
from pathlib import Path

PLACEHOLDER_PATTERNS = [
    r"\bTBD\b", r"\bTODO\b", r"\bFIXME\b", r"\bXXX\b", r"待补充", r"占位",
]
MIN_DESCRIPTION_LEN = 50
MIN_REFERENCE_BYTES = 500
REF_LINK_RE = re.compile(r"[(`]((?:\.\./[\w-]+/)?references/[\w./-]+?\.md)[)`]")


def parse_frontmatter(text: str) -> dict | None:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fm[key.strip()] = value.strip()
    return fm


def check_skill_md(skill_dir: Path, errors: list[str]) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"{skill_dir.name}: 缺少 SKILL.md")
        return
    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        errors.append(f"{skill_dir.name}/SKILL.md: 缺少 YAML frontmatter")
    else:
        if fm.get("name") != skill_dir.name:
            errors.append(
                f"{skill_dir.name}/SKILL.md: frontmatter name "
                f"'{fm.get('name')}' 与目录名不一致"
            )
        if len(fm.get("description", "")) < MIN_DESCRIPTION_LEN:
            errors.append(
                f"{skill_dir.name}/SKILL.md: description 缺失或过短"
                f"（<{MIN_DESCRIPTION_LEN} 字符）"
            )
    for ref in REF_LINK_RE.findall(text):
        target = (skill_dir / ref).resolve()
        if not target.exists():
            errors.append(f"{skill_dir.name}/SKILL.md: 引用的文件不存在 {ref}")


def check_placeholders(md_file: Path, skills_root: Path, errors: list[str]) -> None:
    text = md_file.read_text(encoding="utf-8")
    rel = md_file.relative_to(skills_root)
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, text):
            errors.append(f"{rel}: 含占位符（匹配 {pattern}）")


def check_reference_size(md_file: Path, skills_root: Path, errors: list[str]) -> None:
    if md_file.stat().st_size < MIN_REFERENCE_BYTES:
        rel = md_file.relative_to(skills_root)
        errors.append(f"{rel}: 内容过短（<{MIN_REFERENCE_BYTES} 字节），疑似未完成")


def validate(skills_root: Path) -> list[str]:
    errors: list[str] = []
    skill_dirs = sorted(d for d in skills_root.iterdir() if d.is_dir())
    if not skill_dirs:
        return [f"{skills_root}: 目录下没有任何 skill"]
    for skill_dir in skill_dirs:
        check_skill_md(skill_dir, errors)
        for md_file in sorted(skill_dir.rglob("*.md")):
            check_placeholders(md_file, skills_root, errors)
            if md_file.parent.name == "references":
                check_reference_size(md_file, skills_root, errors)
    return errors


def main() -> int:
    if len(sys.argv) > 1:
        skills_root = Path(sys.argv[1])
    else:
        skills_root = Path(__file__).resolve().parent.parent / ".claude" / "skills"
    if not skills_root.is_dir():
        print(f"❌ skills 目录不存在：{skills_root}")
        return 1
    errors = validate(skills_root)
    if errors:
        for e in errors:
            print(f"❌ {e}")
        return 1
    n_skills = sum(1 for d in skills_root.iterdir() if d.is_dir())
    n_md = sum(1 for _ in skills_root.rglob("*.md"))
    print(f"✅ 校验通过：{n_skills} 个 skill，{n_md} 个 markdown 文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: 运行测试确认通过**

Run: `python3 -m unittest tests.test_validate_skills -v`
Expected: `OK`，8 个测试全过

- [ ] **Step 6: Commit**

```bash
git add .gitignore scripts/validate_skills.py tests/test_validate_skills.py docs/
git commit -m "chore: 项目初始化 + skill 结构校验脚本（TDD）"
```

---

### Task 2: ubd-framework.md（UbD 内核 reference）

**Files:**
- Create: `.claude/skills/design-textbook-outline/references/ubd-framework.md`

**Interfaces:**
- Consumes: 无
- Produces: 五件套的定义、质量标准与好/坏示例。`design-textbook-outline/SKILL.md`（Task 8）在阶段 2 引用本文件；`write-textbook-chapter/SKILL.md`（Task 10）引用其中"五件套在写作中如何落地"一节。

**Steps:**

- [ ] **Step 1: 撰写文件**

章节骨架与每节必须包含的内容：

```markdown
# UbD 逆向设计框架（教材版落地指南）
## 1. 为什么逆向设计            ——"以终为始"三阶段表（确定预期结果→确定评估证据→设计学习体验）；
                                  教材最常见病是知识点堆砌无主线，UbD 阶段一就是解药（源自 PRD §1.1）
## 2. 五件套逐项落地
### 2.1 大概念（Big Ideas）      ——定义：学科中有解释力和组织力的核心概念；数量约束 3–7 个；
                                  质量标准：能否把 ≥3 个零散知识点串起来；
                                  好例（线性代数）："线性变换——矩阵不是数字表格，是空间变换的代数表示"；
                                  坏例："矩阵"（只是名词不是概念主张）
### 2.2 持久理解（Enduring Understandings）——句式强制："学生将理解……"；
                                  质量标准：忘掉细节后仍保留的洞见，不是知识点复述；
                                  好例："学生将理解：解线性方程组的过程本质上是在问'目标向量是否落在列空间里'"；
                                  坏例："学生将理解矩阵乘法的定义"（这是记忆不是理解）
### 2.3 核心问题（Essential Questions）——2–5 个开放性问题；
                                  质量标准：无标准答案、能贯穿多章反复回来；
                                  好例："为什么同一个变换在不同基下长得不一样？"；
                                  坏例："矩阵乘法怎么算？"（有标准答案）
### 2.4 迁移目标（Transfer Goals）——句式："学生能在<新情境>中运用<所学>做<事情>"；
                                  好例："学生能在遇到任何降维/压缩/推荐场景时，主动识别其中的低秩结构"
### 2.5 学习目标（Learning Objectives）——必须用 Bloom 动词（引用 bloom-levels.md 动词表）；
                                  禁用"理解/掌握/了解"模糊动词；每条可验证；
                                  好例："能用高斯消元法求解 3×4 增广矩阵方程组（Bloom：应用）"
## 3. 五件套之间的一致性检查     ——学习目标须能追溯到某条持久理解；核心问题须指向大概念；
                                  迁移目标须被至少一个表现性任务覆盖（阶段 3 校验）
## 4. 五件套在后续阶段如何使用   ——阶段 3：每章必须声明承载哪些持久理解，未对齐的章要砍或改；
                                  阶段 4：单章写作输入带五件套，概念讲解须呼应核心问题；
                                  阶段 5：全书走查每条持久理解是否有章承载
## 5. 快速自查清单              ——作者确认 gate 前的 6 问（大概念够不够少而精？持久理解是洞见还是知识点？……）
```

要求：每个术语给"定义 + 质量标准 + 至少一好一坏示例"（PRD §9 风险对策：references 给足示例降低 gate 思考成本）。示例学科统一用线性代数（呼应 M2 试点）。全文 150–250 行。

- [ ] **Step 2: 校验**

Run: `python3 scripts/validate_skills.py`
Expected: 无本文件相关报错（此时其他 skill 尚无 SKILL.md，脚本会报"缺少 SKILL.md"——只要无 ubd-framework.md 相关条目即可；或临时用 `python3 -c` 单查本文件占位符与字节数）

验收清单（人工自查）：
- [ ] 五件套每项都有定义、质量标准、好例、坏例
- [ ] "学生将理解……"句式、3–7 个大概念、2–5 个核心问题等数量约束与 PRD §5.2 一致
- [ ] 提及学习目标动词时指向 `bloom-levels.md`（同目录引用）

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/design-textbook-outline/references/ubd-framework.md
git commit -m "docs(references): UbD 框架落地指南"
```

---

### Task 3: bloom-levels.md（Bloom 内核 reference）

**Files:**
- Create: `.claude/skills/design-textbook-outline/references/bloom-levels.md`

**Interfaces:**
- Consumes: 全局接口 C（层级标准名）、H（告警规则）
- Produces: 六层级动词表、可验证学习目标写法、梯度检查规则与报告格式。被 Task 8（阶段 2 学习目标 + 阶段 3 梯度报告）、Task 9（出题标尺）、Task 11（阶段 5 复核）引用。

**Steps:**

- [ ] **Step 1: 撰写文件**

章节骨架：

```markdown
# Bloom 认知层级（修订版）：学习目标与例题梯度的标尺
## 1. 六层级总览                 ——低→高：记忆/理解/应用/分析/评价/创造（首现注英文）；
                                  每层一句话判据 + 教材场景典型题型
## 2. 中文动词表（写学习目标用）  ——每层 6–10 个动词：
   记忆：列举、复述、识别、写出定义、指出、命名
   理解：解释、概括、举例说明、用自己的话描述、判断正误并说明理由、翻译（形式间转换）
   应用：计算、求解、运用、演示、将…套用到新数据、按步骤执行
   分析：推导、分解、区分、找出关系、诊断错误、比较适用场景、归因
   评价：论证、评估优劣、选择并辩护、批判、检验
   创造：设计、构造、提出新解法、组合、证明新命题、推广
## 3. 可验证学习目标的写法        ——公式：条件 + Bloom 动词 + 对象 + 可观察标准；
                                  三组"模糊→可验证"改写示例（如"理解矩阵乘法"→
                                  "能计算 2×3 与 3×2 矩阵的乘积并解释为何交换后维度不匹配（Bloom：应用）"）
## 4. 例题/习题的层级判定         ——同一知识点在不同层级的题各长什么样（用等差数列举 6 层递进实例）；
                                  判定歧义时"就低不就高"原则
## 5. 梯度检查规则（全书级）      ——完整复制全局接口 H 的三条规则（阈值、告警文案格式）；
                                  统计口径：示范例题/引导练习/独立习题都计入
## 6. 梯度报告格式               ——层级×章节矩阵表模板 + 合计/占比行 + 告警块示例（给一个完整假数据示例表）
## 7. 每章内部的梯度建议          ——示范例题落在记忆~应用、引导练习主落应用、独立习题应用~分析为主，
                                  评价/创造少量点缀（全书 1–3 题即可）；这是建议非硬规则
```

全文 120–200 行。第 5 节的三条规则文案必须与全局接口 H **逐字一致**。

- [ ] **Step 2: 校验**

Run: `python3 scripts/validate_skills.py 2>&1 | grep bloom-levels`
Expected: 无输出（无本文件相关报错）

验收清单：
- [ ] 六层级中文名与全局接口 C 完全一致
- [ ] 每层动词 ≥6 个且互不重复
- [ ] 告警规则三条与全局接口 H 逐字一致（含 ⚠️/ℹ️ 前缀文案）
- [ ] 有完整的报告示例表（含告警块示范）

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/design-textbook-outline/references/bloom-levels.md
git commit -m "docs(references): Bloom 层级动词表与梯度检查规则"
```

---

### Task 4: chapter-template.md（章节四段式模板）

**Files:**
- Create: `.claude/skills/write-textbook-chapter/references/chapter-template.md`

**Interfaces:**
- Consumes: 全局接口 D（段名）、I（题目格式）；概念上引用 `../../design-textbook-outline/references/ubd-framework.md` 第 4 节、`../../generate-textbook-exercises/references/exercise-design.md`（Task 5，前向引用同项目内文件，Task 5 完成后校验脚本可过）
- Produces: 每章的完整 Markdown 模板 + 各段写作要点。被 Task 10 作为四段式唯一权威来源引用。

> 注意：本任务引用的 exercise-design.md 在 Task 5 才创建。为让校验脚本每步都绿，本任务完成后立即做 Task 5，再跑全量校验（两任务的校验步骤已按此安排）。

**Steps:**

- [ ] **Step 1: 撰写文件**

章节骨架：

```markdown
# 教材章节模板：四段式 + 首尾件
## 1. 设计依据                   ——脚手架与认知负荷：worked example 先行降低初学者负荷，
                                  再逐步撤除支撑（示范→引导→独立）；每个新概念建立在前一章之上不跳跃
## 2. 章的完整骨架（可直接复制的 Markdown 模板）
   ——给出一章从标题到小结的完整模板骨架，含固定标题文案：
   # 第 N 章 <章标题>
   （引言段：2–4 句，先"为什么"再"学什么"，呼应一条核心问题，不设标题）
   ## N.1 概念讲解
   ## N.2 示范例题
   ## N.3 引导练习
   ## N.4 独立习题
   ## 本章小结
## 3. 各段写作要点
### 3.1 概念讲解  ——从前章小结衔接引入；每个概念"动机→定义→直观解释→与相邻概念的关系"；
                    配图规范引用 writing-style.md（同目录）；禁止在此段塞题目
### 3.2 示范例题  ——完整解题过程（worked example），逐步给理由；由 generate-textbook-exercises 生成并验证；
                    每道题格式遵循全局题目格式（复制全局接口 I 的格式块）；1–3 道
### 3.3 引导练习  ——半独立：给"提示阶梯"（提示 1 方向性 → 提示 2 关键步骤 → 完整解答折叠在后）；1–3 道
### 3.4 独立习题  ——无提示变式 + 少量开放题；每题必附参考答案或解题路径（真实性红线）；3–8 道
### 3.5 本章小结  ——固定三件：本章核心结论（3–5 条，供下一章作"前章小结"输入）、
                    与持久理解的呼应（本章推进了哪条）、下一章预告（1 句）
## 4. 章内自查清单               ——四段俱全顺序不乱？每题有 Bloom 标注？小结三件齐？
                                  术语与术语表一致？无"留给读者"悬空？
```

全文 100–160 行。第 2 节模板必须是能直接复制的完整 Markdown 骨架（含占位说明用中文尖括号如 `<章标题>`，不用 TODO 类词）。

- [ ] **Step 2: 校验（与 Task 5 合并跑全量）**

验收清单：
- [ ] 四段标题文案与全局接口 D 逐字一致
- [ ] 题目格式块与全局接口 I 逐字一致
- [ ] 小结三件明确（核心结论条数、持久理解呼应、预告）
- [ ] 提示阶梯（引导练习的脚手架撤除机制）有具体分层定义

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/write-textbook-chapter/references/chapter-template.md
git commit -m "docs(references): 章节四段式模板与各段写作要点"
```

---

### Task 5: exercise-design.md（例题设计与验证规范）

**Files:**
- Create: `.claude/skills/generate-textbook-exercises/references/exercise-design.md`

**Interfaces:**
- Consumes: 全局接口 C、I；引用 `../../design-textbook-outline/references/bloom-levels.md`（层级判定）
- Produces: 题型分类、三类题设计规范、**答案验证流程**（真实性红线的操作化）。被 Task 9 作为出题唯一权威来源引用；被 Task 4 的 3.2–3.4 节引用。

**Steps:**

- [ ] **Step 1: 撰写文件**

章节骨架：

```markdown
# STEM 例题/习题设计与验证规范
## 1. 三类题的定位差异            ——示范例题=完整脚手架（教）；引导练习=部分脚手架（扶）；
                                   独立习题=无脚手架（放）。与 Bloom 梯度的正交关系：
                                   三类是"支撑程度"，Bloom 是"认知高度"，不可混为一谈
## 2. STEM 题型分类与验证方式
   | 题型 | 例 | 验证方式 |
   | 数值计算 | 解方程组、求行列式 | 用 Python（含 sympy/numpy，环境无则手算两遍交叉核对）独立复算最终答案 |
   | 符号推导 | 化简、求导、证明恒等式 | 逐步核验每步依据 + sympy 符号验证（可行时） |
   | 证明题 | 证明性质/定理 | 核验证明链条每步依据；无法机器验证时标注"需作者确认" |
   | 代码题 | 实现算法 | 实际运行代码核对输出 |
   | 概念辨析 | 判断+说明理由 | 核对定义来源（教材设计文档/公认定义）|
   | 开放/探究题 | 数值实验、设计类 | 不设标准答案，给"参考要点"，标注"开放题" |
## 3. 答案验证流程（红线，逐条硬性）
   1) 出题时同步写完整解答，禁止先题后答分离编造
   2) 计算类必须用与解答不同的路径独立复算（代码优先；给出验证用的代码或复算过程）
   3) 复算不一致 → 修题或修解答，重新验证；连续 2 次失败 → 弃题换题
   4) 验证状态标注只有两种（复制全局接口 I 的两种状态文案）
   5) 独立习题的参考答案同样走验证；解题路径至少含关键中间结果
   6) "留给读者作为练习"式悬空 = 违规
## 4. 三类题各自的设计要点
   ——示范例题：题面贴合刚讲的概念、解答每步一行理由、末尾"回顾这道题用到了什么"；
   ——引导练习：与示范例题同构但换数据/换场景，提示阶梯 2 层（方向→关键步骤）；
   ——独立习题：变式（换条件）、组合（跨概念）、开放（少量）；难度按 Bloom 阶梯排列，先低后高
## 5. Bloom 标注规范              ——判定标准引用 bloom-levels.md 第 4 节；标注格式（全局接口 C）；
                                   同题多问取最高层级标注
## 6. 输出格式                    ——完整复制全局接口 I 的例题/习题格式块；
                                   输出契约字段（全局接口 E 的 generate-textbook-exercises 输出）
## 7. 反模式清单                  ——全章题目同一层级；题目与本章学习目标无关；
                                   解答跳步（"易得"）；无验证直接给答案；文科论述题混入（标 v2 降级）
```

全文 130–200 行。

- [ ] **Step 2: 全量校验（覆盖 Task 4 的前向引用）**

Run: `python3 scripts/validate_skills.py 2>&1 | grep -E 'chapter-template|exercise-design'`
Expected: 无输出

验收清单：
- [ ] 验证流程 6 条硬规则齐全，含"连续 2 次失败弃题"与"悬空=违规"
- [ ] 题型表覆盖 ≥6 类且每类有验证方式
- [ ] 验证状态两种文案与全局接口 I 一致
- [ ] 三类题与 Bloom 的正交关系讲清楚（防止"引导练习=理解层"的错误绑定）

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/generate-textbook-exercises/references/exercise-design.md
git commit -m "docs(references): STEM 例题设计与真算验证规范"
```

---

### Task 6: writing-style.md（教材文体规范，复用改造）

**Files:**
- Create: `.claude/skills/write-textbook-chapter/references/writing-style.md`
- 参考源（只读）: `/Users/blingabc/PycharmProjects/tutorial-skill/references/writing-style.md`

**Interfaces:**
- Consumes: tutorial-writer 的 writing-style.md（复用其 §1 单线结构、§2 图文分工、§5 先为什么、§6 代码块、§7 常见坑、§8 术语一致、§9 措辞禁忌、§10 中文排版）
- Produces: 教材语境的文体规范。被 Task 10 全文引用；术语表规则被 Task 8 引用。

**Steps:**

- [ ] **Step 1: 撰写文件（复用 + 改造）**

改造映射（源条款 → 教材版处理）：

| tutorial-writer 条款 | 处理 |
|---|---|
| §1 单线结构 | 保留，重述为"全书一条主线=大概念递进；章内单线；延伸内容进'延伸阅读'不打断主线" |
| §2 图文分工铁律 | 保留原文精神；配图双轨改为教材简化版（见下） |
| §3 步骤化 | **弱化**——教材以概念叙事为主，仅"操作类章节"（如环境搭建）适用步骤化；正文默认叙事散文 |
| §4 章节级检查点 | **替换**为"本章小结"机制（指向 chapter-template.md 第 3.5 节） |
| §5 先"为什么"再"怎么做" | 保留，扩展为"章引言呼应核心问题" |
| §6 代码块规范 | 保留 |
| §7 常见坑提示框 | 保留（教材同样适用，格式不变） |
| §8 术语一致性 | 保留 + 扩展：**数学符号一致性**（同一量全书用同一符号，符号约定记入术语表附注） |
| §9 措辞禁忌 | 保留原文（禁"简单地/只需/显然"——数学教材尤其禁"显然/易得/trivially"跳步） |
| §10 中文排版 | 保留原文（中英文空格、标点规则） |
| §11 骨架选型 | **删除**（教材统一用四段式，无选型） |

新增教材特有条款：

```markdown
## 配图双轨（教材简化版）
- 抽象概念/流程/几何直观 → mermaid 代码块或内嵌 SVG，随正文直接产出，不依赖外部工具；
- 真实软件界面 → 人工截图标注块（四要素：内容描述/建议框选/建议尺寸/脱敏提醒），不生成图片文件；
- 每图必有图注（*图 N-M：…*，N 为章号）；纯概念章节至少一张示意图。
## 叙事性要求
- 用有论证的叙事散文，不用 bullet 堆砌讲概念（bullet 只用于真正的并列枚举）；
- 每个概念遵循"动机 → 定义 → 直观解释 → 关系"链条（与 chapter-template.md 3.1 一致）。
## 认知负荷控制
- 一个自然段只引入一个新概念；连续引入 ≥3 个新术语之间必须有例子或直观解释间隔。
```

全文 120–180 行。

- [ ] **Step 2: 校验**

Run: `python3 scripts/validate_skills.py 2>&1 | grep writing-style`
Expected: 无输出

验收清单：
- [ ] 保留条款忠实于源文件（措辞禁忌、中文排版规则原样保留）
- [ ] 步骤化已弱化、骨架选型已删除、检查点已替换为本章小结
- [ ] 新增三条款（配图双轨简化版/叙事性/认知负荷）齐全
- [ ] 数学符号一致性并入术语条款

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/write-textbook-chapter/references/writing-style.md
git commit -m "docs(references): 教材文体规范（复用 tutorial-writer 改造）"
```

---

### Task 7: handoff-contract.md（交接契约 + 状态机规范）

**Files:**
- Create: `.claude/skills/write-textbook/references/handoff-contract.md`

**Interfaces:**
- Consumes: 全局接口 E（契约）、F（落盘布局）、G（.progress.json）、J（进度打印）
- Produces: 全项目交接契约与状态机的唯一权威定义。4 个 SKILL.md（Task 8–11）全部引用本文件而非各自重复定义。

**Steps:**

- [ ] **Step 1: 撰写文件**

章节骨架：

```markdown
# 阶段交接契约与状态机规范
## 1. 契约写法约定               ——`{字段, 字段}` 形如函数签名；上游产出=下游输入，字段名逐字一致；
                                  "已确认"字样表示该产出必须经过作者 gate 确认后才可传递
## 2. 五阶段交接契约             ——完整复制全局接口 E 的全部契约（阶段 1→2、2→3、3→4、
                                  主↔章、章↔题六组），每组配一段"字段语义说明"
## 3. 教材项目落盘布局           ——完整复制全局接口 F（目录树 + 00-教材设计.md 固定标题 +
                                  章文件命名 NN-<章标题>.md + 术语表列定义）
## 4. .progress.json 状态机      ——完整复制全局接口 G（schema + 字段规则 + 重入规则表）；
                                  写盘时机：每完成一个阶段/一章立即写，绝不批量延迟
## 5. 进度打印与 gate 停点格式    ——完整复制全局接口 J 的三种格式
## 6. 上下文隔离原则             ——单章写作不得读入其他章正文；跨章一致性只靠
                                  术语表+前章小结+五件套三个轻量载体传递（PRD §9 风险对策）
```

全文 100–150 行。第 2–5 节内容与本计划全局接口 E/F/G/J **逐字一致**（本文件就是这些接口的最终归宿，计划中的定义在此落地为 skill 可引用的 reference）。

- [ ] **Step 2: 校验**

Run: `python3 scripts/validate_skills.py 2>&1 | grep handoff`
Expected: 无输出

验收清单：
- [ ] 六组契约字段名与全局接口 E 逐字一致
- [ ] .progress.json schema 示例是合法 JSON 且字段与全局接口 G 一致
- [ ] 重入规则表 5 行齐全
- [ ] 含"写盘时机"与"上下文隔离"两条纪律

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/write-textbook/references/handoff-contract.md
git commit -m "docs(references): 阶段交接契约与 .progress.json 状态机规范"
```

---

### Task 8: design-textbook-outline SKILL.md（子 skill 1）

**Files:**
- Create: `.claude/skills/design-textbook-outline/SKILL.md`

**Interfaces:**
- Consumes: `references/ubd-framework.md`、`references/bloom-levels.md`（本 skill 目录内）、`../write-textbook/references/handoff-contract.md`
- Produces: 阶段 1–3 的执行指令。产出 `00-教材设计.md`（结构=全局接口 F）；对主 skill 的返回 = 契约 `{章节树[], 例题习题计划[], 表现性任务[], 梯度报告}` + gate 确认状态。

**Steps:**

- [ ] **Step 1: 撰写 SKILL.md**

frontmatter 用全局接口 B 的原文。正文骨架：

```markdown
# design-textbook-outline
一句话职责 + 触发/不触发（不触发：写正文、生成例题、单篇教程）
## 两种调用模式
- 被 write-textbook 调度：输入为 {教材项目目录, 教材名}；产出写入该目录，gate 结果回报主 skill
- 独立触发：先问教材名与落盘目录（一轮），后续流程相同，产出 00-教材设计.md（不建 .progress.json——那是主 skill 的职责）
## 阶段 1/3：教学定位确认
- 打印 `▶ 阶段 1/3：教学定位确认`
- AskUserQuestion 一轮收集四项：学科（具体到分支）、读者认知起点（零基础/有先修）、
  教材深度（入门/进阶）、篇幅规模（6–8 / 8–12 / 12+ 章）
- 无 AskUserQuestion 环境时降级为编号提问（给出与 tutorial-writer 同款的降级问卷格式，宽松解析）
- 产出契约 {学科, 读者认知起点, 教材深度, 篇幅规模}，写入 00-教材设计.md「## 一、教学定位」
## 阶段 2/3：UbD 预期结果设计（核心 gate）
- 打印 `▶ 阶段 2/3：UbD 预期结果设计`
- 严格按 references/ubd-framework.md 设计五件套；学习目标动词查 references/bloom-levels.md 第 2 节
- 数量硬约束：大概念 3–7 / 核心问题 2–5 / 每条学习目标带 Bloom 标注
- 完整呈现五件套 → 打印 `⏸ 等待确认：UbD 五件套（回复"确认"进入章节设计，或直接提出修改）`
- **gate 规则**：作者要求修改 → 改后重新完整呈现再等确认，循环直到明确确认；未确认绝不进阶段 3
- 确认后写入 00-教材设计.md「## 二、UbD 五件套（已确认）」
## 阶段 3/3：评估与章节设计（次要 gate）
- 打印 `▶ 阶段 3/3：评估与章节设计`
- 章节树：每章 {章号, 章标题, 一句话定位, 承载的持久理解编号[]}；
  **对齐检查**：有章承载不了任何持久理解 → 砍或改；有持久理解无章承载 → 补章或明示放弃
- 例题习题计划：每章三类题的 {主题, Bloom层级} 列表（数量参考 chapter-template 的段配额：示范 1–3/引导 1–3/独立 3–8）
- 梯度报告：按 references/bloom-levels.md 第 5–6 节生成矩阵表并执行三条告警规则；有告警必须连同补题建议一起呈现
- 表现性任务：1–3 个，每个注明对应的迁移目标
- 呈现章节树+计划+梯度报告+表现性任务 → `⏸ 等待确认：章节树与梯度规划`（同款修改循环）
- 确认后写入「## 三、章节树与梯度规划（已确认）」「## 四、表现性任务」
## 产出与交接
- 落盘物：完整的 00-教材设计.md（结构见 ../write-textbook/references/handoff-contract.md 第 3 节）
- 回报上游：契约 {章节树[], 例题习题计划[], 表现性任务[], 梯度报告} + 两个 gate 均已确认的声明
## 真实性约束
- 五件套和章节树是设计产物无需验证，但阶段 1 若作者提供了学科材料，设计须与材料一致，不虚构学科内容
```

全文 120–180 行。gate 停点文案、进度打印格式与 handoff-contract.md 第 5 节一致。

- [ ] **Step 2: 校验**

Run: `python3 scripts/validate_skills.py 2>&1 | grep -v '缺少 SKILL.md'`
Expected: 除其余 3 个 skill 缺 SKILL.md 外无报错（design-textbook-outline 的所有检查项通过）

验收清单：
- [ ] frontmatter 与全局接口 B 逐字一致
- [ ] 两个 gate 都有"修改后重新呈现再确认"的循环规则，且明确"未确认绝不放行"
- [ ] 对齐检查双向（章→持久理解、持久理解→章）
- [ ] 独立触发模式不写 .progress.json
- [ ] 所有 references 引用路径正确（2 个本地 + 1 个跨 skill）

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/design-textbook-outline/SKILL.md
git commit -m "feat(skill): design-textbook-outline——UbD 大纲设计（双 gate）"
```

---

### Task 9: generate-textbook-exercises SKILL.md（子 skill 3）

**Files:**
- Create: `.claude/skills/generate-textbook-exercises/SKILL.md`

**Interfaces:**
- Consumes: `references/exercise-design.md`（本地）、`../design-textbook-outline/references/bloom-levels.md`、`../write-textbook/references/handoff-contract.md`
- Produces: 输入契约 `{章上下文, 题目计划, 术语表}` → 输出契约 `{题目[]}`（每题 `{编号, 类型, 题干, 解答或提示, Bloom层级, 验证状态}`）的执行指令。

**Steps:**

- [ ] **Step 1: 撰写 SKILL.md**

frontmatter 用全局接口 B 原文。正文骨架：

```markdown
# generate-textbook-exercises
一句话职责 + 触发/不触发（不触发：文科论述题→标注 v2 降级；组卷；非 STEM 内容）
## 两种调用模式
- 被 write-textbook-chapter 调用：输入=契约 {章上下文, 题目计划, 术语表}
- 独立触发：一轮问清 {主题, 读者水平, 三类题各要几道, 期望 Bloom 层级分布}，术语自拟
## 生成流程（每道题走完 1–4 才算完成一道）
1. 按 references/exercise-design.md 第 4 节设计题面（对照题目计划的主题与 Bloom 层级；
   层级判定标准查 ../design-textbook-outline/references/bloom-levels.md 第 4 节）
2. 同步写出完整解答（示范例题=逐步带理由；引导练习=提示阶梯+完整解答；独立习题=参考答案/解题路径）
3. **真算验证（红线）**：按 exercise-design.md 第 2 节选验证方式——
   计算/符号类：写一段独立 Python（sympy/numpy）复算，用 Bash 实际执行，比对结果；
   代码类：实际运行；证明类：逐步核验依据；
   环境无 Python 时手algo两遍交叉核对并在验证状态注明方式
4. 验证不一致 → 修题重验；连续 2 次失败 → 弃题换题（exercise-design.md 第 3 节流程）
## 输出
- 按 handoff-contract 输出契约逐题给出 {编号, 类型, 题干, 解答或提示, Bloom层级, 验证状态}
- 正文格式遵循 exercise-design.md 第 6 节（即全书统一题目格式）
- 术语用词严格对照传入的术语表
## 纪律
- 绝不输出未验证的计算答案；无法验证的标 ⚠️ 需作者确认（原因）
- 开放题给参考要点不编造标准答案
- 验证用的复算代码随输出附上（放在"验证"行后的折叠块或代码块），供作者复查
```

全文 90–140 行。

- [ ] **Step 2: 校验**

Run: `python3 scripts/validate_skills.py 2>&1 | grep generate-textbook-exercises`
Expected: 无输出

验收清单：
- [ ] frontmatter 与全局接口 B 一致
- [ ] 每道题的 4 步流程明确，验证是硬性步骤而非建议
- [ ] 输入/输出契约字段与全局接口 E 逐字一致
- [ ] 有"环境无 Python 的降级验证"路径
- [ ] 文科题型的 v2 降级处理有明确指令

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/generate-textbook-exercises/SKILL.md
git commit -m "feat(skill): generate-textbook-exercises——真算验证的例题生成"
```

---

### Task 10: write-textbook-chapter SKILL.md（子 skill 2）

**Files:**
- Create: `.claude/skills/write-textbook-chapter/SKILL.md`

**Interfaces:**
- Consumes: `references/chapter-template.md`、`references/writing-style.md`（本地）、`../design-textbook-outline/references/ubd-framework.md` 第 4 节、`../write-textbook/references/handoff-contract.md`；调用 `generate-textbook-exercises`（全局接口 K 的调用方式）
- Produces: 输入契约 `{章号, 章标题, 该章大纲切片, UbD五件套, 术语表, 前章小结}` → 落盘 `NN-<章标题>.md` + 输出契约 `{章文件路径, 新增术语[], Bloom标注回写[]}` 的执行指令。

**Steps:**

- [ ] **Step 1: 撰写 SKILL.md**

frontmatter 用全局接口 B 原文。正文骨架：

```markdown
# write-textbook-chapter
一句话职责 + 触发/不触发（不触发：设计大纲、全书调度、纯出题）
## 两种调用模式
- 被 write-textbook 调度：输入=契约 {章号, 章标题, 该章大纲切片, UbD五件套, 术语表, 前章小结}
- 独立触发（写深度文章）：一轮问清 {主题, 读者水平, 篇幅}，自拟轻量版五件套（1 条持久理解+1 个核心问题），
  无前章小结与外部术语表时自建术语表
## 上下文隔离纪律（PRD 核心 NFR）
- 只接收上述输入契约，**不读入其他章正文**；跨章一致性靠 {术语表, 前章小结, 五件套} 三载体
## 写作流程
1. 打印 `▶ 第 N/M 章：<章标题>`（被调度时；独立触发打印章标题即可）
2. 按 references/chapter-template.md 第 2 节骨架起草：引言（衔接前章小结、呼应核心问题）→ 概念讲解
   （writing-style.md 全文约束：叙事性、认知负荷、术语一致、措辞禁忌、中文排版、配图双轨）
3. 调用 generate-textbook-exercises（全局调用方式：Skill 工具，降级读 ../generate-textbook-exercises/SKILL.md）
   传入 {章上下文, 题目计划(来自大纲切片), 术语表}，将返回题目按四段式放入 N.2/N.3/N.4
4. 写「本章小结」三件（chapter-template.md 3.5）
5. 落盘 NN-<章标题>.md；按 chapter-template.md 第 4 节章内自查清单逐项自查并修正
## 输出
- 契约 {章文件路径, 新增术语[], Bloom标注回写[]}——新增术语=本章首次引入且已按术语表格式登记的词条；
  Bloom标注回写=本章每道题的 {题目编号, 类型, Bloom层级}（供主 skill 阶段 5 复核实际梯度）
## 真实性约束
- 概念讲解中的事实性内容基于大纲切片与作者已确认的教材设计，不虚构学科结论；
  例题验证责任在 generate-textbook-exercises，本 skill 不得改动已验证解答的数值
```

全文 100–150 行。

- [ ] **Step 2: 校验**

Run: `python3 scripts/validate_skills.py 2>&1 | grep write-textbook-chapter`
Expected: 无输出

验收清单：
- [ ] frontmatter 与全局接口 B 一致
- [ ] 输入/输出契约字段与全局接口 E 逐字一致
- [ ] 上下文隔离纪律明确（不读其他章正文）
- [ ] 调用 exercises skill 的方式遵循全局接口 K（含降级路径）
- [ ] 独立触发模式有轻量版五件套自拟规则

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/write-textbook-chapter/SKILL.md
git commit -m "feat(skill): write-textbook-chapter——四段式单章写作"
```

---

### Task 11: write-textbook SKILL.md（主 skill / orchestrator）

**Files:**
- Create: `.claude/skills/write-textbook/SKILL.md`

**Interfaces:**
- Consumes: `references/handoff-contract.md`（本地）、`../design-textbook-outline/references/bloom-levels.md`（阶段 5 复核）；调用 `design-textbook-outline` 与 `write-textbook-chapter`（全局接口 K）
- Produces: 五阶段调度、状态机维护、阶段 5 自检的执行指令。最终交付 = 完整教材目录（全局接口 F）。

**Steps:**

- [ ] **Step 1: 撰写 SKILL.md**

frontmatter 用全局接口 B 原文。正文骨架：

```markdown
# write-textbook
一句话职责 + 触发/不触发（不触发：单篇教程→tutorial-writer；单章→write-textbook-chapter；只出题→generate-textbook-exercises）
## 工作流总览（五阶段表）
| 阶段 | 名称 | 执行者 | 产出 | Gate? |
|（按 PRD §5.1 五行表，标注阶段 2 核心 gate/阶段 3 次要 gate）|
## 启动与重入（每次触发第一件事）
1. 确定教材项目目录：用户指定或询问一次（默认 ./<教材名>/）
2. 找 .progress.json：无 → 新项目（建目录+初始化 .progress.json，current_stage=1）；
   有 → 按 references/handoff-contract.md 第 4 节重入规则表定位续点，打印
   `▶ 续写：<教材名>，从阶段 N（/第 N 章）继续`
3. .progress.json 只由本 skill 读写；每完成一阶段/一章立即更新（写盘时机纪律）
## 阶段 1–3：委托 design-textbook-outline
- 按全局调用方式调用（Skill 工具，降级读 ../design-textbook-outline/SKILL.md）
- 其内部两个 gate 即本流程的 gate；每个 gate 确认后本 skill 更新 gates.* 字段并推进 current_stage
## 阶段 4：逐章循环
- 打印 `▶ 阶段 4/5：章节正文编写`
- for 章号 in chapters.next..total：
  1) 从 00-教材设计.md 提取该章大纲切片（章节树条目+该章例题习题计划）
  2) 读术语表.md 当前版 + 前一章文件的「## 本章小结」（第 1 章传空）
  3) 组装输入契约调用 write-textbook-chapter
  4) 收输出契约：新增术语追加进术语表.md；Bloom 标注回写暂存进 .progress.json 同级的设计文档
     「三、章节树与梯度规划」下该章条目的"实际"列（计划 vs 实际并排）
  5) chapters.done += 该章；chapters.next += 1；写盘 .progress.json
- 任何一章中断，重入时从 chapters.next 无缝继续（已完成章不重写）
## 阶段 5：审核定稿（自检清单，非 gate，必须全跑）
- 打印 `▶ 阶段 5/5：审核定稿`
- 逐项检查并输出报告（每项：通过/不通过+具体位置+建议）：
  1) 章节对齐走查：每章「本章小结」声明的持久理解呼应 vs 00-教材设计.md 的承载计划
  2) Bloom 梯度复核：用各章"实际"标注重算矩阵，按 bloom-levels.md 三条告警规则复核（不只看计划）
  3) 术语一致性：术语表 vs 各章用词抽查（每章至少查引言+小结）
  4) 例题验证残留：全书搜"⚠️ 需作者确认"，汇总清单呈现（有标注是合规的，但必须汇总让作者看见）
  5) 循序渐进走查：每章引言是否衔接前章小结、无前置知识跳跃
- 报告后：不通过项由作者决定修不修；作者要求修 → 定位到章，重新调用 write-textbook-chapter 修订该章
- 全部处理完：stage5_passed=true 写盘，输出交付摘要（章数/题数/验证数/告警处理情况）
## 交付物
- <教材名>/ 完整目录（00-教材设计.md、NN-章.md × N、术语表.md、.progress.json）
- 说明边界：正文与结构定稿；人工截图标注块（如有）需作者自行补图后才算可发布
```

全文 130–190 行。

- [ ] **Step 2: 校验**

Run: `python3 scripts/validate_skills.py`
Expected: `✅ 校验通过：4 个 skill，10 个 markdown 文件`

验收清单：
- [ ] frontmatter 与全局接口 B 一致
- [ ] 重入逻辑覆盖重入规则表全部 5 种状态
- [ ] 阶段 4 循环的 5 个子步骤齐全（提取切片/读上下文/调用/收写回/写盘）
- [ ] 阶段 5 五项自检与 PRD §5.5 一一对应
- [ ] "计划 vs 实际"Bloom 梯度复核明确（不只看计划）
- [ ] gate 语义：主 skill 不越过子 skill 的未确认 gate 推进状态

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/write-textbook/SKILL.md
git commit -m "feat(skill): write-textbook 主 skill——五阶段调度与状态机"
```

---

### Task 12: 综合验证 + README + 冒烟测试（M1 验收）

**Files:**
- Create: `README.md`
- Modify: 前序任务发现的任何不一致处

**Interfaces:**
- Consumes: 全部前序产出
- Produces: M1 验收证据 + M2 试跑指引

**Steps:**

- [ ] **Step 1: 全量静态校验**

Run: `python3 -m unittest tests.test_validate_skills -v && python3 scripts/validate_skills.py`
Expected: 测试 OK + `✅ 校验通过：4 个 skill，10 个 markdown 文件`

- [ ] **Step 2: 跨文件一致性人工走查（对照全局接口定义）**

逐项核对并当场修正：
- [ ] 六组契约字段名：handoff-contract.md = 4 个 SKILL.md 中的用法
- [ ] Bloom 六层级名与告警三规则：bloom-levels.md = outline SKILL = 主 SKILL 阶段 5
- [ ] 四段式标题文案：chapter-template.md = chapter SKILL
- [ ] 题目格式与验证状态文案：exercise-design.md = exercises SKILL = chapter-template.md
- [ ] `.progress.json` 字段：handoff-contract.md = 主 SKILL
- [ ] 进度打印/gate 停点格式：handoff-contract.md = 3 个有打印行为的 SKILL
- [ ] 所有跨 skill `../` 引用路径真实存在（校验脚本已查，人工复核语义指向正确的节号）

- [ ] **Step 3: 子代理行为冒烟测试（3 个场景）**

用 Agent 工具 dispatch 3 个 general-purpose 子代理（只读验证，不改文件），各给一个场景：

1. **exercises skill 冒烟**：「读取 `.claude/skills/generate-textbook-exercises/SKILL.md` 及其引用的 references，严格按其指令为主题"等差数列求和"生成 1 道示范例题（Bloom：应用），完整走完验证流程，输出题目+解答+验证过程」。检查点：解答逐步带理由、真实执行了复算、输出含 `✅ 已验证` 状态与 Bloom 标注。
2. **outline skill gate 冒烟**：「读取 `design-textbook-outline/SKILL.md` 及 references，模拟被主 skill 调度为"线性代数入门"设计阶段 2 五件套，**到 gate 停点为止**，报告你会向作者呈现什么、以什么文案等待确认」。检查点：五件套齐全且数量约束达标、停点文案 = `⏸ 等待确认：…`、明确表示未确认不继续。
3. **主 skill 重入冒烟**：「读取 `write-textbook/SKILL.md` 及 handoff-contract.md，给你如下 .progress.json（current_stage=4, chapters={total:10, done:[1,2,3], next:4}），报告重入后你的第一步动作和要组装的输入契约字段」。检查点：定位到第 4 章续写、契约六字段齐全、提到读第 3 章「本章小结」与术语表。

任一检查点不过 → 定位对应 SKILL.md 措辞歧义并修正，重跑该场景。

- [ ] **Step 4: 撰写 README.md**

内容（60–100 行）：项目一句话定位；四 skill 架构图（复制 PRD §4.2 树）；目录结构；安装方式（本项目内自动生效；全局安装 `cp -r .claude/skills/* ~/.claude/skills/`）；**M2 试跑指引**——新开 Claude Code 会话，输入"用 write-textbook 写一本《线性代数入门》教材"，预期走到阶段 2 gate 停点；校验命令；PRD/调研文档链接；里程碑状态表（M1 ✅ / M2–M5 待跑）。

- [ ] **Step 5: 最终校验 + Commit**

Run: `python3 scripts/validate_skills.py && python3 -m unittest tests.test_validate_skills`
Expected: 全绿

```bash
git add -A
git commit -m "docs: README 与 M1 综合验收（冒烟测试通过）"
```

---

## Self-Review 记录

**Spec 覆盖核对**（PRD → 任务）：G1 UbD gate → T8/T11；G2 Bloom 标注+告警 → T3/T8/T11；G3 四段式 → T4/T10；G4 真算验证 → T5/T9；G5 上下文隔离 → T7/T10/T11；G6 工程复用 → T6/T7；US1–US6 → T8(US1,US2)/T10(US3,US5)/T9(US4)/T11(US6)；§5.5 自检五项 → T11 阶段 5；§7 六 references → T2–T7；M1 验收 → T1/T12；M2 准备 → T12 README。无缺口。

**类型一致性**：契约字段、schema、层级名、段名、格式文案全部锚定在"全局接口定义 A–K"，各任务只引用不重定义；T12 Step 2 做最终逐项核对。

**执行方式**：用户已明确"生成计划再实施计划"且本会话为自主模式 → 采用 Inline Execution（superpowers:executing-plans），顺序执行 T1→T12（跨文档一致性优先，不并行）。
