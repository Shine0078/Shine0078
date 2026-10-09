#!/usr/bin/env python3
"""Validate the published GitHub profile's local assets and public links."""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
BANNER = ROOT / "assets" / "hero.svg"


def main() -> int:
    content = README.read_text(encoding="utf-8")
    if len(content) < 1000:
        raise ValueError("Profile README appears incomplete")
    if "Shine0078" not in content or "barcode-studio" not in content:
        raise ValueError("Missing account identity or real project showcase")
    if "assets/hero.svg" not in content:
        raise ValueError("Original banner must be linked in README")
    for relative in re.findall(r'''(?:src|href)=["']\./([^"'#?]+)["']''', content):
        if not (ROOT / relative).is_file():
            raise FileNotFoundError(f"Broken relative asset: {relative}")
    root = ET.parse(BANNER).getroot()
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("Banner is not a valid SVG")
    if "viewBox" not in root.attrib:
        raise ValueError("Banner needs a responsive viewBox")
    if re.search(r"(?i)javascript:|<script\b|github_pat_|ghp_", content):
        raise ValueError("Unsafe executable URL/script or credential-like text")
    internal_links = re.findall(r"\]\(#([a-z0-9-]+)\)", content)
    for slug in internal_links:
        if not re.search(r"^#{2,6}\s+.*" + re.escape(slug.replace("-", ".*")) , content, flags=re.MULTILINE | re.IGNORECASE):
            # GitHub heading slugs can differ for Unicode glyphs. Verify
            # anchors conservatively against expected section titles.
            expected = {"-selected-builds": "Selected builds", "-toolkit": "Toolkit",
                        "-under-the-hood": "Under the hood", "-the-build-log": "The build log"}
            if slug in expected and expected[slug].lower() not in content.lower():
                raise ValueError(f"Broken navigation destination: {slug}")
    print("Profile validation passed: local assets, original SVG, public content, navigation.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, FileNotFoundError, ET.ParseError) as error:
        print(f"Profile validation failed: {error}", file=sys.stderr)
        sys.exit(1)
