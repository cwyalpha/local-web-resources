#!/usr/bin/env python3
"""Validate documented paths, curated entrypoints, and CSS subresources."""

import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_SERVER_DIR = DEFAULT_SKILL_DIR.parent / "web-resources-server"
BASE_PATH_RE = re.compile(r"\{BASE_URL\}/([A-Za-z0-9_./@+\-]+)")
CSS_URL_RE = re.compile(r"url\(\s*([\"']?)(.*?)\1\s*\)", re.IGNORECASE)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-dir", type=Path, default=DEFAULT_SKILL_DIR)
    parser.add_argument("--server-dir", type=Path, default=DEFAULT_SERVER_DIR)
    parser.add_argument("--node-check", action="store_true", help="Parse-check curated classic JS entrypoints.")
    return parser.parse_args()


def documented_paths(skill_dir: Path) -> set[str]:
    paths = set()
    for markdown in [skill_dir / "SKILL.md", *sorted((skill_dir / "components").glob("*.md")), *sorted((skill_dir / "references").glob("*.md"))]:
        if markdown.is_file():
            paths.update(BASE_PATH_RE.findall(markdown.read_text(encoding="utf-8")))
    return paths


def entrypoints(skill_dir: Path) -> list[dict]:
    index = json.loads((skill_dir / "components" / "index.json").read_text(encoding="utf-8"))
    entries = []
    for libraries in index["categories"].values():
        for library in libraries:
            for entry in [*library.get("entrypoints", []), *library.get("optional_entrypoints", [])]:
                entries.append({"library": library["name"], **entry})
    return entries


def css_subresources(server_dir: Path) -> list[tuple[Path, str, Path]]:
    missing = []
    for css_file in sorted(path for path in server_dir.rglob("*.css") if path.is_file()):
        text = css_file.read_text(encoding="utf-8", errors="replace")
        for _, raw_url in CSS_URL_RE.findall(text):
            value = unquote(raw_url.strip())
            if not value or value.startswith(("data:", "http:", "https:", "//", "#")):
                continue
            value = value.split("#", 1)[0].split("?", 1)[0]
            target = (css_file.parent / value).resolve()
            if server_dir not in target.parents and target != server_dir:
                missing.append((css_file, raw_url, target))
            elif not target.is_file():
                missing.append((css_file, raw_url, target))
    return missing


def main():
    args = parse_args()
    skill_dir = args.skill_dir.expanduser().resolve()
    server_dir = args.server_dir.expanduser().resolve()
    failures = []

    docs = documented_paths(skill_dir)
    directory_settings = {"libs/js-core/katex"}  # Reveal's local package root.
    missing_docs = sorted(path for path in docs if not (
        (server_dir / path).is_dir() if path in directory_settings else (server_dir / path).is_file()
    ))
    failures.extend(f"documented path missing: {path}" for path in missing_docs)

    curated = entrypoints(skill_dir)
    missing_entries = [entry for entry in curated if not (server_dir / entry["path"]).is_file()]
    failures.extend(
        f"curated entrypoint missing: {entry['library']}: {entry['path']}"
        for entry in missing_entries
    )

    css_missing = css_subresources(server_dir)
    failures.extend(
        f"CSS subresource missing: {css.relative_to(server_dir)} -> {url}"
        for css, url, _ in css_missing
    )

    node_failures = []
    if args.node_check:
        checked = set()
        for entry in curated:
            if entry["kind"] != "js" or not entry["path"].endswith(".js") or entry["path"] in checked:
                continue
            checked.add(entry["path"])
            result = subprocess.run(
                ["node", "--check", str(server_dir / entry["path"])],
                capture_output=True,
                text=True,
            )
            if result.returncode:
                node_failures.append(f"{entry['path']}: {result.stderr.strip()}")
        failures.extend(f"JS parse failed: {failure}" for failure in node_failures)

    print(f"Documented paths: {len(docs)}")
    print(f"Curated entrypoints: {len(curated)}")
    print(f"CSS subresource failures: {len(css_missing)}")
    if args.node_check:
        print(f"Curated JS parse failures: {len(node_failures)}")

    if failures:
        print("\nFAILED")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("\nOK: all documented paths, curated entrypoints, and CSS subresources are available.")


if __name__ == "__main__":
    main()
