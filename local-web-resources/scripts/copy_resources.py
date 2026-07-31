#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Copy selected front-end libraries from an offline cdnjs mirror to the HTTP server."""

import argparse
import shutil
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SERVER_DIR = SCRIPT_DIR.parent.parent / "web-resources-server"
CDNJS_ROOT = None
LIBS_DIR = DEFAULT_SERVER_DIR / "libs"

# ============================================================
# 资源清单：category -> [(cdnjs_name, display_name, copy_rules)]
# copy_rules:
#   "min"        — 只复制 .min.js 和 .min.css (默认)
#   "min+fonts"  — 复制 min 文件 + webfonts/fonts 目录下的字体文件
#   "selective"  — 自定义选择文件
#   "full"       — 复制整个版本目录（谨慎使用）
# ============================================================

RESOURCE_MAP = {
    "css-frameworks": [
        ("bootstrap",            "Bootstrap 5",           "min+fonts"),
        ("tailwindcss-browser",  "Tailwind CSS 4 Browser","min"),
        ("normalize",            "normalize.css",         "min"),
        ("modern-normalize",     "modern-normalize",      "min"),
        ("animate.css",          "Animate.css",           "min"),
        ("picocss",              "Pico.css",              "selective"),
        ("bulma",                "Bulma",                 "min"),
    ],
    "js-core": [
        ("jquery",        "jQuery",       "min"),
        ("vue",           "Vue 3",        "selective"),
        ("lodash.js",     "Lodash",       "selective"),
        ("dayjs",         "Day.js",       "selective"),
        ("marked",        "Marked",       "min"),
        ("dompurify",     "DOMPurify",    "min"),
        ("crypto-js",     "CryptoJS",     "min"),
    ],
    "charts": [
        ("echarts",    "ECharts",    "selective"),
        ("Chart.js",   "Chart.js",   "selective"),
        ("d3",         "D3.js",      "min"),
        ("antv-g2",    "AntV G2",    "min"),
        ("antv-g6",    "AntV G6",    "min"),
        ("antv-x6",    "AntV X6",    "min"),
        ("mermaid",    "Mermaid",    "min"),
        ("apexcharts", "ApexCharts", "min"),
    ],
    "ui-components": [
        ("sweetalert2",         "SweetAlert2",    "min"),
        ("limonte-sweetalert2", "SweetAlert2 Alt", "min"),
        ("toastr.js",           "Toastr",         "min"),
        ("nprogress",           "NProgress",      "min"),
        ("typed.js",            "Typed.js",       "min"),
        ("intro.js",            "Intro.js",       "min"),
        ("driver.js",           "Driver.js",      "min"),
        ("choices.js",          "Choices.js",     "min"),
        ("select2",             "Select2",        "min"),
        ("flatpickr",           "Flatpickr",      "min"),
        ("noUiSlider",          "noUiSlider",     "min"),
    ],
    "code-highlight": [
        ("highlight.js", "highlight.js", "selective"),
        ("prism",        "Prism",        "selective"),
    ],
    "icons": [
        ("font-awesome",     "Font Awesome 7",    "min+fonts"),
        ("bootstrap-icons",  "Bootstrap Icons",   "min+fonts"),
        ("remixicon",        "Remix Icon",        "min+fonts"),
        ("tabler-icons",     "Tabler Icons",      "min+fonts"),
        ("material-design-icons", "Material Icons","min+fonts"),
    ],
    "animation": [
        ("gsap",          "GSAP",          "selective"),
        ("lottie-web",    "Lottie Web",    "min"),
        ("particles.js",  "Particles.js",  "min"),
        ("aos",           "AOS",           "min"),
        ("wow",           "WOW.js",        "min"),
        ("countup.js",    "CountUp.js",    "min"),
        ("canvas-confetti","Canvas Confetti","min"),
    ],
    "utils": [
        ("clipboard.js",   "Clipboard.js",  "min"),
        ("html2canvas",    "html2canvas",    "min"),
        ("FileSaver.js",   "FileSaver.js",   "min"),
        ("jszip",          "JSZip",          "min"),
        ("xlsx",           "SheetJS",        "min"),
        ("jspdf",          "jsPDF",          "min"),
        ("qrcodejs",       "QRCode.js",      "min"),
        ("html-to-image",  "html-to-image",  "min"),
        ("dom-to-image",   "dom-to-image",   "min"),
        ("signature_pad",  "Signature Pad",  "min"),
        ("localforage",    "localForage",    "min"),
        ("PapaParse",      "PapaParse",      "min"),
        ("showdown",       "Showdown",       "min"),
        ("turndown",       "Turndown",       "min"),
    ],
    "tables": [
        ("datatables",        "DataTables",    "min"),
        ("tabulator-tables",  "Tabulator",     "min"),
        ("handsontable",      "Handsontable",  "min"),
    ],
    "editors": [
        ("tinymce",       "TinyMCE",      "selective"),
        ("codemirror",    "CodeMirror",   "selective"),
        ("monaco-editor", "Monaco Editor","selective"),
    ],
    "layout": [
        ("Sortable",      "Sortable",      "min"),
        ("Swiper",        "Swiper",        "min"),
        ("masonry",       "Masonry",       "min"),
        ("fullPage.js",   "fullPage.js",   "min"),
        ("gridstack.js",  "Gridstack",     "min"),
        ("simplebar",     "SimpleBar",     "min"),
    ],
}


def find_version_dir(lib_path: Path) -> Path | None:
    """找到库的版本目录（通常只有一个版本）"""
    if not lib_path.exists():
        return None
    subdirs = [d for d in lib_path.iterdir() if d.is_dir() and d.name != '.DS_Store']
    if not subdirs:
        return None
    # 返回第一个（通常也是唯一的）版本目录
    return subdirs[0]


def copy_min_files(src_dir: Path, dst_dir: Path):
    """复制 .min.js 和 .min.css 文件（排除 .map）"""
    for f in src_dir.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix == '.map':
            continue
        name = f.name.lower()
        if name.endswith('.min.js') or name.endswith('.min.css'):
            rel = f.relative_to(src_dir)
            dst = dst_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)


def copy_font_files(src_dir: Path, dst_dir: Path):
    """复制字体相关文件 (woff, woff2, ttf, eot, svg for fonts)"""
    font_dirs = ['webfonts', 'fonts', 'font']
    font_exts = {'.woff', '.woff2', '.ttf', '.eot'}
    
    for font_dirname in font_dirs:
        for fd in src_dir.rglob(font_dirname):
            if fd.is_dir():
                for f in fd.rglob("*"):
                    if f.is_file() and f.suffix.lower() in font_exts:
                        rel = f.relative_to(src_dir)
                        dst = dst_dir / rel
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(f, dst)


def copy_min_and_fonts(src_dir: Path, dst_dir: Path):
    """复制 min 文件 + 字体文件"""
    copy_min_files(src_dir, dst_dir)
    copy_font_files(src_dir, dst_dir)
    # 同时复制非 min 的 CSS（因为图标库的 CSS 可能没有 min 版本仍然需要）
    for f in src_dir.rglob("*.css"):
        if f.is_file() and not f.name.endswith('.min.css'):
            # 检查是否已有对应的 min 版本
            min_name = f.stem + '.min.css'
            min_path = f.parent / min_name
            if not min_path.exists():
                # 没有 min 版本，复制原始 CSS
                rel = f.relative_to(src_dir)
                dst = dst_dir / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dst)


def copy_selective(cdnjs_name: str, src_dir: Path, dst_dir: Path):
    """针对特定库的定制复制规则"""
    
    if cdnjs_name == "highlight.js":
        # 核心 + 精选主题
        core = src_dir / "highlight.min.js"
        if core.exists():
            shutil.copy2(core, dst_dir / "highlight.min.js")
        # es 目录下的核心
        es_core = src_dir / "es" / "highlight.min.js"
        if es_core.exists():
            (dst_dir / "es").mkdir(parents=True, exist_ok=True)
            shutil.copy2(es_core, dst_dir / "es" / "highlight.min.js")
        # 精选主题
        themes = [
            "default", "github", "github-dark", "github-dark-dimmed",
            "vs", "vs2015", "atom-one-dark", "atom-one-light",
            "monokai", "monokai-sublime", "tokyo-night-dark",
            "nord", "dracula",  # dracula might not exist
            "stackoverflow-dark", "stackoverflow-light",
        ]
        styles_src = src_dir / "styles"
        if styles_src.exists():
            styles_dst = dst_dir / "styles"
            styles_dst.mkdir(parents=True, exist_ok=True)
            for theme in themes:
                for ext in [".min.css", ".css"]:
                    tf = styles_src / f"{theme}{ext}"
                    if tf.exists():
                        shutil.copy2(tf, styles_dst / tf.name)
    
    elif cdnjs_name == "prism":
        # 核心 + 常用语言 + 主题
        for f in src_dir.glob("prism*.js"):
            shutil.copy2(f, dst_dir / f.name)
        for f in src_dir.glob("prism*.css"):
            shutil.copy2(f, dst_dir / f.name)
        # 常用语言组件
        langs = [
            "prism-python", "prism-javascript", "prism-typescript",
            "prism-css", "prism-markup", "prism-bash", "prism-sql",
            "prism-json", "prism-yaml", "prism-markdown",
            "prism-java", "prism-c", "prism-cpp", "prism-csharp",
            "prism-go", "prism-rust",
        ]
        comp_dir = src_dir / "components"
        if comp_dir.exists():
            comp_dst = dst_dir / "components"
            comp_dst.mkdir(parents=True, exist_ok=True)
            for lang in langs:
                for ext in [".min.js", ".js"]:
                    lf = comp_dir / f"{lang}{ext}"
                    if lf.exists():
                        shutil.copy2(lf, comp_dst / lf.name)
        # 主题
        themes_dir = src_dir / "themes"
        if themes_dir.exists():
            themes_dst = dst_dir / "themes"
            themes_dst.mkdir(parents=True, exist_ok=True)
            for f in themes_dir.iterdir():
                if f.is_file() and f.suffix in ['.css', '.min.css']:
                    shutil.copy2(f, themes_dst / f.name)
    
    elif cdnjs_name == "echarts":
        # 核心 + 中文语言包 + 常用主题
        for name in ["echarts.min.js", "echarts.js", "echarts.esm.min.js", "echarts.esm.js",
                      "echarts.simple.min.js", "echarts.common.min.js"]:
            f = src_dir / name
            if f.exists():
                shutil.copy2(f, dst_dir / name)
        # 中文语言包
        i18n_dir = src_dir / "i18n"
        if i18n_dir.exists():
            i18n_dst = dst_dir / "i18n"
            i18n_dst.mkdir(parents=True, exist_ok=True)
            for lang in ["langZH", "langEN"]:
                for ext in [".min.js", ".js", "-obj.min.js", "-obj.js"]:
                    lf = i18n_dir / f"{lang}{ext}"
                    if lf.exists():
                        shutil.copy2(lf, i18n_dst / lf.name)
        # 常用主题
        theme_dir = src_dir / "theme"
        if theme_dir.exists():
            theme_dst = dst_dir / "theme"
            theme_dst.mkdir(parents=True, exist_ok=True)
            for theme in ["dark", "vintage", "macarons", "infographic", "shine", "roma", "v5"]:
                for ext in [".min.js", ".js"]:
                    tf = theme_dir / f"{theme}{ext}"
                    if tf.exists():
                        shutil.copy2(tf, theme_dst / tf.name)

    elif cdnjs_name == "Chart.js":
        # 只复制 umd 版本（可在 script 标签直接用）
        for name in ["chart.umd.min.js", "chart.umd.js", "chart.min.js"]:
            f = src_dir / name
            if f.exists():
                shutil.copy2(f, dst_dir / name)

    elif cdnjs_name == "vue":
        # 复制全局构建版本
        for name in ["vue.global.js", "vue.global.min.js", "vue.global.prod.js", "vue.global.prod.min.js",
                      "vue.esm-browser.js", "vue.esm-browser.min.js", "vue.esm-browser.prod.js", "vue.esm-browser.prod.min.js"]:
            f = src_dir / name
            if f.exists():
                shutil.copy2(f, dst_dir / name)
    
    elif cdnjs_name == "lodash.js":
        for name in ["lodash.min.js", "lodash.js", "lodash.core.min.js"]:
            f = src_dir / name
            if f.exists():
                shutil.copy2(f, dst_dir / name)
    
    elif cdnjs_name == "dayjs":
        # 核心 + 中文locale + 常用插件
        for f in src_dir.glob("dayjs.min.js"):
            shutil.copy2(f, dst_dir / f.name)
        locale_dir = src_dir / "locale"
        if locale_dir.exists():
            locale_dst = dst_dir / "locale"
            locale_dst.mkdir(parents=True, exist_ok=True)
            for loc in ["zh-cn", "zh-tw", "en"]:
                for ext in [".min.js", ".js"]:
                    lf = locale_dir / f"{loc}{ext}"
                    if lf.exists():
                        shutil.copy2(lf, locale_dst / lf.name)
        plugin_dir = src_dir / "plugin"
        if plugin_dir.exists():
            plugin_dst = dst_dir / "plugin"
            plugin_dst.mkdir(parents=True, exist_ok=True)
            plugins = ["relativeTime", "duration", "customParseFormat", "advancedFormat",
                       "isBetween", "isSameOrBefore", "isSameOrAfter", "weekOfYear", "quarterOfYear"]
            for p in plugins:
                for ext in [".min.js", ".js"]:
                    pf = plugin_dir / f"{p}{ext}"
                    if pf.exists():
                        shutil.copy2(pf, plugin_dst / pf.name)
    
    elif cdnjs_name == "gsap":
        # 核心 + 常用插件
        gsap_files = [
            "gsap.min.js", "gsap.js",
            "ScrollTrigger.min.js", "ScrollToPlugin.min.js",
            "Draggable.min.js", "MotionPathPlugin.min.js",
            "TextPlugin.min.js", "Flip.min.js",
        ]
        for name in gsap_files:
            f = src_dir / name
            if f.exists():
                shutil.copy2(f, dst_dir / name)
    
    elif cdnjs_name == "picocss":
        # 只复制默认主题
        for name in ["pico.min.css", "pico.css", "pico.classless.min.css", "pico.classless.css"]:
            f = src_dir / name
            if f.exists():
                shutil.copy2(f, dst_dir / name)
    
    elif cdnjs_name in ("tinymce", "codemirror", "monaco-editor"):
        # 大型编辑器只复制核心 min 文件
        copy_min_files(src_dir, dst_dir)
    
    else:
        # 默认 fallback: 复制 min 文件
        copy_min_files(src_dir, dst_dir)


def main():
    global CDNJS_ROOT, LIBS_DIR
    parser = argparse.ArgumentParser(description="Copy curated assets from an offline cdnjs mirror.")
    parser.add_argument("--cdnjs-root", type=Path, required=True, help="Path containing cdnjs library directories.")
    parser.add_argument("--server-dir", type=Path, default=DEFAULT_SERVER_DIR)
    args = parser.parse_args()
    CDNJS_ROOT = args.cdnjs_root.expanduser().resolve()
    LIBS_DIR = args.server_dir.expanduser().resolve() / "libs"
    if not CDNJS_ROOT.is_dir():
        raise SystemExit(f"cdnjs mirror not found: {CDNJS_ROOT}")
    LIBS_DIR.mkdir(parents=True, exist_ok=True)

    total_copied = 0
    total_size = 0
    skipped = []

    for category, libs in RESOURCE_MAP.items():
        print(f"\n{'='*60}")
        print(f"  Category: {category}")
        print(f"{'='*60}")
        
        for cdnjs_name, display_name, rule in libs:
            lib_src = CDNJS_ROOT / cdnjs_name
            ver_dir = find_version_dir(lib_src)
            
            if ver_dir is None:
                print(f"  [SKIP] {display_name} ({cdnjs_name}) -- not found in cdnjs")
                skipped.append(cdnjs_name)
                continue
            
            version = ver_dir.name
            dst_dir = LIBS_DIR / category / cdnjs_name
            dst_dir.mkdir(parents=True, exist_ok=True)
            
            if rule == "min":
                copy_min_files(ver_dir, dst_dir)
            elif rule == "min+fonts":
                copy_min_and_fonts(ver_dir, dst_dir)
            elif rule == "selective":
                copy_selective(cdnjs_name, ver_dir, dst_dir)
            elif rule == "full":
                if dst_dir.exists():
                    shutil.rmtree(dst_dir)
                shutil.copytree(ver_dir, dst_dir)
            
            # 统计
            copied_files = list(dst_dir.rglob("*"))
            file_count = sum(1 for f in copied_files if f.is_file())
            file_size = sum(f.stat().st_size for f in copied_files if f.is_file())
            total_copied += file_count
            total_size += file_size
            
            print(f"  [OK] {display_name:20s} v{version:12s} -> {file_count:3d} files, {file_size/1024:.0f} KB")
    
    print(f"\n{'='*60}")
    print(f"  DONE: {total_copied} files, {total_size/1024/1024:.1f} MB total")
    if skipped:
        print(f"  Skipped ({len(skipped)}): {', '.join(skipped)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
