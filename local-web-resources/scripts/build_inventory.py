#!/usr/bin/env python3
"""Build a machine-readable inventory for the HTTP resource server."""

import argparse
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SERVER_DIR = SCRIPT_DIR.parent.parent / "web-resources-server"
EXCLUDED_SERVER_FILES = {
    Path("libs/editors/codemirror/addon/mode/multiplex_test.min.js"),
    Path("libs/layout/gridstack.js/vitest.config.min.js"),
    Path("libs/layout/gridstack.js/vitest.setup.min.js"),
}


def scan_tree(root: Path, base: Path) -> list[dict]:
    entries = []
    if not root.is_dir():
        return entries
    for directory in sorted(path for path in root.iterdir() if path.is_dir()):
        files = sorted(
            path
            for path in directory.rglob("*")
            if path.is_file() and path.relative_to(base) not in EXCLUDED_SERVER_FILES
        )
        entries.append(
            {
                "name": directory.name,
                "directory": directory.relative_to(base).as_posix(),
                "file_count": len(files),
                "total_size_kb": round(sum(path.stat().st_size for path in files) / 1024, 1),
                "extensions": sorted({path.suffix.lower() for path in files if path.suffix}),
            }
        )
    return entries


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-dir", type=Path, default=DEFAULT_SERVER_DIR)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main():
    args = parse_args()
    server_dir = args.server_dir.expanduser().resolve()
    output = args.output.expanduser().resolve() if args.output else server_dir / "inventory.json"
    libs_dir = server_dir / "libs"
    fonts_dir = server_dir / "fonts"
    if not libs_dir.is_dir() or not fonts_dir.is_dir():
        raise SystemExit(f"Expected libs/ and fonts/ under {server_dir}")

    libraries = []
    for category_dir in sorted(path for path in libs_dir.iterdir() if path.is_dir()):
        for library in scan_tree(category_dir, server_dir):
            library["category"] = category_dir.name
            libraries.append(library)
    fonts = scan_tree(fonts_dir, server_dir)

    inventory = {
        "schema_version": 2,
        "description": "Local HTTP web resource server inventory",
        "summary": {
            "library_count": len(libraries),
            "font_family_count": len(fonts),
            "total_size_mb": round(
                (sum(item["total_size_kb"] for item in libraries) + sum(item["total_size_kb"] for item in fonts))
                / 1024,
                1,
            ),
        },
        "libraries": libraries,
        "fonts": fonts,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output}: {len(libraries)} libraries, {len(fonts)} font families")


if __name__ == "__main__":
    main()
