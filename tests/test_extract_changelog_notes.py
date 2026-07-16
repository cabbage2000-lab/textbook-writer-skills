#!/usr/bin/env python3
"""extract_changelog_notes.py 的单元测试：验证 CHANGELOG 版本段摘取逻辑。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from extract_changelog_notes import extract_section  # noqa: E402

SAMPLE_CHANGELOG = """# Changelog

## [Unreleased]

### Added

- 新特性 A

## [0.2.0] - 2026-08-01

### Added

- 特性 B

### Fixed

- 修复 C

## [0.1.0] - 2026-07-14

### Added

- M1 骨架
"""


class ExtractSectionTest(unittest.TestCase):
    def test_extracts_middle_version_section(self):
        section = extract_section(SAMPLE_CHANGELOG, "0.2.0")
        self.assertIn("### Added", section)
        self.assertIn("特性 B", section)
        self.assertIn("### Fixed", section)
        self.assertIn("修复 C", section)
        self.assertNotIn("特性 A", section)
        self.assertNotIn("M1 骨架", section)

    def test_extracts_last_version_section_to_eof(self):
        section = extract_section(SAMPLE_CHANGELOG, "0.1.0")
        self.assertIn("M1 骨架", section)

    def test_returns_none_for_missing_version(self):
        self.assertIsNone(extract_section(SAMPLE_CHANGELOG, "9.9.9"))

    def test_returns_empty_string_for_heading_with_no_body(self):
        text = "## [0.3.0]\n## [0.2.0]\n\nbody\n"
        self.assertEqual(extract_section(text, "0.3.0"), "")


if __name__ == "__main__":
    unittest.main()
