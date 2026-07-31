#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_font_css.py
Generate proper @font-face CSS for all Chinese font subset files.
Fetches unicode-range from CDN CSS, rewrites paths to local.
If CDN is unavailable, generates fallback CSS without unicode-range.
"""

import argparse
import re
import ssl
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SERVER_DIR = SCRIPT_DIR.parent.parent / "web-resources-server"
FONTS_DIR = DEFAULT_SERVER_DIR / "fonts"

ssl_ctx = ssl.create_default_context()


def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        print(f"  [WARN] Failed to fetch {url}: {e}")
        return None


# ============================================================
# Generic @font-face parser
# ============================================================
def parse_fontface_blocks(css_text):
    """Parse all @font-face blocks from CSS text."""
    results = []
    pattern = re.compile(r'@font-face\s*\{([^}]+)\}', re.DOTALL)
    for match in pattern.finditer(css_text):
        block = match.group(1)
        ff = re.search(r"font-family:\s*['\"]([^'\"]+)['\"]", block)
        fw = re.search(r'font-weight:\s*(\d+)', block)
        fs = re.search(r"font-style:\s*(\w+)", block)
        ur = re.search(r'unicode-range:\s*([^;]+);', block)
        src = re.search(r"url\(['\"]?([^)'\"]+'?)['\"]?\)", block)

        if ff and src:
            src_url = src.group(1).strip("'\"")
            # Extract just the filename
            filename = src_url.split("/")[-1]
            results.append({
                "family": ff.group(1),
                "weight": fw.group(1) if fw else "400",
                "style": fs.group(1) if fs else "normal",
                "filename": filename,
                "unicode_range": ur.group(1).strip() if ur else None,
            })
    return results


def generate_fontface_css(entries, font_dir_name, font_dir_path):
    """Generate @font-face CSS with local paths."""
    css_lines = []
    for entry in entries:
        local_path = font_dir_path / entry["filename"]
        if not local_path.exists():
            continue

        rel_url = f"./{font_dir_name}/{entry['filename']}"
        ur_line = f"\n  unicode-range: {entry['unicode_range']};" if entry["unicode_range"] else ""

        css_lines.append(f"""@font-face {{
  font-family: '{entry["family"]}';
  font-style: {entry["style"]};
  font-weight: {entry["weight"]};
  font-display: swap;
  src: url('{rel_url}') format('woff2');{ur_line}
}}""")
    return "\n\n".join(css_lines)


def generate_fallback_for_dir(font_dir_name, family_name, font_dir):
    """Generate @font-face without unicode-range by scanning files."""
    css_lines = []
    for f in sorted(font_dir.glob("*.woff2")):
        # Guess weight from filename
        name_lower = f.name.lower()
        if "bold" in name_lower or "-700-" in name_lower:
            weight = "700"
        elif "light" in name_lower or "-300-" in name_lower:
            weight = "300"
        else:
            weight = "400"

        css_lines.append(f"""@font-face {{
  font-family: '{family_name}';
  font-style: normal;
  font-weight: {weight};
  font-display: swap;
  src: url('./{font_dir_name}/{f.name}') format('woff2');
}}""")
    return "\n\n".join(css_lines)


# ============================================================
# Font configurations
# ============================================================
FONT_CONFIGS = [
    {
        "dir_name": "noto-sans-sc",
        "family": "Noto Sans SC",
        "css_urls": [
            "https://cdn.jsdelivr.net/npm/@fontsource/noto-sans-sc@5/400.css",
            "https://cdn.jsdelivr.net/npm/@fontsource/noto-sans-sc@5/700.css",
        ],
    },
    {
        "dir_name": "noto-serif-sc",
        "family": "Noto Serif SC",
        "css_urls": [
            "https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc@5/400.css",
            "https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc@5/700.css",
        ],
    },
    {
        "dir_name": "lxgw-wenkai",
        "family": "LXGW WenKai",
        "css_urls": [
            "https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@1.7.0/lxgwwenkai-regular.css",
            "https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@1.7.0/lxgwwenkai-bold.css",
        ],
    },
    {
        "dir_name": "lxgw-wenkai-mono",
        "family": "LXGW WenKai Mono",
        "css_urls": [
            "https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@1.7.0/lxgwwenkaimono-regular.css",
            "https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@1.7.0/lxgwwenkaimono-bold.css",
        ],
    },
    {
        "dir_name": "zhuque-fangsong",
        "family": "Zhuque Fangsong",
        "css_urls": [],
    },
]


def main():
    global FONTS_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-dir", type=Path, default=DEFAULT_SERVER_DIR)
    args = parser.parse_args()
    FONTS_DIR = args.server_dir.expanduser().resolve() / "fonts"
    if not FONTS_DIR.is_dir():
        raise SystemExit(f"Fonts directory not found: {FONTS_DIR}")

    print("=" * 60)
    print("  Generating Chinese Font CSS (@font-face)")
    print("=" * 60)

    all_sections = []
    all_sections.append("/* fonts-chinese.css */")
    all_sections.append("/* Auto-generated @font-face for Chinese web fonts */")
    all_sections.append("/* Include in HTML: <link rel=\"stylesheet\" href=\"{path}/fonts/fonts-chinese.css\"> */\n")

    total_rules = 0

    for config in FONT_CONFIGS:
        dir_name = config["dir_name"]
        family = config["family"]
        font_dir = FONTS_DIR / dir_name

        print(f"\n--- {family} ({dir_name}) ---")

        if not font_dir.exists():
            print(f"  [SKIP] Font directory not found")
            continue

        all_entries = []
        cdn_ok = False

        for url in config["css_urls"]:
            print(f"  Fetching: {url.split('/')[-1]}...")
            css_text = fetch_url(url)
            if css_text:
                entries = parse_fontface_blocks(css_text)
                all_entries.extend(entries)
                print(f"  Parsed {len(entries)} rules")
                cdn_ok = True

        if cdn_ok and all_entries:
            # Deduplicate by filename
            seen = set()
            unique = []
            for e in all_entries:
                if e["filename"] not in seen:
                    seen.add(e["filename"])
                    unique.append(e)

            css = generate_fontface_css(unique, dir_name, font_dir)
        else:
            print(f"  [FALLBACK] Generating from file scan (no unicode-range)")
            css = generate_fallback_for_dir(dir_name, family, font_dir)

        if css:
            rule_count = css.count("@font-face")
            total_rules += rule_count
            all_sections.append(f"\n/* {'=' * 50} */")
            all_sections.append(f"/* {family} ({rule_count} rules) */")
            all_sections.append(f"/* {'=' * 50} */\n")
            all_sections.append(css)
            print(f"  -> {rule_count} @font-face rules")

    # Write output
    output = FONTS_DIR / "fonts-chinese.css"
    content = "\n".join(all_sections)
    with output.open("w", encoding="utf-8", newline="\r\n") as css_file:
        css_file.write(content)

    print(f"\n{'=' * 60}")
    print(f"  Output: {output}")
    print(f"  Total: {total_rules} @font-face rules")
    print(f"  Size: {len(content.encode('utf-8')) / 1024:.1f} KB")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
