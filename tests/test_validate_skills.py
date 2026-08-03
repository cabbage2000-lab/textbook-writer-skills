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


CODEX_INTERFACE = {
    "displayName": "Demo",
    "shortDescription": "演示",
    "longDescription": "演示 plugin 的长描述。",
    "developerName": "demo-dev",
    "category": "Productivity",
    "capabilities": ["Read"],
    "defaultPrompt": ["写一本教材"],
}


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def make_manifests(root: Path, *, plugin: dict | None = None,
                   marketplace: dict | None = None,
                   codex_plugin: dict | None = None,
                   codex_marketplace: dict | None = None,
                   codebuddy_plugin: dict | None = None,
                   codebuddy_marketplace: dict | None = None) -> None:
    """造齐三宿主六份清单：默认全部同源一致（各测试再按需污染其中一份）。"""
    if plugin is None:
        plugin = {"name": "demo", "version": "0.1.0", "description": "演示 plugin"}
    if marketplace is None:
        marketplace = {"name": "demo-market", "plugins": [dict(plugin)]}
    if codex_plugin is None:
        codex_plugin = dict(
            plugin, skills="./skills/", interface=dict(CODEX_INTERFACE))
    if codex_marketplace is None:
        codex_marketplace = {
            "name": "demo-market",
            "plugins": [{
                "name": plugin["name"],
                "source": {"source": "local", "path": "./"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_USE"},
            }],
        }
    if codebuddy_plugin is None:
        codebuddy_plugin = dict(plugin)
    if codebuddy_marketplace is None:
        codebuddy_marketplace = {
            "name": "demo-market",
            "owner": {"name": "demo-dev"},
            "plugins": [dict(plugin, source="./")],
        }
    _write_json(root / ".claude-plugin" / "plugin.json", plugin)
    _write_json(root / ".claude-plugin" / "marketplace.json", marketplace)
    _write_json(root / ".codex-plugin" / "plugin.json", codex_plugin)
    _write_json(root / ".agents" / "plugins" / "marketplace.json", codex_marketplace)
    _write_json(root / ".codebuddy-plugin" / "plugin.json", codebuddy_plugin)
    _write_json(root / ".codebuddy-plugin" / "marketplace.json", codebuddy_marketplace)


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


class ValidateCodexManifestsTest(TempDirTest):
    """Codex 侧两份清单：与 Claude 侧同源 + Codex 专有的摄取要求。"""

    def test_missing_codex_manifest_reported(self):
        make_manifests(self.root)
        (self.root / ".codex-plugin" / "plugin.json").unlink()
        errors = validate_manifests(self.root)
        self.assertTrue(any(".codex-plugin/plugin.json" in e for e in errors))

    def test_cross_host_version_drift_detected(self):
        plugin = {"name": "demo", "version": "0.2.0", "description": "演示 plugin"}
        codex = dict(plugin, version="0.1.0", skills="./skills/",
                     interface=dict(CODEX_INTERFACE))
        make_manifests(self.root, plugin=plugin, codex_plugin=codex)
        errors = validate_manifests(self.root)
        self.assertTrue(any("跨宿主 plugin 清单的 version 不一致" in e for e in errors))

    def test_wrong_skills_pointer_detected(self):
        plugin = {"name": "demo", "version": "0.1.0", "description": "演示 plugin"}
        codex = dict(plugin, skills="./.codex-plugin/skills/",
                     interface=dict(CODEX_INTERFACE))
        make_manifests(self.root, plugin=plugin, codex_plugin=codex)
        errors = validate_manifests(self.root)
        self.assertTrue(any("skills 指针" in e for e in errors))

    def test_incomplete_interface_detected(self):
        plugin = {"name": "demo", "version": "0.1.0", "description": "演示 plugin"}
        interface = {k: v for k, v in CODEX_INTERFACE.items()
                     if k != "longDescription"}
        codex = dict(plugin, skills="./skills/", interface=interface)
        make_manifests(self.root, plugin=plugin, codex_plugin=codex)
        errors = validate_manifests(self.root)
        self.assertTrue(any("longDescription" in e for e in errors))

    def test_missing_interface_detected(self):
        plugin = {"name": "demo", "version": "0.1.0", "description": "演示 plugin"}
        make_manifests(self.root, plugin=plugin,
                       codex_plugin=dict(plugin, skills="./skills/"))
        errors = validate_manifests(self.root)
        self.assertTrue(any("缺少 interface 块" in e for e in errors))

    def test_codex_marketplace_entry_missing_detected(self):
        make_manifests(self.root, codex_marketplace={"name": "m", "plugins": []})
        errors = validate_manifests(self.root)
        self.assertTrue(any(".agents/plugins/marketplace.json" in e for e in errors))

    def test_codex_marketplace_source_shape_checked(self):
        make_manifests(self.root, codex_marketplace={
            "name": "m",
            "plugins": [{
                "name": "demo",
                "source": "./",  # Claude 版的写法，Codex 要对象
                "policy": {"installation": "AVAILABLE"},
            }],
        })
        errors = validate_manifests(self.root)
        self.assertTrue(any("source=" in e for e in errors))

    def test_codex_marketplace_policy_checked(self):
        make_manifests(self.root, codex_marketplace={
            "name": "m",
            "plugins": [{
                "name": "demo",
                "source": {"source": "local", "path": "./"},
                "policy": {"installation": "UNAVAILABLE"},
            }],
        })
        errors = validate_manifests(self.root)
        self.assertTrue(any("AVAILABLE" in e for e in errors))


class ValidateCodebuddyManifestsTest(TempDirTest):
    """WorkBuddy（CodeBuddy 内核）侧两份清单：结构与 Claude 版同构，另放一个目录。"""

    def test_missing_codebuddy_manifest_reported(self):
        make_manifests(self.root)
        (self.root / ".codebuddy-plugin" / "marketplace.json").unlink()
        errors = validate_manifests(self.root)
        self.assertTrue(
            any(".codebuddy-plugin/marketplace.json" in e for e in errors))

    def test_cross_host_description_drift_detected(self):
        plugin = {"name": "demo", "version": "0.1.0", "description": "演示 plugin"}
        make_manifests(self.root, plugin=plugin,
                       codebuddy_plugin=dict(plugin, description="改过的描述"))
        errors = validate_manifests(self.root)
        self.assertTrue(any(
            ".codebuddy-plugin/plugin.json" in e and "description" in e
            for e in errors))

    def test_missing_owner_detected(self):
        plugin = {"name": "demo", "version": "0.1.0", "description": "演示 plugin"}
        make_manifests(self.root, plugin=plugin, codebuddy_marketplace={
            "name": "m", "plugins": [dict(plugin, source="./")],
        })
        errors = validate_manifests(self.root)
        self.assertTrue(any("owner.name" in e for e in errors))

    def test_wrong_source_detected(self):
        plugin = {"name": "demo", "version": "0.1.0", "description": "演示 plugin"}
        make_manifests(self.root, plugin=plugin, codebuddy_marketplace={
            "name": "m",
            "owner": {"name": "demo-dev"},
            "plugins": [dict(plugin, source="./plugins/demo")],
        })
        errors = validate_manifests(self.root)
        self.assertTrue(any("必须是 './'" in e for e in errors))


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

    def test_ignoring_other_manifest_dirs_rejected(self):
        (self.root / ".gitignore").write_text(
            ".codex-plugin/\n.agents\n.codebuddy-plugin\n", encoding="utf-8")
        errors = validate_repo_health(self.root)
        self.assertTrue(any(".codex-plugin" in e for e in errors))
        self.assertTrue(any(".agents" in e for e in errors))
        self.assertTrue(any(".codebuddy-plugin" in e for e in errors))

    def test_skills_inside_manifest_dir_rejected(self):
        """skills/ 塞进清单目录：插件装得上、但一个 skill 都加载不到。"""
        (self.root / ".codex-plugin" / "skills" / "demo").mkdir(parents=True)
        (self.root / ".codex-plugin" / "plugin.json").write_text(
            "{}", encoding="utf-8")
        errors = validate_repo_health(self.root)
        self.assertTrue(any("只放清单文件" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
