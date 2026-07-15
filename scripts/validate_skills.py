#!/usr/bin/env python3
"""校验本仓库的结构完整性：skills/ 内容质量 + plugin 清单一致性 + 仓库健康。

skill 结构检查（validate）：
1. 每个 skill 目录含 SKILL.md，frontmatter 的 name 与目录名一致、description ≥ 50 字符
2. description ≤ 1024 字符（Claude Code 对 frontmatter description 的硬限制）
3. frontmatter 仅含白名单字段（防手误写入无效字段被静默忽略）
4. SKILL.md ≤ 500 行（渐进披露预算：超限内容应下沉到 references/）
5. 所有 .md 文件不含占位符（TBD/TODO/FIXME/XXX/待补充/占位）
6. SKILL.md 中引用的 references/ 相对路径（含 ../ 跨 skill）都存在
7. references 下每个 .md 实质内容 ≥ 500 字节

plugin 清单检查（validate_manifests）：
8. plugin.json 与 marketplace.json 都存在且可解析
9. 两份清单的 name / version / description 一致（手工重复维护最易漂移处）

仓库健康检查（validate_repo_health）：
10. .gitignore 不得忽略 .claude-plugin（分发清单必须入库，否则 plugin 装不出去）

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
REF_LINK_RE = re.compile(r"[(`]((?:\.\./[\w-]+/)?references/[\w./-]+?\.md)[)`]")


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


def _load_json(path: Path, errors: list[str]) -> dict | None:
    if not path.exists():
        errors.append(f"{path.name}: 文件不存在")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"{path.name}: JSON 解析失败（{e}）")
        return None


def validate_manifests(repo_root: Path) -> list[str]:
    """plugin.json 与 marketplace.json 是同一份元数据的两份手工拷贝，强制同步。"""
    errors: list[str] = []
    manifest_dir = repo_root / ".claude-plugin"
    plugin = _load_json(manifest_dir / "plugin.json", errors)
    marketplace = _load_json(manifest_dir / "marketplace.json", errors)
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
            if line.rstrip("/") == ".claude-plugin":
                errors.append(
                    ".gitignore: 忽略了 .claude-plugin——plugin 分发清单"
                    "必须入库，该目录被忽略会导致新增清单文件静默丢失"
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
    errors = validate(skills_root)
    if repo_root is not None:
        errors += validate_manifests(repo_root)
        errors += validate_repo_health(repo_root)
    if errors:
        for e in errors:
            print(f"❌ {e}")
        return 1
    n_skills = sum(1 for d in skills_root.iterdir() if d.is_dir())
    n_md = sum(1 for _ in skills_root.rglob("*.md"))
    suffix = "，清单一致" if repo_root is not None else ""
    print(f"✅ 校验通过：{n_skills} 个 skill，{n_md} 个 markdown 文件{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
