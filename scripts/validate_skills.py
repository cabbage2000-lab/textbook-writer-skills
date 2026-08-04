#!/usr/bin/env python3
"""校验本仓库的结构完整性：skills/ 内容质量 + plugin 清单一致性 + 仓库健康。

skill 结构检查（validate）：
1. 每个 skill 目录含 SKILL.md，frontmatter 的 name 与目录名一致、description ≥ 50 字符
2. description ≤ 1024 字符（Claude Code 对 frontmatter description 的硬限制）
3. frontmatter 仅含白名单字段（防手误写入无效字段被静默忽略）
4. SKILL.md ≤ 500 行（渐进披露预算：超限内容应下沉到 references/）
5. 所有 .md 文件不含占位符（TBD/TODO/FIXME/XXX/待补充/占位）
6. 所有 .md 中引用的 references/ 相对路径（含多级 ../ 跨 skill）都存在
7. references/ 及其子目录下每个 .md 实质内容 ≥ 500 字节

学科档案检查（validate_subject_profiles）：学科差异收拢在可插拔的档案里，
规格见 skills/textbook/references/subject-profile-spec.md：
13. 每份档案含规格要求的四个固定小节（缺一节，消费它的 skill 就无处可查）
14. 档案第 2 节题型表的「验证手段」列不得为空——红线「每题必须验证」靠这条守住：
    档案能定义"用什么方式验证"，不能定义"是否需要验证"
15. 规格第 5 节索引表与 profiles/ 下实际文件一一对应（有档案不登记 = 选不到，
    登记了没文件 = 运行时读不到）

plugin 清单检查（validate_manifests）：三个宿主各要一套清单，格式不同不能合并，
只能各写一份 + 在此守住六份不背离（同一份元数据抄六遍，必然漂移）：
8. 六份清单都存在且可解析——Claude Code 读 .claude-plugin/{plugin,marketplace}.json，
   Codex 读 .codex-plugin/plugin.json + .agents/plugins/marketplace.json，
   WorkBuddy（CodeBuddy 内核）读 .codebuddy-plugin/{plugin,marketplace}.json
9. 六份清单的 name / version / description / license 一致（发版时最易漏改处）
10. 各宿主专有字段合规：Codex 的 skills 指针指向 ./skills/、interface 必填字段齐全、
    marketplace 条目为 local + ./ 且 policy.installation 为 AVAILABLE；
    CodeBuddy 的 marketplace 有 owner.name、条目 source 为 ./

仓库健康检查（validate_repo_health）：
11. .gitignore 不得忽略 .claude-plugin / .codex-plugin / .codebuddy-plugin / .agents
    （分发清单必须入库，否则 plugin 装不出去）
12. 三个 .*-plugin/ 目录只放清单文件——skills/ 必须在仓库根（plugin 根），
    塞进清单目录会导致一个 skill 都加载不到
13. 学科档案规格文件与至少一份档案存在（缺了它们，四个可变点就会重新弥散回各 skill）

用法：python3 scripts/validate_skills.py [skills_root]
"""
import json
import re
import sys
from pathlib import Path

PLACEHOLDER_PATTERNS = [
    r"\bTBD\b", r"\bTODO\b", r"\bFIXME\b", r"\bXXX\b", r"待补充", r"占位",
]
MIN_DESCRIPTION_LEN = 50
MAX_DESCRIPTION_LEN = 1024
MAX_SKILL_MD_LINES = 500
MIN_REFERENCE_BYTES = 500
# Claude Code 实际会读取的 frontmatter 字段；其余字段会被静默忽略，写了等于埋雷
ALLOWED_FRONTMATTER_KEYS = {
    "name", "description", "version", "license", "allowed-tools",
    "compatibility", "metadata",
}
REF_LINK_RE = re.compile(r"[(`]((?:\.\./)*(?:[\w-]+/)*references/[\w./-]+?\.md)[)`]")
# 学科档案层：内核 skill 持有规格，各档案放 profiles/ 下（详见 subject-profile-spec.md）
PROFILE_SPEC_REL = Path("textbook/references/subject-profile-spec.md")
PROFILE_DIR_REL = Path("textbook/references/profiles")
# 档案的固定四节：每节恰有一个消费者（阶段 1 / exercises / outline / chapter）
PROFILE_REQUIRED_SECTIONS = (
    "## 1 适用范围与判定",
    "## 2 题型集与验证方式",
    "## 3 认知动词与层级示例",
    "## 4 章内段义与载体扩展",
)
PROFILE_TABLE_HEADER = ("题型", "示例", "验证手段", "无法验证时的降级")
# 「验证手段」列写成这些等于宣称该题型不用验证——正是红线要拦的
PROFILE_EMPTY_MEANS = {"", "-", "—", "–", "无", "不适用", "n/a", "na", "none"}
PROFILE_LINK_RE = re.compile(r"\(profiles/([\w-]+)\.md\)")
# 各宿主的 plugin 清单里必须逐字一致的字段（同一个 plugin 分三处发行，元信息只有一份事实）
MIRRORED_FIELDS = ("name", "version", "description", "license")
# Codex 官方摄取校验（plugin-creator/validate_plugin.py）要求的 interface 必填字段，
# 缺任一项整个 plugin 会被判非法
CODEX_INTERFACE_REQUIRED = (
    "displayName", "shortDescription", "longDescription", "developerName",
    "category", "capabilities", "defaultPrompt",
)
# 分发清单所在目录：被 .gitignore 掉就等于没发布，且新增清单文件会静默丢失
MANIFEST_DIRS = (".claude-plugin", ".codex-plugin", ".codebuddy-plugin", ".agents")
# 各 .*-plugin/ 目录允许出现的文件——skills/ 必须留在仓库根（plugin 根）
MANIFEST_DIR_ALLOWED = {
    ".claude-plugin": {"plugin.json", "marketplace.json"},
    ".codex-plugin": {"plugin.json"},
    ".codebuddy-plugin": {"plugin.json", "marketplace.json"},
}


def parse_frontmatter(text: str) -> dict | None:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
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
        desc = fm.get("description", "")
        if len(desc) < MIN_DESCRIPTION_LEN:
            errors.append(
                f"{skill_dir.name}/SKILL.md: description 缺失或过短"
                f"（<{MIN_DESCRIPTION_LEN} 字符）"
            )
        if len(desc) > MAX_DESCRIPTION_LEN:
            errors.append(
                f"{skill_dir.name}/SKILL.md: description 超长"
                f"（{len(desc)} > {MAX_DESCRIPTION_LEN} 字符，超出部分会被截断）"
            )
        unknown = set(fm) - ALLOWED_FRONTMATTER_KEYS
        if unknown:
            errors.append(
                f"{skill_dir.name}/SKILL.md: frontmatter 含未知字段 "
                f"{sorted(unknown)}（会被 Claude Code 静默忽略）"
            )
    n_lines = text.count("\n") + 1
    if n_lines > MAX_SKILL_MD_LINES:
        errors.append(
            f"{skill_dir.name}/SKILL.md: {n_lines} 行超出预算"
            f"（>{MAX_SKILL_MD_LINES} 行，请把细节下沉到 references/）"
        )


def check_reference_links(md_file: Path, skills_root: Path, errors: list[str]) -> None:
    """引用完整性覆盖所有 .md，不只 SKILL.md——档案层与内核互引密度高，断链要当场发现。"""
    text = md_file.read_text(encoding="utf-8")
    rel = md_file.relative_to(skills_root)
    for ref in REF_LINK_RE.findall(text):
        if not (md_file.parent / ref).resolve().exists():
            errors.append(f"{rel}: 引用的文件不存在 {ref}")


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
            check_reference_links(md_file, skills_root, errors)
            # 判定用 parts 而非 parent.name：references/ 的子目录（如 profiles/）同样受约
            if "references" in md_file.parts:
                check_reference_size(md_file, skills_root, errors)
    return errors


def _section_body(text: str, heading: str) -> str:
    """取某个二级标题到下一个二级标题之间的正文；标题不存在则返回空串。"""
    start = text.find(heading)
    if start < 0:
        return ""
    rest = text[start + len(heading):]
    nxt = re.search(r"^## ", rest, re.MULTILINE)
    return rest[:nxt.start()] if nxt else rest


def _table_rows(body: str) -> list[list[str]]:
    """解析 Markdown 表格，返回去掉表头与分隔行的数据行（每行为单元格列表）。"""
    rows = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):  # 分隔行
            continue
        rows.append(cells)
    return rows


def check_profile(md_file: Path, skills_root: Path, errors: list[str]) -> None:
    text = md_file.read_text(encoding="utf-8")
    rel = md_file.relative_to(skills_root)
    for section in PROFILE_REQUIRED_SECTIONS:
        if section not in text:
            errors.append(
                f"{rel}: 缺少固定小节「{section}」"
                "——四节结构见 subject-profile-spec.md 第 3 节，缺一节消费它的 skill 就无处可查"
            )
    rows = _table_rows(_section_body(text, PROFILE_REQUIRED_SECTIONS[1]))
    if not rows:
        errors.append(f"{rel}: 第 2 节没有题型表（表头须为 {' | '.join(PROFILE_TABLE_HEADER)}）")
        return
    header, data = rows[0], rows[1:]
    if tuple(header[:4]) != PROFILE_TABLE_HEADER:
        errors.append(
            f"{rel}: 第 2 节表头为 {header}，必须是 {list(PROFILE_TABLE_HEADER)}"
            "——表头固定才能机械校验验证手段是否填了"
        )
        return
    if not data:
        errors.append(f"{rel}: 第 2 节题型表没有任何题型")
    for row in data:
        if len(row) < 4:
            errors.append(f"{rel}: 第 2 节题型行列数不足（{row}），四列都必须填")
            continue
        if row[2].lower() in PROFILE_EMPTY_MEANS:
            errors.append(
                f"{rel}: 题型「{row[0]}」的验证手段为空（{row[2]!r}）"
                "——档案只能定义'用什么方式验证'，不能定义'是否需要验证'；"
                "填不出手段的题型不该写进档案"
            )


def validate_subject_profiles(skills_root: Path) -> list[str]:
    """学科档案层：四节齐全 + 验证手段非空 + 索引与文件一一对应。

    档案不存在时静默跳过（显式传入的任意 skills 目录未必是本仓库布局）；
    本仓库缺档案层由 validate_repo_health 报错。
    """
    spec = skills_root / PROFILE_SPEC_REL
    profile_dir = skills_root / PROFILE_DIR_REL
    if not spec.exists():
        return []
    errors: list[str] = []
    indexed = set(PROFILE_LINK_RE.findall(spec.read_text(encoding="utf-8")))
    on_disk = {p.stem for p in profile_dir.glob("*.md")} if profile_dir.is_dir() else set()
    for missing in sorted(indexed - on_disk):
        errors.append(
            f"{PROFILE_SPEC_REL}: 索引表登记了档案 '{missing}'，"
            f"但 {PROFILE_DIR_REL}/{missing}.md 不存在——运行时读不到"
        )
    for unlisted in sorted(on_disk - indexed):
        errors.append(
            f"{PROFILE_DIR_REL}/{unlisted}.md: 未登记在 {PROFILE_SPEC_REL} 第 5 节索引表"
            "——没登记的档案阶段 1 选不到，等于白写"
        )
    for profile in sorted(profile_dir.glob("*.md")) if profile_dir.is_dir() else []:
        check_profile(profile, skills_root, errors)
    return errors


def _load_json(path: Path, errors: list[str], label: str) -> dict | None:
    if not path.exists():
        errors.append(f"{label}: 文件不存在")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"{label}: JSON 解析失败（{e}）")
        return None


def validate_manifests(repo_root: Path) -> list[str]:
    """六份清单是同一份元数据的手工拷贝，强制同步。

    三个宿主的清单格式不同、不能共用一份：Claude Code 读 `.claude-plugin/` 下的
    plugin.json + marketplace.json；Codex 读 `.codex-plugin/plugin.json`（多要
    `skills` 指针与一整块 `interface`）+ `.agents/plugins/marketplace.json`（条目的
    source 是对象、必带 policy）；WorkBuddy 读 `.codebuddy-plugin/` 下的同名两份
    （结构与 Claude 版同构）。所以只能各写一份，由本函数守住不背离。
    """
    errors: list[str] = []
    manifest_dir = repo_root / ".claude-plugin"
    plugin = _load_json(
        manifest_dir / "plugin.json", errors, ".claude-plugin/plugin.json")
    marketplace = _load_json(
        manifest_dir / "marketplace.json", errors, ".claude-plugin/marketplace.json")
    if plugin is None or marketplace is None:
        return errors

    for field in ("name", "version", "description"):
        if not plugin.get(field):
            errors.append(f"plugin.json: 缺少 {field} 字段")

    entries = marketplace.get("plugins") or []
    entry = next(
        (p for p in entries if p.get("name") == plugin.get("name")), None
    )
    if entry is None:
        errors.append(
            f"marketplace.json: plugins 中找不到与 plugin.json "
            f"同名的条目 '{plugin.get('name')}'"
        )
        return errors
    for field in ("version", "description", "license"):
        if entry.get(field) != plugin.get(field):
            errors.append(
                f"两份清单的 {field} 不一致：plugin.json="
                f"'{plugin.get(field)}' vs marketplace.json='{entry.get(field)}'"
            )
    errors += validate_codex_manifests(repo_root, plugin)
    errors += validate_codebuddy_manifests(repo_root, plugin)
    return errors


def validate_codex_manifests(repo_root: Path, plugin: dict) -> list[str]:
    """Codex 侧两份清单：与 Claude 侧同源，外加 Codex 专有的摄取要求。"""
    errors: list[str] = []
    codex_plugin = _load_json(
        repo_root / ".codex-plugin" / "plugin.json", errors,
        ".codex-plugin/plugin.json")
    codex_market = _load_json(
        repo_root / ".agents" / "plugins" / "marketplace.json", errors,
        ".agents/plugins/marketplace.json")
    if codex_plugin is None or codex_market is None:
        return errors

    for field in MIRRORED_FIELDS:
        if codex_plugin.get(field) != plugin.get(field):
            errors.append(
                f"跨宿主 plugin 清单的 {field} 不一致：.claude-plugin/plugin.json="
                f"'{plugin.get(field)}' vs .codex-plugin/plugin.json="
                f"'{codex_plugin.get(field)}'"
            )
    if codex_plugin.get("skills") != "./skills/":
        errors.append(
            f".codex-plugin/plugin.json: skills 指针为 "
            f"'{codex_plugin.get('skills')}'，必须是 './skills/'"
            "——Codex 靠它发现 skill，指错则一个命令都不出现"
        )
    interface = codex_plugin.get("interface")
    if not isinstance(interface, dict):
        errors.append(
            ".codex-plugin/plugin.json: 缺少 interface 块（Codex 摄取必需）")
    else:
        missing = [f for f in CODEX_INTERFACE_REQUIRED if not interface.get(f)]
        if missing:
            errors.append(
                f".codex-plugin/plugin.json: interface 缺少必填字段 {missing}"
                "（Codex 官方摄取校验会判整个 plugin 非法）"
            )

    codex_entry = next(
        (p for p in (codex_market.get("plugins") or [])
         if p.get("name") == plugin.get("name")), None
    )
    if codex_entry is None:
        errors.append(
            f".agents/plugins/marketplace.json: plugins 中找不到与 plugin.json "
            f"同名的条目 '{plugin.get('name')}'——`codex plugin add` "
            "按名字找不到就装不上"
        )
        return errors
    source = codex_entry.get("source")
    if not isinstance(source, dict) or source.get("source") != "local" \
            or source.get("path") != "./":
        errors.append(
            f".agents/plugins/marketplace.json: 条目 source={source!r}，"
            "仓库自身即 plugin，必须是 source=local + path=./"
        )
    policy = codex_entry.get("policy")
    if not isinstance(policy, dict) or policy.get("installation") != "AVAILABLE":
        errors.append(
            f".agents/plugins/marketplace.json: 条目 policy={policy!r}，"
            "installation 必须为 AVAILABLE，否则用户在市场里装不了"
        )
    return errors


def validate_codebuddy_manifests(repo_root: Path, plugin: dict) -> list[str]:
    """WorkBuddy（CodeBuddy 内核）侧两份清单：结构与 Claude 版同构，另放一个目录。

    CodeBuddy 读 `.codebuddy-plugin/`，skills 靠 plugin 根下的 `skills/` 自动发现
    （无需 skills 指针）；marketplace 条目的 source 与 Claude 版一样是相对路径字符串。
    """
    errors: list[str] = []
    manifest_dir = repo_root / ".codebuddy-plugin"
    cb_plugin = _load_json(
        manifest_dir / "plugin.json", errors, ".codebuddy-plugin/plugin.json")
    cb_market = _load_json(
        manifest_dir / "marketplace.json", errors,
        ".codebuddy-plugin/marketplace.json")
    if cb_plugin is None or cb_market is None:
        return errors

    for field in MIRRORED_FIELDS:
        if cb_plugin.get(field) != plugin.get(field):
            errors.append(
                f"跨宿主 plugin 清单的 {field} 不一致：.claude-plugin/plugin.json="
                f"'{plugin.get(field)}' vs .codebuddy-plugin/plugin.json="
                f"'{cb_plugin.get(field)}'"
            )
    if not (cb_market.get("owner") or {}).get("name"):
        errors.append(
            ".codebuddy-plugin/marketplace.json: 缺少 owner.name（CodeBuddy 市场必填）")
    entry = next(
        (p for p in (cb_market.get("plugins") or [])
         if p.get("name") == plugin.get("name")), None
    )
    if entry is None:
        errors.append(
            f".codebuddy-plugin/marketplace.json: plugins 中找不到与 plugin.json "
            f"同名的条目 '{plugin.get('name')}'"
        )
        return errors
    for field in ("version", "description", "license"):
        if entry.get(field) != plugin.get(field):
            errors.append(
                f".codebuddy-plugin 两份清单的 {field} 不一致：plugin.json="
                f"'{plugin.get(field)}' vs marketplace.json='{entry.get(field)}'"
            )
    if entry.get("source") != "./":
        errors.append(
            f".codebuddy-plugin/marketplace.json: 条目 source="
            f"'{entry.get('source')}'，仓库自身即 plugin，必须是 './'"
        )
    return errors


def validate_repo_health(repo_root: Path) -> list[str]:
    """防回归：这些坑踩过一次，用校验固化下来。"""
    errors: list[str] = []
    gitignore = repo_root / ".gitignore"
    if gitignore.exists():
        for raw in gitignore.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line.startswith("#") or not line:
                continue
            if line.rstrip("/").lstrip("/") in MANIFEST_DIRS:
                errors.append(
                    f".gitignore: 忽略了 {line}——plugin 分发清单"
                    "必须入库，该目录被忽略会导致新增清单文件静默丢失"
                )
    for dirname, allowed in MANIFEST_DIR_ALLOWED.items():
        manifest_dir = repo_root / dirname
        if not manifest_dir.is_dir():
            continue
        extra = sorted(
            p.name for p in manifest_dir.iterdir()
            if not p.name.startswith(".") and p.name not in allowed
        )
        if extra:
            errors.append(
                f"{dirname}/: 出现了不该有的内容 {extra}——该目录只放清单文件，"
                "skills/ 必须在仓库根（plugin 根），放错位置装上后一个 skill 都加载不到"
            )
    skills_root = repo_root / "skills"
    if not (skills_root / PROFILE_SPEC_REL).exists():
        errors.append(
            f"skills/{PROFILE_SPEC_REL} 不存在——学科档案规格是四个可变点的收口处，"
            "缺了它题型集/验证手段/认知动词/章内段义会重新弥散回各 skill"
        )
    elif not any((skills_root / PROFILE_DIR_REL).glob("*.md")):
        errors.append(
            f"skills/{PROFILE_DIR_REL}/ 下没有任何档案——至少要有一份，否则阶段 1 无档案可选"
        )
    return errors


def main() -> int:
    if len(sys.argv) > 1:
        # 显式传入任意 skills 目录：只校验 skill 结构（该目录未必属于本仓库布局）
        skills_root = Path(sys.argv[1])
        repo_root = None
    else:
        repo_root = Path(__file__).resolve().parent.parent
        skills_root = repo_root / "skills"
    if not skills_root.is_dir():
        print(f"❌ skills 目录不存在：{skills_root}")
        return 1
    errors = validate(skills_root) + validate_subject_profiles(skills_root)
    if repo_root is not None:
        errors += validate_manifests(repo_root)
        errors += validate_repo_health(repo_root)
    if errors:
        for e in errors:
            print(f"❌ {e}")
        return 1
    n_skills = sum(1 for d in skills_root.iterdir() if d.is_dir())
    n_md = sum(1 for _ in skills_root.rglob("*.md"))
    n_profiles = len(list((skills_root / PROFILE_DIR_REL).glob("*.md")))
    suffix = "，三宿主六份 plugin 清单一致" if repo_root is not None else ""
    print(
        f"✅ 校验通过：{n_skills} 个 skill，{n_md} 个 markdown 文件，"
        f"{n_profiles} 份学科档案{suffix}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
