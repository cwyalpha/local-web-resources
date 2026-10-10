#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_component_index.py
Scan the resource server directory and generate per-component .md index files
for the Skill. Each index file lists all available files for that component
with their HTTP paths (relative to BASE_URL).
"""

import argparse
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_SERV_DIR = DEFAULT_SKILL_DIR.parent / "web-resources-server"
EXCLUDED_SERVER_FILES = {
    "libs/editors/codemirror/addon/mode/multiplex_test.min.js",
    "libs/layout/gridstack.js/vitest.config.min.js",
    "libs/layout/gridstack.js/vitest.setup.min.js",
}

# Metadata for libraries (name -> description, usage hints)
LIB_META = {
    # CSS Frameworks
    "bootstrap": {"desc": "响应式布局、组件系统", "version": "5.3.8", "category": "CSS 框架"},
    "tailwindcss-browser": {"desc": "原子化 CSS（浏览器版，放在 <head> 中）", "version": "4.1.13", "category": "CSS 框架"},
    "bulma": {"desc": "现代 CSS 框架", "version": "1.0.4", "category": "CSS 框架"},
    "picocss": {"desc": "极简 Classless CSS", "version": "2.1.1", "category": "CSS 框架"},
    "normalize": {"desc": "CSS 重置", "version": "8.0.1", "category": "CSS 框架"},
    "modern-normalize": {"desc": "现代 CSS 重置", "version": "3.0.1", "category": "CSS 框架"},
    "animate.css": {"desc": "CSS 动画库", "version": "4.1.1", "category": "CSS 框架"},
    # JS Core
    "jquery": {"desc": "DOM 操作", "version": "3.7.1", "category": "JS 核心"},
    "alpinejs": {"desc": "适合静态页面的轻量交互层（script 必须使用 defer）", "version": "3.15.12", "category": "JS 核心"},
    "vue": {"desc": "前端框架（script 标签用 vue.global.min.js）", "version": "3.5.22", "category": "JS 核心"},
    "lodash.js": {"desc": "工具函数库", "version": "4.17.21", "category": "JS 核心"},
    "dayjs": {"desc": "轻量日期库", "version": "1.11.18", "category": "JS 核心"},
    "marked": {"desc": "Markdown 渲染", "version": "16.3.0", "category": "JS 核心"},
    "markdown-it": {"desc": "Markdown 渲染（插件丰富）", "version": "14.x", "category": "JS 核心"},
    "dompurify": {"desc": "HTML 净化", "version": "3.2.6", "category": "JS 核心"},
    "crypto-js": {"desc": "加密工具", "version": "4.2.0", "category": "JS 核心"},
    "katex": {"desc": "数学公式渲染", "version": "0.16.9", "category": "JS 核心",
              "usage": "CSS: katex.min.css + JS: katex.min.js + contrib/auto-render.min.js\n用法: <body onload=\"renderMathInElement(document.body);\">"},
    # Charts
    "echarts": {"desc": "全功能图表（推荐）。含中国地图: map/china.js（自动注册），省份: map/province/{pinyin}.js", "version": "6.0.0", "category": "数据可视化"},
    "Chart.js": {"desc": "轻量图表", "version": "4.5.0", "category": "数据可视化"},
    "d3": {"desc": "数据驱动可视化", "version": "7.9.0", "category": "数据可视化"},
    "cytoscape": {"desc": "图论分析、复杂关系网络与交互", "version": "3.34.0", "category": "数据可视化"},
    "plotly": {"desc": "科学、统计、3D 与金融图表", "version": "3.7.0", "category": "数据可视化"},
    "vis-network": {"desc": "快速拓扑/关系网络与物理布局", "version": "10.1.0", "category": "数据可视化"},
    "antv-g2": {"desc": "图形语法图表", "version": "5.4.1", "category": "数据可视化"},
    "antv-g6": {"desc": "图/关系可视化", "version": "5.0.49", "category": "数据可视化"},
    "antv-x6": {"desc": "流程图/DAG 编辑器", "version": "3.1.7", "category": "数据可视化"},
    "mermaid": {"desc": "文本转图表（流程图/时序图/甘特图等）", "version": "11.12.0", "category": "数据可视化"},
    "apexcharts": {"desc": "交互式图表", "version": "5.3.5", "category": "数据可视化"},
    # Code Highlight
    "highlight.js": {"desc": "代码高亮（推荐）。主题在 styles/ 下，如 github.min.css、github-dark.min.css", "version": "11.11.1", "category": "代码高亮"},
    "prism": {"desc": "轻量代码高亮", "version": "1.30.0", "category": "代码高亮"},
    # Icons
    "font-awesome": {"desc": "图标库 30000+。用法: <i class=\"fa-solid fa-check\"></i>", "version": "7.0.1", "category": "图标"},
    "bootstrap-icons": {"desc": "图标库 2000+。用法: <i class=\"bi bi-check\"></i>", "version": "1.13.1", "category": "图标"},
    "remixicon": {"desc": "图标库 2800+。用法: <i class=\"ri-check-line\"></i>", "version": "4.6.0", "category": "图标"},
    "tabler-icons": {"desc": "图标库 5000+。用法: <i class=\"ti ti-check\"></i>", "version": "3.35.0", "category": "图标"},
    "material-design-icons": {"desc": "Material 图标 2000+。用法: <span class=\"material-icons\">check</span>", "version": "4.0.0", "category": "图标"},
    "lucide": {"desc": "SVG 图标（静态页面默认推荐）", "version": "1.28.0", "category": "图标"},
    # Animation
    "gsap": {"desc": "专业动画引擎。插件: ScrollTrigger.min.js, Draggable.min.js 等", "version": "3.13.0", "category": "动画"},
    "lottie-web": {"desc": "Lottie 动画播放", "version": "5.13.0", "category": "动画"},
    "particles.js": {"desc": "粒子背景效果", "version": "2.0.0", "category": "动画"},
    "aos": {"desc": "滚动动画（注意：文件名 aos.js / aos.css，无 .min）", "version": "2.3.4", "category": "动画"},
    "wow": {"desc": "滚动触发动画", "version": "1.1.2", "category": "动画"},
    "countup.js": {"desc": "数字递增动画。用 countUp.umd.min.js，调用: new countUp.CountUp(id, val)", "version": "2.9.0", "category": "动画"},
    "canvas-confetti": {"desc": "彩纸效果", "version": "1.9.3", "category": "动画"},
    # UI Components
    "sweetalert2": {"desc": "弹窗对话框", "version": "11.23.0", "category": "UI 组件"},
    "limonte-sweetalert2": {"desc": "SweetAlert2 另一版本", "version": "11.x", "category": "UI 组件"},
    "toastr.js": {"desc": "通知提示", "version": "2.1.4", "category": "UI 组件"},
    "nprogress": {"desc": "顶部进度条", "version": "0.2.0", "category": "UI 组件"},
    "typed.js": {"desc": "打字机效果", "version": "2.1.0", "category": "UI 组件"},
    "intro.js": {"desc": "新手引导", "version": "8.3.2", "category": "UI 组件"},
    "flatpickr": {"desc": "日期选择器", "version": "4.6.13", "category": "UI 组件"},
    "select2": {"desc": "增强下拉框（依赖 jQuery）", "version": "4.0.13", "category": "UI 组件"},
    "choices.js": {"desc": "下拉/标签输入", "version": "11.1.0", "category": "UI 组件"},
    "noUiSlider": {"desc": "范围滑块", "version": "15.8.1", "category": "UI 组件"},
    "cropperjs": {"desc": "图片裁剪（v2 API）", "version": "2.0.0", "category": "UI 组件"},
    "jstree": {"desc": "树形控件（依赖 jQuery）", "version": "3.3.17", "category": "UI 组件"},
    "driver.js": {"desc": "新手引导/高亮", "version": "1.8.0", "category": "UI 组件"},
    # Utils
    "clipboard.js": {"desc": "复制到剪贴板", "version": "2.0.11", "category": "工具"},
    "html2canvas": {"desc": "HTML 转 Canvas/图片", "version": "1.4.1", "category": "工具"},
    "FileSaver.js": {"desc": "文件保存", "version": "2.0.5", "category": "工具"},
    "jszip": {"desc": "ZIP 压缩", "version": "3.10.1", "category": "工具"},
    "xlsx": {"desc": "Excel 读写 (SheetJS)", "version": "0.20.3", "category": "工具"},
    "jspdf": {"desc": "生成 PDF", "version": "3.0.3", "category": "工具"},
    "qrcodejs": {"desc": "二维码生成", "version": "1.0.0", "category": "工具"},
    "html-to-image": {"desc": "HTML 转图片", "version": "1.11.13", "category": "工具"},
    "dom-to-image": {"desc": "DOM 转图片", "version": "2.x", "category": "工具"},
    "PapaParse": {"desc": "CSV 解析", "version": "5.4.1", "category": "工具"},
    "showdown": {"desc": "Markdown→HTML", "version": "2.1.0", "category": "工具"},
    "turndown": {"desc": "HTML→Markdown", "version": "7.2.1", "category": "工具"},
    "localforage": {"desc": "本地存储", "version": "1.10.0", "category": "工具"},
    "signature_pad": {"desc": "手写签名", "version": "5.1.1", "category": "工具"},
    "fuse.js": {"desc": "前端模糊搜索", "version": "7.1.0", "category": "工具"},
    # Tables
    "datatables": {"desc": "jQuery/原生初始化表格，含 Bootstrap 5 适配", "version": "2.3.8", "category": "表格"},
    "tabulator-tables": {"desc": "独立表格库", "version": "6.3.1", "category": "表格"},
    "handsontable": {"desc": "类 Excel 表格", "version": "16.1.1", "category": "表格"},
    # Editors
    "tinymce": {"desc": "富文本编辑器", "version": "8.1.2", "category": "编辑器"},
    "codemirror": {"desc": "经典全局脚本版代码编辑器（CodeMirror 5）", "version": "5.65.21", "category": "编辑器"},
    "monaco-editor": {"desc": "VS Code 编辑器", "version": "0.53.0", "category": "编辑器"},
    # Layout
    "Sortable": {"desc": "拖拽排序", "version": "1.15.6", "category": "布局"},
    "Swiper": {"desc": "轮播/滑动", "version": "11.0.5", "category": "布局"},
    "masonry": {"desc": "瀑布流布局", "version": "4.2.2", "category": "布局"},
    "fullPage.js": {"desc": "全屏滚动", "version": "4.0.37", "category": "布局"},
    "gridstack.js": {"desc": "网格拖拽", "version": "12.3.3", "category": "布局"},
    "simplebar": {"desc": "自定义滚动条", "version": "6.3.2", "category": "布局"},
    "reveal.js": {"desc": "HTML 幻灯片/演示文稿。主题在 theme/ 下 (black, white, league, dracula 等)", "version": "5.2.1", "category": "布局"},
}

FONT_META = {
    "smiley-sans": {"desc": "得意黑 v2.0.1：倾斜标题字体，font-style: oblique，400 字重", "css_family": "Smiley Sans"},
    "resource-han-rounded": {"desc": "源泉圆体 v0.990：简体中文圆体，400/700 字重，保留完整字形", "css_family": "Resource Han Rounded CN"},
    "inter": {"desc": "英文 UI 无衬线字体", "css_family": "Inter"},
    "roboto": {"desc": "英文通用无衬线字体", "css_family": "Roboto"},
    "jetbrains-mono": {"desc": "代码等宽字体", "css_family": "JetBrains Mono"},
    "noto-sans-sc": {"desc": "思源黑体（替代黑体/微软雅黑）", "css_family": "Noto Sans SC"},
    "noto-serif-sc": {"desc": "思源宋体（宋体风格的正式报告和长篇正文）", "css_family": "Noto Serif SC"},
    "lxgw-wenkai": {"desc": "霞鹜文楷（替代楷体）", "css_family": "LXGW WenKai"},
    "lxgw-wenkai-mono": {"desc": "霞鹜文楷等宽（代码用）", "css_family": "LXGW WenKai Mono"},
    "zhuque-fangsong": {"desc": "朱雀仿宋 v0.212 预览版（公文、正式报告仿宋正文）", "css_family": "Zhuque Fangsong"},
    "merriweather": {"desc": "英文正文衬线字体", "css_family": "Merriweather"},
}

# Only verified browser entrypoints are recommended. Everything else remains
# discoverable in the generated file inventory but is not marked as safe to use.
CURATED_META = {
    "bootstrap": {
        "tier": "default",
        "entrypoints": [
            {"kind": "css", "path": "libs/css-frameworks/bootstrap/css/bootstrap.min.css", "load": "head"},
            {"kind": "js", "path": "libs/css-frameworks/bootstrap/js/bootstrap.bundle.min.js", "load": "body-end"},
        ],
        "global": "bootstrap",
        "license": "MIT",
    },
    "alpinejs": {
        "tier": "default",
        "entrypoints": [
            {"kind": "js", "path": "libs/js-core/alpinejs/cdn.min.js", "load": "head-defer"},
        ],
        "global": "Alpine",
        "license": "MIT",
        "note": "适合筛选、选框联动、折叠、标签页和少量跨组件状态；不要用于纯展示页面。",
    },
    "echarts": {
        "tier": "default",
        "entrypoints": [{"kind": "js", "path": "libs/charts/echarts/echarts.min.js", "load": "body-end"}],
        "optional_entrypoints": [
            {
                "kind": "js",
                "path": "libs/charts/echarts/map/china.js",
                "load": "after-echarts",
                "when": "使用中国地图时",
            },
        ],
        "global": "echarts",
        "license": "Apache-2.0",
        "note": "省级地图按需加载 map/province/{pinyin}.js；地图注册文件必须在 ECharts 核心之后。",
    },
    "d3": {
        "tier": "common",
        "entrypoints": [{"kind": "js", "path": "libs/charts/d3/d3.min.js", "load": "body-end"}],
        "global": "d3",
        "license": "ISC",
    },
    "mermaid": {
        "tier": "common",
        "entrypoints": [{"kind": "js", "path": "libs/charts/mermaid/mermaid.min.js", "load": "body-end"}],
        "global": "mermaid",
        "license": "MIT",
        "note": "适合流程图、时序图、甘特图等文本图。自动扫描 .mermaid 与手动 render/run 二选一；手动渲染时尽早 initialize({startOnLoad:false})，等待 Promise 并捕获失败，避免再次读取已渲染 SVG。",
    },
    "lucide": {
        "tier": "default",
        "entrypoints": [{"kind": "js", "path": "libs/icons/lucide/lucide.min.js", "load": "body-end"}],
        "global": "lucide",
        "license": "ISC",
        "note": "使用 data-lucide 属性后调用 lucide.createIcons()；动态插入图标后再次调用。图标名使用官方 kebab-case，例如 qr-code，不是 qrcode。",
    },
    "tabulator-tables": {
        "tier": "default",
        "entrypoints": [
            {"kind": "css", "path": "libs/tables/tabulator-tables/css/tabulator_bootstrap5.min.css", "load": "head-after-bootstrap"},
            {"kind": "js", "path": "libs/tables/tabulator-tables/js/tabulator.min.js", "load": "body-end"},
        ],
        "global": "Tabulator",
        "dependencies": ["Bootstrap CSS（仅使用 Bootstrap 5 主题时）"],
        "license": "MIT",
        "note": "Tabulator JS 不依赖 bootstrap.bundle 或 jQuery；不要仅因使用 Bootstrap 主题而发明 JS 依赖顺序。",
    },
    "choices.js": {
        "tier": "common",
        "entrypoints": [
            {"kind": "css", "path": "libs/ui-components/choices.js/choices.min.css", "load": "head"},
            {"kind": "js", "path": "libs/ui-components/choices.js/choices.min.js", "load": "body-end"},
        ],
        "global": "Choices",
        "license": "MIT",
    },
    "dayjs": {
        "tier": "common",
        "entrypoints": [{"kind": "js", "path": "libs/js-core/dayjs/dayjs.min.js", "load": "body-end"}],
        "global": "dayjs",
        "license": "MIT",
    },
    "lodash.js": {
        "tier": "common",
        "entrypoints": [{"kind": "js", "path": "libs/js-core/lodash.js/lodash.min.js", "load": "body-end"}],
        "global": "_",
        "license": "MIT",
    },
    "dompurify": {
        "tier": "common",
        "entrypoints": [{"kind": "js", "path": "libs/js-core/dompurify/purify.min.js", "load": "body-end"}],
        "global": "DOMPurify",
        "license": "Apache-2.0 OR MPL-2.0",
        "note": "渲染不可信 Markdown/HTML 时必须使用。",
    },
    "marked": {
        "tier": "common",
        "entrypoints": [{"kind": "js", "path": "libs/js-core/marked/lib/marked.umd.min.js", "load": "body-end"}],
        "global": "marked",
        "dependencies": ["dompurify（输入不可信时）"],
        "license": "MIT",
    },
    "highlight.js": {
        "tier": "common",
        "entrypoints": [
            {"kind": "css", "path": "libs/code-highlight/highlight.js/styles/github.min.css", "load": "head"},
            {"kind": "js", "path": "libs/code-highlight/highlight.js/highlight.min.js", "load": "body-end"},
        ],
        "global": "hljs",
        "license": "BSD-3-Clause",
    },
    "sweetalert2": {
        "tier": "common",
        "entrypoints": [
            {"kind": "css", "path": "libs/ui-components/sweetalert2/sweetalert2.min.css", "load": "head"},
            {"kind": "js", "path": "libs/ui-components/sweetalert2/sweetalert2.all.min.js", "load": "body-end"},
        ],
        "global": "Swal",
        "license": "MIT",
    },
    "flatpickr": {
        "tier": "conditional",
        "entrypoints": [
            {"kind": "css", "path": "libs/ui-components/flatpickr/flatpickr.min.css", "load": "head"},
            {"kind": "js", "path": "libs/ui-components/flatpickr/flatpickr.min.js", "load": "body-end"},
        ],
        "optional_entrypoints": [
            {
                "kind": "js",
                "path": "libs/ui-components/flatpickr/l10n/zh.min.js",
                "load": "after-flatpickr",
                "when": "设置 locale: 'zh' 时必须加载",
            },
        ],
        "global": "flatpickr",
        "license": "MIT",
        "note": "中文语言包必须在 flatpickr.min.js 之后、初始化之前加载，否则会报告 invalid locale zh。",
    },
    "katex": {
        "tier": "conditional",
        "entrypoints": [
            {"kind": "css", "path": "libs/js-core/katex/katex.min.css", "load": "head"},
            {"kind": "js", "path": "libs/js-core/katex/katex.min.js", "load": "body-end"},
        ],
        "optional_entrypoints": [
            {
                "kind": "js",
                "path": "libs/js-core/katex/contrib/auto-render.min.js",
                "load": "after-katex",
                "when": "需要自动扫描公式时",
            },
        ],
        "global": "katex",
        "license": "MIT",
        "note": "长块级公式可能撑宽较窄的卡片或分栏；为 .katex-display 或其容器设置 overflow-x: auto。",
    },
    "qrcodejs": {
        "tier": "specialized",
        "entrypoints": [{"kind": "js", "path": "libs/utils/qrcodejs/qrcode.min.js", "load": "body-end"}],
        "global": "QRCode",
        "license": "MIT",
    },
    "countup.js": {
        "tier": "conditional",
        "entrypoints": [{"kind": "js", "path": "libs/animation/countup.js/countUp.umd.min.js", "load": "body-end"}],
        "global": "countUp",
        "license": "MIT",
        "note": "使用 UMD 入口并通过 new countUp.CountUp(id, value, options) 初始化。",
    },
    "xlsx": {
        "tier": "common",
        "entrypoints": [{"kind": "js", "path": "libs/utils/xlsx/xlsx.full.min.js", "load": "body-end"}],
        "global": "XLSX",
        "license": "Apache-2.0",
        "note": "xlsx.full.min.js / xlsx.mini.min.js 已升级到 0.20.3；其余旧构建仅保留兼容，不用于新页面。读取用户文件时限制大小并捕获解析错误。",
    },
    "PapaParse": {
        "tier": "common",
        "entrypoints": [{"kind": "js", "path": "libs/utils/PapaParse/papaparse.min.js", "load": "body-end"}],
        "global": "Papa",
        "license": "MIT",
    },
    "fuse.js": {
        "tier": "common",
        "entrypoints": [{"kind": "js", "path": "libs/utils/fuse.js/fuse.min.js", "load": "body-end"}],
        "global": "Fuse",
        "license": "Apache-2.0",
    },
    "html-to-image": {
        "tier": "common",
        "entrypoints": [{"kind": "js", "path": "libs/utils/html-to-image/html-to-image.min.js", "load": "body-end"}],
        "global": "htmlToImage",
        "license": "MIT",
    },
    "FileSaver.js": {
        "tier": "common",
        "entrypoints": [{"kind": "js", "path": "libs/utils/FileSaver.js/FileSaver.min.js", "load": "body-end"}],
        "global": "saveAs",
        "license": "MIT",
    },
    "Sortable": {
        "tier": "common",
        "entrypoints": [{"kind": "js", "path": "libs/layout/Sortable/Sortable.min.js", "load": "body-end"}],
        "global": "Sortable",
        "license": "MIT",
    },
    "Chart.js": {
        "tier": "conditional",
        "entrypoints": [{"kind": "js", "path": "libs/charts/Chart.js/chart.umd.min.js", "load": "body-end"}],
        "global": "Chart",
        "license": "MIT",
    },
    "bootstrap-icons": {
        "tier": "conditional",
        "entrypoints": [{"kind": "css", "path": "libs/icons/bootstrap-icons/font/bootstrap-icons.min.css", "load": "head"}],
        "license": "MIT",
    },
    "datatables": {
        "tier": "conditional",
        "entrypoints": [
            {"kind": "css", "path": "libs/tables/datatables/css/dataTables.bootstrap5.min.css", "load": "head"},
            {"kind": "js", "path": "libs/js-core/jquery/jquery.min.js", "load": "body-end"},
            {"kind": "js", "path": "libs/tables/datatables/js/dataTables.min.js", "load": "body-end"},
            {"kind": "js", "path": "libs/tables/datatables/js/dataTables.bootstrap5.min.js", "load": "body-end"},
        ],
        "global": "DataTable",
        "dependencies": ["jquery", "bootstrap（使用 Bootstrap 5 样式时）"],
        "license": "MIT",
        "note": "新页面只使用 dataTables.min.js + dataTables.bootstrap5.min.js；jquery.dataTables.min.js 和旧主题仅保留兼容。",
    },
    "prism": {
        "tier": "conditional",
        "entrypoints": [
            {"kind": "css", "path": "libs/code-highlight/prism/themes/prism.min.css", "load": "head"},
            {"kind": "js", "path": "libs/code-highlight/prism/prism.min.js", "load": "body-end"},
        ],
        "global": "Prism",
        "license": "MIT",
    },
    "driver.js": {
        "tier": "specialized",
        "entrypoints": [
            {"kind": "css", "path": "libs/ui-components/driver.js/driver.css", "load": "head"},
            {"kind": "js", "path": "libs/ui-components/driver.js/driver.js.iife.js", "load": "body-end"},
        ],
        "global": "driver.js",
        "license": "MIT",
        "note": "IIFE API 为 window.driver.js.driver(options)。",
    },
    "antv-x6": {
        "tier": "specialized",
        "entrypoints": [{"kind": "js", "path": "libs/charts/antv-x6/x6.min.js", "load": "body-end"}],
        "global": "X6",
        "license": "MIT",
    },
    "cytoscape": {
        "tier": "specialized",
        "entrypoints": [{"kind": "js", "path": "libs/charts/cytoscape/cytoscape.min.js", "load": "body-end"}],
        "global": "cytoscape",
        "license": "MIT",
        "note": "容器必须有明确高度；隐藏容器显示或尺寸变化后调用 cy.resize(); cy.fit();。适合图论分析与复杂交互；简单仪表盘关系图优先 ECharts。",
    },
    "plotly": {
        "tier": "specialized",
        "entrypoints": [{"kind": "js", "path": "libs/charts/plotly/plotly.min.js", "load": "body-end"}],
        "global": "Plotly",
        "license": "MIT",
        "note": "仅用于科学、统计、3D、金融图表或已有 Plotly JSON；普通业务图表优先 ECharts。尺寸变化后调用 Plotly.Plots.resize(gd)。Geo/LaTeX 不得回退公网：Geo 需本地 TopoJSON，LaTeX 需本地 MathJax。",
    },
    "vis-network": {
        "tier": "specialized",
        "entrypoints": [
            {"kind": "css", "path": "libs/charts/vis-network/vis-network.min.css", "load": "head"},
            {"kind": "js", "path": "libs/charts/vis-network/vis-network.min.js", "load": "body-end"},
        ],
        "global": "vis",
        "license": "Apache-2.0 OR MIT",
        "note": "使用 standalone UMD；容器必须有明确高度。适合快速拓扑和物理布局；需要图论分析用 Cytoscape，可编辑流程用 X6。",
    },
    "codemirror": {
        "tier": "specialized",
        "entrypoints": [
            {"kind": "css", "path": "libs/editors/codemirror/codemirror.min.css", "load": "head"},
            {"kind": "js", "path": "libs/editors/codemirror/codemirror.min.js", "load": "body-end"},
        ],
        "global": "CodeMirror",
        "license": "MIT",
    },
    "cropperjs": {
        "tier": "specialized",
        "entrypoints": [{"kind": "js", "path": "libs/ui-components/cropperjs/cropper.min.js", "load": "body-end"}],
        "global": "Cropper",
        "license": "MIT",
        "note": "这是 Cropper.js v2；不要套用 v1 教程或猜测 CSS 入口。",
    },
    "limonte-sweetalert2": {
        "tier": "alias",
        "status": "duplicate",
        "note": "与 sweetalert2 内容完全重复；新页面禁止选择此别名。",
    },
    "dom-to-image": {
        "tier": "specialized",
        "status": "legacy",
        "note": "新页面优先使用 html-to-image 或 html2canvas。",
    },
    "wow": {"tier": "specialized", "status": "legacy"},
    "particles.js": {"tier": "specialized", "status": "legacy"},
    "handsontable": {
        "tier": "license-gated",
        "status": "license-gated",
        "license": "商业使用需核对许可",
    },
    "intro.js": {
        "tier": "license-gated",
        "status": "license-gated",
        "license": "AGPL 或商业许可",
    },
    "fullPage.js": {
        "tier": "license-gated",
        "status": "license-gated",
        "license": "GPLv3 或商业许可；内网应用需核对",
    },
    "tinymce": {
        "tier": "license-gated",
        "status": "license-gated",
        "license": "GPLv2+ 或商业许可",
    },
}

SPECIALIZED_LIBS = {
    "aos", "animate.css", "antv-g2", "antv-g6", "canvas-confetti",
    "crypto-js", "cytoscape", "gridstack.js", "gsap", "jstree",
    "lottie-web", "masonry", "monaco-editor", "noUiSlider", "picocss",
    "plotly", "qrcodejs", "reveal.js", "select2", "showdown", "signature_pad",
    "typed.js", "vis-network", "vue",
}

RESOURCE_OVERRIDES = {}


def metadata_for(lib_name: str, category_name: str) -> dict:
    meta = {"desc": "", "version": "", "category": category_name, "tier": "conditional", "status": "available"}
    meta.update(LIB_META.get(lib_name, {}))
    meta.update(CURATED_META.get(lib_name, {}))
    if lib_name in SPECIALIZED_LIBS and "tier" not in CURATED_META.get(lib_name, {}):
        meta["tier"] = "specialized"
    meta.update(RESOURCE_OVERRIDES.get(lib_name, {}))
    return meta


def scan_lib(lib_dir: Path, base_prefix: str) -> list:
    """Scan a library directory and return list of HTTP paths."""
    files = []
    for f in sorted(lib_dir.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(lib_dir)
        http_path = f"{base_prefix}/{rel.as_posix()}"
        if http_path in EXCLUDED_SERVER_FILES:
            continue
        size_kb = f.stat().st_size / 1024
        files.append({"path": http_path, "name": f.name, "size_kb": round(size_kb, 1)})
    return files


def generate_component_md(lib_name: str, category_name: str, files: list, meta: dict) -> str:
    """Generate a component reference without guessing browser entrypoints."""
    css_files = [f for f in files if f["name"].endswith((".css", ".min.css"))]
    js_files = [f for f in files if f["name"].endswith((".js", ".min.js", ".mjs"))]
    font_files = [f for f in files if f["name"].endswith((".woff", ".woff2", ".ttf", ".eot"))]
    other_files = [f for f in files if f not in css_files + js_files + font_files]

    lines = [
        f"# {lib_name}",
        "",
        f"- 版本：{meta.get('version') or '未记录'}",
        f"- 分类：{meta.get('category', category_name)}",
        f"- 推荐级别：{meta.get('tier', 'conditional')}",
        f"- 状态：{meta.get('status', 'available')}",
        f"- 说明：{meta.get('desc') or '—'}",
    ]
    if meta.get("global"):
        lines.append(f"- 浏览器全局：`{meta['global']}`")
    if meta.get("dependencies"):
        lines.append(f"- 依赖：{', '.join(meta['dependencies'])}")
    if meta.get("license"):
        lines.append(f"- 许可：{meta['license']}")
    if meta.get("note"):
        lines.append(f"- 注意：{meta['note']}")

    entrypoints = meta.get("entrypoints", [])
    if entrypoints:
        lines.extend(["", "## 推荐入口", ""])
        for entry in entrypoints:
            lines.append(
                f"- {entry['kind'].upper()}（{entry['load']}）："
                f"`{{BASE_URL}}/{entry['path']}`"
            )
    else:
        lines.extend([
            "",
            "## 推荐入口",
            "",
            "未验证普通 `<script>` / `<link>` 入口。仅在明确需要此库时，从下方文件清单选择并做浏览器验证。",
        ])

    optional_entrypoints = meta.get("optional_entrypoints", [])
    if optional_entrypoints:
        lines.extend(["", "## 按需入口", ""])
        for entry in optional_entrypoints:
            lines.append(
                f"- {entry['when']}；{entry['kind'].upper()}（{entry['load']}）："
                f"`{{BASE_URL}}/{entry['path']}`"
            )

    sections = [
        ("CSS 文件", css_files),
        ("JS 文件", js_files),
        ("字体文件", font_files),
        ("其他文件", other_files),
    ]
    lines.extend(["", "以下是文件库存，不代表独立浏览器入口。优先使用上面的推荐入口；ESM、CommonJS、内部插件源码可能需要构建工具及额外依赖，不要作为普通 script 直接引用。"])
    active_sections = [(title, items) for title, items in sections if items]
    if sum(len(items) for _, items in active_sections) > 80:
        lines.extend(["", "## 目录", ""])
        for title, _ in active_sections:
            lines.append(f"- [{title}](#{title.replace(' ', '-').lower()})")

    for title, items in active_sections:
        lines.extend(["", f"## {title}", ""])
        limit = 20 if title in {"CSS 文件", "JS 文件"} and len(items) > 30 else 12 if title in {"字体文件", "其他文件"} else len(items)
        for item in items[:limit]:
            lines.append(f"- `{{BASE_URL}}/{item['path']}` ({item['size_kb']} KB)")
        if len(items) > limit:
            lines.append(f"- ……其余 {len(items) - limit} 个文件可通过 `components/index.json` 或服务器目录检索。")

    return "\n".join(lines) + "\n"


def generate_catalog_md(categories: dict) -> str:
    tier_labels = {
        "default": "默认",
        "common": "常用",
        "conditional": "按需",
        "specialized": "专业/低频",
        "license-gated": "许可受限",
        "alias": "别名/禁用",
    }
    lines = [
        "# 资源目录",
        "",
        "推荐级别用于导航，不是白名单。根据目标、内容和视觉风格自主选择并组合资源，无需等待用户点名专业库；仅加载实际使用的资源，避免无意义的功能重复。",
        "",
        "状态说明：`available` 可用；`legacy` 仅兼容旧页面；`duplicate` 不用于新页面；`license-gated` 使用前核对许可。",
        "",
        "## 分类",
        "",
    ]
    for category in sorted(categories):
        lines.append(f"- [{category}](#{category.replace(' ', '-').lower()})")
    for category, libraries in sorted(categories.items()):
        lines.extend(["", f"## {category}", ""])
        ordered = sorted(
            libraries,
            key=lambda item: (
                ["default", "common", "conditional", "specialized", "license-gated", "alias"].index(item["tier"])
                if item["tier"] in tier_labels else 99,
                item["name"].lower(),
            ),
        )
        for item in ordered:
            tier = tier_labels.get(item["tier"], item["tier"])
            status = "" if item["status"] == "available" else f"，{item['status']}"
            lines.append(
                f"- [{item['name']}]({item['file']}) — {tier}{status}；"
                f"{item['desc']}（{item['version'] or '版本未记录'}）"
            )
    return "\n".join(lines) + "\n"


def parse_args():
    parser = argparse.ArgumentParser(description="Generate local web resource component references.")
    parser.add_argument("--server-dir", type=Path, default=DEFAULT_SERV_DIR)
    parser.add_argument("--skill-dir", type=Path, default=DEFAULT_SKILL_DIR)
    return parser.parse_args()


def main():
    global RESOURCE_OVERRIDES
    args = parse_args()
    serv_dir = args.server_dir.expanduser().resolve()
    skill_dir = args.skill_dir.expanduser().resolve()
    metadata_path = skill_dir / "scripts" / "resource_metadata.json"
    RESOURCE_OVERRIDES = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.is_file() else {}
    components_dir = skill_dir / "components"
    libs_dir = serv_dir / "libs"

    if not libs_dir.is_dir():
        raise SystemExit(f"Resource library directory not found: {libs_dir}")

    components_dir.mkdir(parents=True, exist_ok=True)

    print("Scanning libraries...")
    component_count = 0

    # Group by category
    categories = {}

    for category_dir in sorted(libs_dir.iterdir()):
        if not category_dir.is_dir():
            continue
        cat_name = category_dir.name

        for lib_dir in sorted(category_dir.iterdir()):
            if not lib_dir.is_dir():
                continue
            lib_name = lib_dir.name
            base_prefix = f"libs/{cat_name}/{lib_name}"
            files = scan_lib(lib_dir, base_prefix)

            if not files:
                continue

            meta = metadata_for(lib_name, cat_name)
            md_content = generate_component_md(lib_name, cat_name, files, meta)

            md_path = components_dir / f"{lib_name}.md"
            md_path.write_text(md_content, encoding="utf-8")
            component_count += 1

            cat = meta.get("category", cat_name)
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                "name": lib_name,
                "desc": meta.get("desc", ""),
                "version": meta.get("version", ""),
                "file": f"{lib_name}.md",
                "tier": meta.get("tier", "conditional"),
                "status": meta.get("status", "available"),
                "entrypoints": meta.get("entrypoints", []),
                "optional_entrypoints": meta.get("optional_entrypoints", []),
                "global": meta.get("global"),
                "dependencies": meta.get("dependencies", []),
                "license": meta.get("license"),
                "file_count": len(files),
                "size_kb": round(sum(f["size_kb"] for f in files), 1),
                "files": [f["path"] for f in files],
            })

    # Generate fonts component
    print("Scanning fonts...")
    fonts_dir = serv_dir / "fonts"
    font_lines = ["# 字体资源", ""]
    font_lines.append("**入口 CSS**（一行引入全部中英文字体）:")
    font_lines.append("`{BASE_URL}/fonts/fonts.css`")
    font_lines.append("")
    font_lines.append("| 字体 | CSS font-family | 说明 |")
    font_lines.append("|------|----------------|------|")
    for fname, fmeta in FONT_META.items():
        font_lines.append(f"| {fname} | `'{fmeta['css_family']}'` | {fmeta['desc']} |")

    font_lines.append("\n**推荐组合**:")
    font_lines.append("```css")
    font_lines.append("body { font-family: 'Noto Sans SC', 'Inter', sans-serif; }                 /* 通用界面 */")
    font_lines.append("body { font-family: 'Noto Serif SC', 'Merriweather', serif; }              /* 正式报告 */")
    font_lines.append(".fangsong { font-family: 'Zhuque Fangsong', 'Noto Serif SC', serif; }      /* 仿宋正文 */")
    font_lines.append(".literary { font-family: 'LXGW WenKai', 'Noto Serif SC', serif; }          /* 文艺/楷体 */")
    font_lines.append("code { font-family: 'JetBrains Mono', 'LXGW WenKai Mono', monospace; }     /* 代码 */")
    font_lines.append("```")

    (components_dir / "fonts.md").write_text("\n".join(font_lines) + "\n", encoding="utf-8")
    component_count += 1

    index = {
        "schema_version": 2,
        "server_root": "{BASE_URL}",
        "categories": categories,
    }
    (components_dir / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (components_dir / "catalog.md").write_text(generate_catalog_md(categories), encoding="utf-8")

    print(f"\nGenerated {component_count} component files in {components_dir}")
    for cat, libs in sorted(categories.items()):
        print(f"  {cat}: {len(libs)} 个")
    print(f"Total: {sum(len(v) for v in categories.values())} libraries + 1 fonts")


if __name__ == "__main__":
    main()
