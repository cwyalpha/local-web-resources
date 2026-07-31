#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Copy additional libraries from an offline cdnjs mirror."""

import argparse
import shutil
import os
import urllib.request
import ssl
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SERVER_DIR = SCRIPT_DIR.parent.parent / "web-resources-server"
CDNJS = None
LIBS = DEFAULT_SERVER_DIR / "libs"

ssl_ctx = ssl.create_default_context()


def copy_cdnjs_lib(cdnjs_name, target_category, target_name=None, 
                    extensions=None, include_dirs=None):
    """Copy a library from cdnjs to the Skill libs directory."""
    if target_name is None:
        target_name = cdnjs_name
    if extensions is None:
        extensions = {'.min.js', '.min.css'}
    
    src_base = CDNJS / cdnjs_name
    if not src_base.exists():
        print(f"  [SKIP] {cdnjs_name} not found in cdnjs")
        return 0
    
    # Get version directory
    versions = sorted(src_base.iterdir())
    version_dir = versions[0] if versions else None
    if not version_dir:
        return 0
    
    dst = LIBS / target_category / target_name
    dst.mkdir(parents=True, exist_ok=True)
    
    copied = 0
    for f in version_dir.rglob("*"):
        if not f.is_file():
            continue
        
        name_lower = f.name.lower()
        ext = f.suffix.lower()
        
        # Check if we should include this file
        should_copy = False
        
        # Always copy .min.js and .min.css
        if name_lower.endswith('.min.js') or name_lower.endswith('.min.css'):
            should_copy = True
        
        # Copy specific extensions
        if ext in extensions:
            should_copy = True
        
        # Copy font/image files for specific dirs
        if include_dirs:
            rel = str(f.relative_to(version_dir))
            for d in include_dirs:
                if rel.startswith(d) or f"/{d}/" in rel or f"\\{d}\\" in rel:
                    should_copy = True
        
        # Copy woff/woff2/ttf for icon/font libs
        if ext in ('.woff', '.woff2', '.ttf', '.eot', '.svg', '.png', '.gif'):
            should_copy = True
        
        if should_copy:
            rel_path = f.relative_to(version_dir)
            dst_file = dst / rel_path
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst_file)
            copied += 1
    
    return copied


def download_file(url, dst_path):
    """Download a file from URL."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
            data = resp.read()
        Path(dst_path).parent.mkdir(parents=True, exist_ok=True)
        with open(dst_path, "wb") as f:
            f.write(data)
        return len(data)
    except Exception as e:
        print(f"  [FAIL] {url}: {e}")
        return 0


def main():
    global CDNJS, LIBS
    parser = argparse.ArgumentParser()
    parser.add_argument("--cdnjs-root", type=Path, required=True)
    parser.add_argument("--server-dir", type=Path, default=DEFAULT_SERVER_DIR)
    args = parser.parse_args()
    CDNJS = args.cdnjs_root.expanduser().resolve()
    LIBS = args.server_dir.expanduser().resolve() / "libs"
    if not CDNJS.is_dir():
        raise SystemExit(f"cdnjs mirror not found: {CDNJS}")
    LIBS.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  Copying additional libraries")
    print("=" * 60)
    
    # 1. KaTeX (math formulas) -> js-core category
    print("\n--- KaTeX ---")
    n = copy_cdnjs_lib("KaTeX", "js-core", "katex",
                       extensions={'.min.js', '.min.css', '.woff2', '.woff', '.ttf'})
    print(f"  Copied {n} files")
    
    # 2. reveal.js (presentations) -> layout category
    print("\n--- reveal.js ---")
    n = copy_cdnjs_lib("reveal.js", "layout", "reveal.js",
                       extensions={'.min.js', '.min.css', '.esm.min.js'})
    print(f"  Copied {n} files")
    
    # 3. Cropper.js (image cropping) -> ui-components
    print("\n--- Cropper.js ---")
    n = copy_cdnjs_lib("cropperjs", "ui-components", "cropperjs",
                       extensions={'.min.js', '.min.css'})
    print(f"  Copied {n} files")
    
    # 4. Fuse.js (fuzzy search) -> utils
    print("\n--- Fuse.js ---")
    n = copy_cdnjs_lib("fuse.js", "utils", "fuse.js",
                       extensions={'.min.js'})
    print(f"  Copied {n} files")
    
    # 5. Cytoscape (graph/network visualization) -> charts
    print("\n--- Cytoscape ---")
    n = copy_cdnjs_lib("cytoscape", "charts", "cytoscape",
                       extensions={'.min.js'})
    print(f"  Copied {n} files")
    
    # 6. jstree (tree widget) -> ui-components
    print("\n--- jstree ---")
    n = copy_cdnjs_lib("jstree", "ui-components", "jstree",
                       extensions={'.min.js', '.min.css', '.png', '.gif'})
    print(f"  Copied {n} files")
    
    # 7. markdown-it (not in cdnjs, download from jsdelivr)
    print("\n--- markdown-it ---")
    md_dir = LIBS / "js-core" / "markdown-it"
    md_dir.mkdir(parents=True, exist_ok=True)
    
    urls = [
        ("https://cdn.jsdelivr.net/npm/markdown-it@14/dist/markdown-it.min.js", 
         md_dir / "markdown-it.min.js"),
    ]
    
    for url, dst in urls:
        size = download_file(url, dst)
        if size:
            print(f"  [OK] {dst.name} ({size // 1024} KB)")
        else:
            print(f"  [FAIL] {dst.name}")
    
    # Summary
    print("\n" + "=" * 60)
    new_libs = ["katex", "reveal.js", "cropperjs", "fuse.js", "cytoscape", "jstree", "markdown-it"]
    for lib_name in new_libs:
        # Find it
        for cat in LIBS.iterdir():
            lib_dir = cat / lib_name
            if lib_dir.exists():
                files = list(lib_dir.rglob("*"))
                file_count = sum(1 for f in files if f.is_file())
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                print(f"  {lib_name}: {file_count} files, {total_size // 1024} KB")
                break
    print("=" * 60)


if __name__ == "__main__":
    main()
