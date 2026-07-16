#!/usr/bin/env python3
"""从 CHANGELOG.md 摘取指定版本对应的段落，供 release workflow 生成 Release notes。

CHANGELOG.md 遵循 Keep a Changelog 格式：每个版本一个 `## [x.y.z] - date` 标题，
版本段边界就是相邻两个 `## [` 标题行之间的区间。

用法：python3 scripts/extract_changelog_notes.py <version>
<version> 不带 v 前缀（如 0.1.0），与 CHANGELOG 里 `[0.1.0]` 的写法一致。

找不到对应版本段，或摘取内容为空/纯空白，都会以非 0 退出码结束并向 stderr 报错——
不允许产出空白或不完整的 Release notes。
"""
import re
import sys
from pathlib import Path

ANY_VERSION_HEADING_RE = re.compile(r"^## \[", re.MULTILINE)


def extract_section(changelog_text: str, version: str) -> str | None:
    """返回 `version` 对应的段落正文（不含标题行本身）；找不到返回 None。"""
    heading_re = re.compile(
        r"^## \[" + re.escape(version) + r"\].*$", re.MULTILINE
    )
    m = heading_re.search(changelog_text)
    if m is None:
        return None
    start = m.end()
    next_heading = ANY_VERSION_HEADING_RE.search(changelog_text, pos=start)
    end = next_heading.start() if next_heading else len(changelog_text)
    return changelog_text[start:end].strip()


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "用法：python3 scripts/extract_changelog_notes.py <version>",
            file=sys.stderr,
        )
        return 1
    version = sys.argv[1]
    repo_root = Path(__file__).resolve().parent.parent
    changelog_path = repo_root / "CHANGELOG.md"
    if not changelog_path.is_file():
        print(f"❌ 找不到 {changelog_path}", file=sys.stderr)
        return 1
    text = changelog_path.read_text(encoding="utf-8")
    section = extract_section(text, version)
    if section is None:
        print(
            f"❌ CHANGELOG.md 中找不到版本 [{version}] 对应的段落",
            file=sys.stderr,
        )
        return 1
    if not section:
        print(
            f"❌ CHANGELOG.md 中版本 [{version}] 对应的段落内容为空",
            file=sys.stderr,
        )
        return 1
    print(section)
    return 0


if __name__ == "__main__":
    sys.exit(main())
