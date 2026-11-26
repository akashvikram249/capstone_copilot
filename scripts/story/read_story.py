#!/usr/bin/env python3
"""Print a user story from a .txt, .md or .docx file as plain text (no dependencies).

Usage: python3 scripts/story/read_story.py <file> [--copy]
  --copy  also copy the text to the macOS clipboard (for pasting into CodeMie).
"""
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def paragraph_text(p):
    parts = []
    for node in p.iter():
        if node.tag == W + "t":
            parts.append(node.text or "")
        elif node.tag == W + "tab":
            parts.append("\t")
        elif node.tag in (W + "br", W + "cr"):
            parts.append("\n")
    return "".join(parts)


def docx_text(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(W + "body")
    lines = []
    for el in body:
        if el.tag == W + "p":
            style = el.find(f"{W}pPr/{W}pStyle")
            text = paragraph_text(el).strip()
            if style is not None and text:
                val = style.get(W + "val", "")
                m = re.match(r"Heading(\d)", val)
                if m:
                    text = "#" * int(m.group(1)) + " " + text
            if el.find(f"{W}pPr/{W}numPr") is not None and text:
                text = "- " + text
            lines.append(text)
        elif el.tag == W + "tbl":
            for row in el.iter(W + "tr"):
                cells = [" ".join(paragraph_text(p).strip() for p in c.iter(W + "p")).strip()
                         for c in row.findall(W + "tc")]
                lines.append(" | ".join(cells))
            lines.append("")
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    path = Path(args[0]).expanduser()
    if not path.is_file():
        sys.exit(f"Story file not found: {path}")
    ext = path.suffix.lower()
    if ext in (".txt", ".md", ".markdown", ""):
        text = path.read_text(encoding="utf-8", errors="replace")
    elif ext == ".docx":
        try:
            text = docx_text(path)
        except (zipfile.BadZipFile, KeyError, ET.ParseError):
            sys.exit(f"Could not read {path} as a Word .docx file. Save it as .docx, .txt or .md and retry.")
    else:
        sys.exit(f"Unsupported story file type '{ext}'. Use .txt, .md or .docx.")
    if not text.strip():
        sys.exit(f"{path} contains no text.")
    sys.stdout.write(text)
    if "--copy" in sys.argv:
        try:
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
            print("\n[copied to clipboard]", file=sys.stderr)
        except (OSError, subprocess.CalledProcessError):
            print("\n[clipboard copy unavailable here]", file=sys.stderr)


if __name__ == "__main__":
    main()
