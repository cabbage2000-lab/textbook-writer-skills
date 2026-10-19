"""DOCX extraction covers the content and locators used by source mapping."""

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "textbook" / "references"))
from extract_docx import extract_docx  # noqa: E402


DOCUMENT = """<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>
  <w:p><w:r><w:t>矩阵</w:t></w:r><w:hyperlink><w:r><w:t>乘法</w:t></w:r></w:hyperlink></w:p>
  <w:tbl><w:tr>
    <w:tc><w:p><w:r><w:t>行</w:t></w:r></w:p></w:tc>
    <w:tc><w:p><w:r><w:t>列</w:t></w:r></w:p></w:tc>
  </w:tr></w:tbl>
  <w:p><w:r><w:t>核对</w:t></w:r><w:r><w:tab/></w:r><w:r><w:t>答案</w:t></w:r></w:p>
</w:body></w:document>"""


class ExtractDocxTest(unittest.TestCase):
    def test_extracts_body_paragraphs_and_table_cells(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", DOCUMENT)
            self.assertEqual(
                extract_docx(path),
                "[P1] 矩阵乘法\n[T1R1C1] 行\n[T1R1C2] 列\n[P2] 核对\t答案\n",
            )

    def test_rejects_unreadable_docx(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.docx"
            path.write_text("not a docx", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not a readable"):
                extract_docx(path)


if __name__ == "__main__":
    unittest.main()
