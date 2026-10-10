# 资源目录

推荐级别用于导航，不是白名单。根据目标、内容和视觉风格自主选择并组合资源，无需等待用户点名专业库；仅加载实际使用的资源，避免无意义的功能重复。

状态说明：`available` 可用；`legacy` 仅兼容旧页面；`duplicate` 不用于新页面；`license-gated` 使用前核对许可。

## 分类

- [CSS 框架](#css-框架)
- [JS 核心](#js-核心)
- [UI 组件](#ui-组件)
- [代码高亮](#代码高亮)
- [动画](#动画)
- [图标](#图标)
- [工具](#工具)
- [布局](#布局)
- [数据可视化](#数据可视化)
- [编辑器](#编辑器)
- [表格](#表格)

## CSS 框架

- [bootstrap](bootstrap.md) — 默认；响应式布局、组件系统（5.3.8）
- [bulma](bulma.md) — 按需；现代 CSS 框架（1.0.4）
- [modern-normalize](modern-normalize.md) — 按需；现代 CSS 重置（3.0.1）
- [normalize](normalize.md) — 按需；CSS 重置（8.0.1）
- [tailwindcss-browser](tailwindcss-browser.md) — 按需；原子化 CSS（浏览器版，放在 <head> 中）（4.1.13）
- [animate.css](animate.css.md) — 专业/低频；CSS 动画库（4.1.1）
- [picocss](picocss.md) — 专业/低频；极简 Classless CSS（2.1.1）

## JS 核心

- [alpinejs](alpinejs.md) — 默认；适合静态页面的轻量交互层（script 必须使用 defer）（3.17.4）
- [dayjs](dayjs.md) — 常用；轻量日期库（1.11.23）
- [dompurify](dompurify.md) — 常用；HTML 净化（3.4.16）
- [lodash.js](lodash.js.md) — 常用；工具函数库（4.17.21）
- [marked](marked.md) — 常用；Markdown 渲染（16.3.0）
- [jquery](jquery.md) — 按需；DOM 操作（3.7.1）
- [katex](katex.md) — 按需；数学公式渲染（0.16.47）
- [markdown-it](markdown-it.md) — 按需；Markdown 渲染；不可信输出仍须 DOMPurify（14.3.2）
- [vue](vue.md) — 按需；静态页面按需使用 Vue 全局生产构建（3.5.43）
- [crypto-js](crypto-js.md) — 专业/低频；加密工具（4.2.0）

## UI 组件

- [choices.js](choices.js.md) — 常用；下拉/标签输入（11.2.4）
- [sweetalert2](sweetalert2.md) — 常用；弹窗对话框（11.23.0）
- [flatpickr](flatpickr.md) — 按需；日期选择器（4.6.13）
- [nprogress](nprogress.md) — 按需；顶部进度条（0.2.0）
- [toastr.js](toastr.js.md) — 按需；通知提示（2.1.4）
- [cropperjs](cropperjs.md) — 专业/低频；图片裁剪（v2 API）（2.0.0）
- [driver.js](driver.js.md) — 专业/低频；新手引导/高亮（1.9.0）
- [jstree](jstree.md) — 专业/低频；树形控件（依赖 jQuery）（3.3.17）
- [noUiSlider](noUiSlider.md) — 专业/低频；范围滑块（15.8.1）
- [select2](select2.md) — 专业/低频；增强下拉框（依赖 jQuery）（4.0.13）
- [typed.js](typed.js.md) — 专业/低频；打字机效果（2.1.0）
- [intro.js](intro.js.md) — 许可受限，license-gated；新手引导（8.3.2）
- [limonte-sweetalert2](limonte-sweetalert2.md) — 别名/禁用，duplicate；SweetAlert2 另一版本（11.23.0）

## 代码高亮

- [highlight.js](highlight.js.md) — 常用；代码高亮（推荐）。主题在 styles/ 下，如 github.min.css、github-dark.min.css（11.11.1）
- [prism](prism.md) — 按需；轻量代码高亮（1.30.0）

## 动画

- [canvas-confetti](canvas-confetti.md) — 按需；彩纸动画（1.9.4）
- [countup.js](countup.js.md) — 按需；数字递增动画。用 countUp.umd.min.js，调用: new countUp.CountUp(id, val)（2.10.1）
- [aos](aos.md) — 专业/低频；滚动动画（注意：文件名 aos.js / aos.css，无 .min）（2.3.4）
- [gsap](gsap.md) — 专业/低频；专业动画引擎。插件: ScrollTrigger.min.js, Draggable.min.js 等（3.13.0）
- [lottie-web](lottie-web.md) — 专业/低频；Lottie 动画播放（5.13.0）
- [particles.js](particles.js.md) — 专业/低频，legacy；粒子背景效果（2.0.0）
- [wow](wow.md) — 专业/低频，legacy；滚动触发动画（1.1.2）

## 图标

- [lucide](lucide.md) — 默认；SVG 图标（静态页面默认推荐）（1.55.0）
- [bootstrap-icons](bootstrap-icons.md) — 按需；图标库 2000+。用法: <i class="bi bi-check"></i>（1.13.1）
- [font-awesome](font-awesome.md) — 按需；图标库 30000+。用法: <i class="fa-solid fa-check"></i>（7.0.1）
- [material-design-icons](material-design-icons.md) — 按需；Material 图标 2000+。用法: <span class="material-icons">check</span>（4.0.0）
- [phosphor-icons](phosphor-icons.md) — 按需；多粗细、填充与双色图标；根据页面风格选择字重。（2.1.2）
- [remixicon](remixicon.md) — 按需；图标库 2800+。用法: <i class="ri-check-line"></i>（4.6.0）
- [tabler-icons](tabler-icons.md) — 按需；图标库 5000+。用法: <i class="ti ti-check"></i>（3.35.0）

## 工具

- [FileSaver.js](FileSaver.js.md) — 常用；文件保存（2.0.5）
- [fuse.js](fuse.js.md) — 常用；前端模糊搜索（7.1.0）
- [html-to-image](html-to-image.md) — 常用；HTML 转图片（1.11.13）
- [PapaParse](PapaParse.md) — 常用；CSV 解析（5.7.0）
- [xlsx](xlsx.md) — 常用；Excel 读写 (SheetJS)（0.20.3）
- [clipboard.js](clipboard.js.md) — 按需；复制到剪贴板（2.0.11）
- [html2canvas](html2canvas.md) — 按需；HTML 转 Canvas/图片（1.4.1）
- [jspdf](jspdf.md) — 按需；浏览器 PDF 生成；中文须显式嵌入支持字体（3.0.4）
- [jszip](jszip.md) — 按需；ZIP 文件读写（3.10.2）
- [localforage](localforage.md) — 按需；本地存储（1.10.0）
- [signature_pad](signature_pad.md) — 按需；Canvas 手写签名（5.1.4）
- [turndown](turndown.md) — 按需；HTML 转 Markdown（7.2.4）
- [dom-to-image](dom-to-image.md) — 专业/低频，legacy；DOM 转图片（2.6.0）
- [qrcodejs](qrcodejs.md) — 专业/低频；二维码生成（1.0.0）
- [showdown](showdown.md) — 专业/低频；Markdown→HTML（2.1.0）

## 布局

- [Sortable](Sortable.md) — 常用；拖拽排序（1.15.7）
- [reveal.js](reveal.js.md) — 按需；HTML 幻灯片默认框架，支持备注、分步显示与 PDF 打印。（5.2.1）
- [simplebar](simplebar.md) — 按需；自定义滚动条（6.3.3）
- [Swiper](Swiper.md) — 按需；触摸轮播与滑动页面（11.2.10）
- [gridstack.js](gridstack.js.md) — 专业/低频；网格拖拽（12.3.3）
- [impress.js](impress.js.md) — 专业/低频；空间缩放和旋转的非线性 HTML 演示。（2.0.0）
- [masonry](masonry.md) — 专业/低频；瀑布流布局（4.2.2）
- [fullPage.js](fullPage.js.md) — 许可受限，license-gated；全屏滚动（4.0.37）

## 数据可视化

- [echarts](echarts.md) — 默认；全功能图表（推荐）。含中国地图: map/china.js（自动注册），省份: map/province/{pinyin}.js（6.1.0）
- [d3](d3.md) — 常用；数据驱动可视化（7.9.0）
- [mermaid](mermaid.md) — 常用；文本转图表（流程图/时序图/甘特图等）（11.12.0）
- [apexcharts](apexcharts.md) — 按需；交互式图表（5.3.5）
- [arquero](arquero.md) — 按需；表格数据变换、分组汇总、连接和透视；结果可传给任意图表库。（8.0.3）
- [Chart.js](Chart.js.md) — 按需；轻量图表（4.5.0）
- [echarts-stat](echarts-stat.md) — 按需；统计、直方图、回归和聚类。（1.2.0）
- [simple-statistics](simple-statistics.md) — 按需；通用统计计算，包括分位数、标准差、相关性和回归。（7.12.1）
- [wordcloud2](wordcloud2.md) — 按需；Canvas / HTML 中文词云。（1.2.3）
- [antv-g2](antv-g2.md) — 专业/低频；图形语法图表（5.4.1）
- [antv-g6](antv-g6.md) — 专业/低频；图/关系可视化（5.0.49）
- [antv-x6](antv-x6.md) — 专业/低频；流程图/DAG 编辑器（3.1.7）
- [cytoscape](cytoscape.md) — 专业/低频；图论分析、复杂关系网络与交互（3.34.3）
- [plotly](plotly.md) — 专业/低频；科学、统计、3D 与金融图表（3.7.0）
- [vis-network](vis-network.md) — 专业/低频；快速拓扑/关系网络与物理布局（10.1.0）

## 编辑器

- [codemirror](codemirror.md) — 专业/低频；经典全局脚本版代码编辑器（CodeMirror 5）（5.65.21）
- [monaco-editor](monaco-editor.md) — 专业/低频；VS Code 编辑器（0.53.0）
- [tinymce](tinymce.md) — 许可受限，license-gated；富文本编辑器（8.1.2）

## 表格

- [tabulator-tables](tabulator-tables.md) — 默认；独立表格库（6.6.1）
- [datatables](datatables.md) — 按需；jQuery/原生初始化表格，含 Bootstrap 5 适配（2.3.8）
- [handsontable](handsontable.md) — 许可受限，license-gated；类 Excel 表格（16.1.1）
