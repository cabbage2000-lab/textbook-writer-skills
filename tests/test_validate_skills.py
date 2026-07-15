#!/usr/bin/env python3
"""validate_skills.py 的单元测试。用临时目录构造好/坏结构，验证校验逻辑。"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from validate_skills import (  # noqa: E402
    validate,
    validate_manifests,
    validate_repo_health,
)

GOOD_DESC = (
    "Use when generating verified STEM exercises with Bloom-level tags "
    "— e.g. 出几道练习题. Not for essay questions."
)


def make_skill(root: Path, name: str, *, frontmatter_name: str | None = None,
               description: str = GOOD_DESC, body: str = "# 正文\n内容充实。\n",
               extra_frontmatter: str = "",
               refs: dict[str, str] | None = None) -> Path:
    d = root / name
    (d / "references").mkdir(parents=True, exist_ok=True)
    fm_name = frontmatter_name if frontmatter_name is not None else name
    (d / "SKILL.md").write_text(
        f"---\nname: {fm_name}\ndescription: {description}\n"
        f"{extra_frontmatter}---\n\n{body}",
        encoding="utf-8",
    )
    for ref_name, ref_content in (refs or {}).items():
        (d / "references" / ref_name).write_text(ref_content, encoding="utf-8")
    return d


def make_manifests(root: Path, *, plugin: dict | None = None,
                   marketplace: dict | None = None) -> None:
    manifest_dir = root / ".claude-plugin"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    if plugin is None:
        plugin = {"name": "demo", "version": "0.1.0", "description": "演示 plugin"}
    if marketplace is None:
        marketplace = {"name": "demo-market", "plugins": [dict(plugin)]}
    (manifest_dir / "plugin.json").write_text(
        json.dumps(plugin, ensure_ascii=False), encoding="utf-8")
    (manifest_dir / "marketplace.json").write_text(
        json.dumps(marketplace, ensure_ascii=False), encoding="utf-8")


class TempDirTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()


class ValidateSkillsTest(TempDirTest):
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

    def test_overlong_description_rejected(self):
        make_skill(self.root, "skill-a", description="长" * 1025)
        errors = validate(self.root)
        self.assertTrue(any("超长" in e for e in errors))

    def test_unknown_frontmatter_key_rejected(self):
        make_skill(self.root, "skill-a", extra_frontmatter="trigger: always\n")
        errors = validate(self.root)
        self.assertTrue(any("未知字段" in e for e in errors))

    def test_oversized_skill_md_rejected(self):
        make_skill(self.root, "skill-a", body="# 正文\n" + "一行。\n" * 501)
        errors = validate(self.root)
        self.assertTrue(any("超出预算" in e for e in errors))

    def test_placeholder_detected(self):
        make_skill(self.root, "skill-a", body="# 正文\nTODO: 这里尚未完成。\n")
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


class ValidateManifestsTest(TempDirTest):
    def test_consistent_manifests_pass(self):
        make_manifests(self.root)
        self.assertEqual(validate_manifests(self.root), [])

    def test_missing_manifest_reported(self):
        errors = validate_manifests(self.root)
        self.assertTrue(any("plugin.json" in e for e in errors))

    def test_version_drift_detected(self):
        plugin = {"name": "demo", "version": "0.2.0", "description": "演示 plugin"}
        market_entry = {"name": "demo", "version": "0.1.0", "description": "演示 plugin"}
        make_manifests(self.root, plugin=plugin,
                       marketplace={"name": "m", "plugins": [market_entry]})
        errors = validate_manifests(self.root)
        self.assertTrue(any("version 不一致" in e for e in errors))

    def test_license_drift_detected(self):
        plugin = {"name": "demo", "version": "0.1.0",
                  "description": "演示 plugin", "license": "MIT"}
        market_entry = dict(plugin, license="Apache-2.0")
        make_manifests(self.root, plugin=plugin,
                       marketplace={"name": "m", "plugins": [market_entry]})
        errors = validate_manifests(self.root)
        self.assertTrue(any("license 不一致" in e for e in errors))

    def test_missing_marketplace_entry_detected(self):
        make_manifests(self.root, marketplace={"name": "m", "plugins": []})
        errors = validate_manifests(self.root)
        self.assertTrue(any("找不到" in e for e in errors))

    def test_invalid_json_reported(self):
        make_manifests(self.root)
        (self.root / ".claude-plugin" / "plugin.json").write_text(
            "{broken", encoding="utf-8")
        errors = validate_manifests(self.root)
        self.assertTrue(any("解析失败" in e for e in errors))


class ValidateRepoHealthTest(TempDirTest):
    def test_clean_gitignore_passes(self):
        (self.root / ".gitignore").write_text(
            ".DS_Store\n.claude/\n", encoding="utf-8")
        self.assertEqual(validate_repo_health(self.root), [])

    def test_ignoring_claude_plugin_rejected(self):
        (self.root / ".gitignore").write_text(
            ".claude/\n.claude-plugin\n", encoding="utf-8")
        errors = validate_repo_health(self.root)
        self.assertTrue(any(".claude-plugin" in e for e in errors))

    def test_ignoring_claude_plugin_with_slash_rejected(self):
        (self.root / ".gitignore").write_text(
            ".claude-plugin/\n", encoding="utf-8")
        errors = validate_repo_health(self.root)
        self.assertTrue(any(".claude-plugin" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
