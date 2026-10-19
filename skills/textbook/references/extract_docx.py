#!/usr/bin/env python3
"""Extract locatable text from a .docx file using only the Python standard library."""

import argparse
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MAX_DOCUMENT_XML_BYTES = 20 * 1024 * 1024


def paragraph_text(paragraph: ET.Element) -> str:
    """Read text in document order, including runs inside hyperlinks."""
    parts = []
    for node in paragraph.iter():
        if node.tag == W + "t":
            parts.append(node.text or "")
        elif node.tag == W + "tab":
            parts.append("\t")
        elif node.tag in (W + "br", W + "cr"):
            parts.append("\n")
    return "".join(parts).strip()


def extract_docx(path: Path) -> str:
    """Return body paragraphs and table cells with stable structural locators."""
    try:
        with zipfile.ZipFile(path) as archive:
            info = archive.getinfo("word/document.xml")
            if info.file_size > MAX_DOCUMENT_XML_BYTES:
                raise ValueError("document.xml is too large to extract safely")
            root = ET.fromstring(archive.read(info))
    except (zipfile.BadZipFile, KeyError, ET.ParseError, RuntimeError) as exc:
        raise ValueError("not a readable .docx document") from exc

    body = root.find(W + "body")
    if body is None:
        raise ValueError(".docx document has no body")

    lines = []
    paragraph_number = 0
    table_number = 0
    for block in body:
        if block.tag == W + "p":
            paragraph_number += 1
            value = paragraph_text(block)
            if value:
                lines.append(f"[P{paragraph_number}] {value}")
        elif block.tag == W + "tbl":
            table_number += 1
            for row_number, row in enumerate(block.findall(W + "tr"), 1):
                for cell_number, cell in enumerate(row.findall(W + "tc"), 1):
                    value = " / ".join(
                        text for paragraph in cell.findall(".//" + W + "p")
                        if (text := paragraph_text(paragraph))
                    )
                    if value:
                        lines.append(f"[T{table_number}R{row_number}C{cell_number}] {value}")
    if not lines:
        raise ValueError(".docx body contains no extractable text")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="local .docx file")
    parser.add_argument("--output", type=Path, help="save extracted UTF-8 text")
    args = parser.parse_args()
    try:
        content = extract_docx(args.source)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content, encoding="utf-8")
        else:
            sys.stdout.write(content)
    except (OSError, ValueError) as exc:
        print(f"DOCX extraction failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
