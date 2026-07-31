#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
download_fonts.py -- Download common Chinese & English web fonts via npm packages
"""

import argparse
import subprocess
import shutil
import tempfile
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SERVER_DIR = SCRIPT_DIR.parent.parent / "web-resources-server"
FONTS_DIR = DEFAULT_SERVER_DIR / "fonts"
TEMP_DIR = None


def run_npm_install(package_name):
    """Install an npm package to temp directory and return its path."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    pkg_json = TEMP_DIR / "package.json"
    if not pkg_json.exists():
        pkg_json.write_text('{"private":true}', encoding="utf-8")
    
    print(f"  [NPM] Installing {package_name}...")
    npm_cmd = shutil.which("npm")
    if not npm_cmd:
        print("  [FAIL] npm executable not found")
        return None
    result = subprocess.run(
        [npm_cmd, "install", package_name, "--save", "--legacy-peer-deps"],
        cwd=str(TEMP_DIR),
        capture_output=True, text=True, timeout=120,
        shell=False,
    )
    if result.returncode != 0:
        print(f"  [FAIL] npm install {package_name}: {result.stderr[:200]}")
        return None
    
    if package_name.startswith("@"):
        scope, name_spec = package_name.split("/", 1)
        package_dir = Path(scope) / name_spec.rsplit("@", 1)[0]
    else:
        package_dir = Path(package_name.rsplit("@", 1)[0])

    pkg_dir = TEMP_DIR / "node_modules" / package_dir
    if pkg_dir.exists():
        return pkg_dir

    # Search in node_modules
    nm = TEMP_DIR / "node_modules"
    for d in nm.iterdir():
        if d.is_dir() and package_dir.name in d.name:
            return d
    
    print(f"  [WARN] Package installed but directory not found")
    return nm


def copy_woff2_files(src_dir, dst_dir, pattern="*.woff2"):
    """Copy woff2 files from src to dst."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in src_dir.rglob(pattern):
        if f.is_file():
            dst = dst_dir / f.name
            shutil.copy2(f, dst)
            size_kb = f.stat().st_size / 1024
            print(f"  [OK]  {f.name} ({size_kb:.0f} KB)")
            count += 1
    # Also copy .woff files as fallback
    for f in src_dir.rglob("*.woff"):
        if f.is_file():
            dst = dst_dir / f.name
            shutil.copy2(f, dst)
            count += 1
    # Also copy .ttf files
    for f in src_dir.rglob("*.ttf"):
        if f.is_file():
            dst = dst_dir / f.name
            shutil.copy2(f, dst)
            count += 1
    return count


def copy_selected_files(src_dir, dst_dir, filenames):
    """Copy a deliberately small set of webfont files."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for filename in filenames:
        matches = list(src_dir.rglob(filename))
        if not matches:
            print(f"  [FAIL] Missing expected file: {filename}")
            continue
        src = matches[0]
        shutil.copy2(src, dst_dir / filename)
        print(f"  [OK]  {filename} ({src.stat().st_size / 1024:.0f} KB)")
        count += 1
    return count


def download_via_url(url, dest_path):
    """Download a file from URL."""
    import urllib.request
    import ssl
    ssl_ctx = ssl.create_default_context()
    
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    if dest_path.exists():
        print(f"  [EXISTS] {dest_path.name}")
        return True
    
    try:
        print(f"  [GET] {dest_path.name} ...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=120) as resp:
            data = resp.read()
        with open(dest_path, "wb") as f:
            f.write(data)
        size_kb = len(data) / 1024
        print(f"  [OK]  {dest_path.name} ({size_kb:.0f} KB)")
        return True
    except Exception as e:
        print(f"  [FAIL] {dest_path.name}: {e}")
        return False


def download_zhuque_fangsong():
    """Download the official Zhuque Fangsong preview and convert it to WOFF2."""
    version = "0.212"
    archive = TEMP_DIR / f"ZhuqueFangsong-v{version}.zip"
    url = (
        "https://github.com/TrionesType/zhuque/releases/download/"
        f"v{version}/ZhuqueFangsong-v{version}.zip"
    )
    if not download_via_url(url, archive):
        return 0

    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        print("  [FAIL] fonttools and brotli are required to convert Zhuque Fangsong to WOFF2")
        return 0

    ttf_name = "ZhuqueFangsong-Regular.ttf"
    ttf_path = TEMP_DIR / ttf_name
    try:
        with zipfile.ZipFile(archive) as bundle:
            ttf_path.write_bytes(bundle.read(ttf_name))
        output_dir = FONTS_DIR / "zhuque-fangsong"
        output_dir.mkdir(parents=True, exist_ok=True)
        output = output_dir / f"zhuque-fangsong-v{version}-regular.woff2"
        font = TTFont(ttf_path)
        font.flavor = "woff2"
        font.save(output)
        font.close()
        print(f"  [OK]  {output.name} ({output.stat().st_size / 1024:.0f} KB)")
        return 1
    except Exception as exc:
        print(f"  [FAIL] Could not prepare Zhuque Fangsong: {exc}")
        return 0


def main():
    global FONTS_DIR, TEMP_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-dir", type=Path, default=DEFAULT_SERVER_DIR)
    args = parser.parse_args()
    FONTS_DIR = args.server_dir.expanduser().resolve() / "fonts"
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR = Path(tempfile.mkdtemp(prefix="local-web-fonts-"))

    print("=" * 60)
    print("  Font Download Script (via npm + direct URLs)")
    print("=" * 60)
    
    total_ok = 0
    total_fail = 0
    
    # ============================================================
    # 1. LXGW WenKai (via npm)
    # ============================================================
    print("\n--- LXGW WenKai (via npm) ---")
    pkg_dir = run_npm_install("lxgw-wenkai-webfont@1.7.0")
    if pkg_dir:
        files_dir = None
        for d in pkg_dir.rglob("files"):
            if d.is_dir():
                files_dir = d
                break
        if files_dir is None:
            # Search broadly
            files_dir = pkg_dir
        n = copy_woff2_files(files_dir, FONTS_DIR / "lxgw-wenkai")
        total_ok += n
        if n == 0:
            total_fail += 1
            print("  [WARN] No font files found in package")
    else:
        total_fail += 1
    
    # LXGW WenKai Mono
    print("\n--- LXGW WenKai Mono (via npm) ---")
    pkg_dir = run_npm_install("lxgw-wenkai-mono-webfont@1.7.0")
    if pkg_dir:
        files_dir = pkg_dir
        for d in pkg_dir.rglob("files"):
            if d.is_dir():
                files_dir = d
                break
        n = copy_woff2_files(files_dir, FONTS_DIR / "lxgw-wenkai-mono")
        total_ok += n
        if n == 0:
            total_fail += 1
    else:
        total_fail += 1
    
    # ============================================================
    # 2. Inter (via npm @fontsource)
    # ============================================================
    print("\n--- Inter (via npm @fontsource) ---")
    pkg_dir = run_npm_install("@fontsource/inter")
    if pkg_dir:
        n = copy_woff2_files(pkg_dir, FONTS_DIR / "inter")
        total_ok += n
        if n == 0:
            total_fail += 1
    else:
        total_fail += 1
    
    # ============================================================
    # 3. JetBrains Mono (via npm @fontsource)
    # ============================================================
    print("\n--- JetBrains Mono (via npm @fontsource) ---")
    pkg_dir = run_npm_install("@fontsource/jetbrains-mono")
    if pkg_dir:
        n = copy_woff2_files(pkg_dir, FONTS_DIR / "jetbrains-mono")
        total_ok += n
        if n == 0:
            total_fail += 1
    else:
        total_fail += 1
    
    # ============================================================
    # 4. Noto Sans SC (via npm @fontsource)
    # ============================================================
    print("\n--- Noto Sans SC (via npm @fontsource) ---")
    pkg_dir = run_npm_install("@fontsource/noto-sans-sc")
    if pkg_dir:
        n = copy_woff2_files(pkg_dir, FONTS_DIR / "noto-sans-sc")
        total_ok += n
        if n == 0:
            total_fail += 1
    else:
        total_fail += 1
    
    # ============================================================
    # 5. Noto Serif SC (via npm @fontsource)
    # ============================================================
    print("\n--- Noto Serif SC (via npm @fontsource) ---")
    pkg_dir = run_npm_install("@fontsource/noto-serif-sc")
    if pkg_dir:
        n = copy_woff2_files(pkg_dir, FONTS_DIR / "noto-serif-sc")
        total_ok += n
        if n == 0:
            total_fail += 1
    else:
        total_fail += 1
    
    # ============================================================
    # 6. Zhuque Fangsong (official release, converted to WOFF2)
    # ============================================================
    print("\n--- Zhuque Fangsong v0.212 (official release) ---")
    n = download_zhuque_fangsong()
    total_ok += n
    if n == 0:
        total_fail += 1

    # ============================================================
    # 7. Roboto (via npm @fontsource)
    # ============================================================
    print("\n--- Roboto (via npm @fontsource) ---")
    pkg_dir = run_npm_install("@fontsource/roboto")
    if pkg_dir:
        n = copy_woff2_files(pkg_dir, FONTS_DIR / "roboto")
        total_ok += n
        if n == 0:
            total_fail += 1
    else:
        total_fail += 1

    # ============================================================
    # 8. Merriweather (selected Latin WOFF2 files via npm)
    # ============================================================
    print("\n--- Merriweather 5.3.0 (via npm @fontsource) ---")
    pkg_dir = run_npm_install("@fontsource/merriweather@5.3.0")
    if pkg_dir:
        n = copy_selected_files(
            pkg_dir,
            FONTS_DIR / "merriweather",
            [
                "merriweather-latin-400-normal.woff2",
                "merriweather-latin-400-italic.woff2",
                "merriweather-latin-700-normal.woff2",
                "merriweather-latin-700-italic.woff2",
            ],
        )
        total_ok += n
        if n != 4:
            total_fail += 1
    else:
        total_fail += 1

    # ============================================================
    # 9. Source Han Serif SC
    # ============================================================
    print("\n--- Source Han Serif SC / Noto Serif SC supplement ---")
    print("  (Covered by Noto Serif SC above)")
    
    # ============================================================
    # Cleanup temp npm directory
    # ============================================================
    print("\n--- Cleaning up temp files ---")
    if TEMP_DIR.exists():
        # Keep node_modules for potential reuse, but can be deleted
        try:
            shutil.rmtree(TEMP_DIR)
            print("  [OK] Cleaned up temp npm directory")
        except Exception as e:
            print(f"  [WARN] Could not fully clean temp: {e}")
    
    # ============================================================
    # Summary
    # ============================================================
    print(f"\n{'=' * 60}")
    print(f"  Done: {total_ok} font files downloaded")
    if total_fail > 0:
        print(f"  {total_fail} categories had issues")
    
    # List what we got
    print(f"\n  Font directories:")
    for d in sorted(FONTS_DIR.iterdir()):
        if d.is_dir():
            files = list(d.glob("*.woff2"))
            woff_count = len(files)
            total_size = sum(f.stat().st_size for f in files) / 1024 / 1024
            print(f"    {d.name:25s} {woff_count:3d} woff2 files ({total_size:.1f} MB)")
    
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
