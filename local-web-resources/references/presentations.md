# HTML 演示与幻灯片

默认使用 Reveal.js；只有明确需要空间缩放、旋转、非线性叙事时才用 impress.js。这两种模式均通过内网 HTTP 资源加载，不要求 npm 或构建工具。页面数据默认内嵌。

## 快速开始

1. 读取 [Reveal.js 入口](../components/reveal.js.md)。复制 `{BASE_URL}/templates/presentation-reveal.html` 的结构，将所有 `{BASE_URL}` 替换为 SKILL.md 配置地址。
2. 保留 `.reveal > .slides > section` 结构；横向章节使用同级 section，纵向子页才嵌套 section。
3. 按任务替换示例内容和数据，删掉不需要的插件及脚本。默认 1280×720、16:9，不用滚动页面模拟放映。
4. 给 body 加 `class="deck-dark"` 可使用同一模板的暗色样式。共用 `{BASE_URL}/templates/presentation.css`，避免全局 Bootstrap 重置与 Reveal 样式冲突。

## 核心与插件

CSS 顺序：字体 → Reveal reset → Reveal 核心 → 单一主题 → 插件样式 → 页面自定义样式。经典脚本顺序：Reveal → 按需插件 → 页面初始化。使用 `new Reveal(options)` 返回的实例，并等待 `initialize()`。

| 插件 | 全局对象 | 用途 |
|---|---|---|
| Markdown | `RevealMarkdown` | 内嵌 `<textarea data-template>` Markdown；非可信文本先净化 |
| Highlight | `RevealHighlight` | 代码高亮；使用 Reveal 自带插件，不重复加载全局 highlight.js |
| Notes | `RevealNotes` | `aside.notes`、演讲者窗口与计时，按 S 打开；需允许用户触发的弹窗 |
| Search | `RevealSearch` | Ctrl/Cmd+F 搜索幻灯片内容 |
| Zoom | `RevealZoom` | Alt+单击放大，Linux 使用 Ctrl+单击 |
| Math | `RevealMath.KaTeX` | 数学公式；必须配置本地资源 |

公式配置示例（模板内已包含）：

```js
katex: {
  local: '{BASE_URL}/libs/js-core/katex',
  extensions: []
}
```

Reveal 5 的 KaTeX 插件会在 local 地址后拼接 `/dist/`，本包已提供对应入口。不要使用无效的 katexScript/katexStyles 配置键，否则会回退到公网 CDN。库自带的 MathJax 配置可能默认访问公网，本包默认只使用上述 KaTeX 模式。只加载需要的插件，并在 `plugins: [...]` 中注册。

## 图表、流程图和动画

- ECharts 容器必须有明确尺寸；隐藏页初始化使用明确 width/height，显示后通过 `slidechanged` 与 `resize` 事件调用实例 `resize()`。
- 先等待实际使用的中文字体，再初始化 Canvas；ECharts option 显式设置 `textStyle.fontFamily`。
- Mermaid 在任何字体等待等 await 之前同步设置 `startOnLoad:false`，避免 DOMContentLoaded 触发自动扫描。幻灯片初始化前通常处于隐藏状态，使用 `await mermaid.render(id, source)` 在临时可测量容器中生成 SVG，再放回幻灯片。不要在 display:none 的页内直接 run，也不要对已经转换成 SVG 的内容重复渲染。
- 普通分步显示用 `.fragment`，对应元素转场用 Reveal Auto-Animate；仅复杂时间线才引入已有 GSAP。
- 截图/打印就绪标志为 `window.__RENDER_READY__`；必须等字体、图表和异步流程图就绪后设为 true。

## 放映与 PDF 打印

方向键/空格翻页，Esc 总览，F 全屏，S 演讲者备注。通过 HTTP/HTTPS 打开放映页。无需服务端会话。

在演示地址的查询串中加入 `print-pdf`，等待全部图表与字体就绪，再用 Chromium 打印为 PDF，开启背景图形、关闭页眉页脚。模板使用 `pdfSeparateFragments:false`，避免每个分步状态生成额外页。打印时关闭图表动画、渲染所有隐藏页图表，并检查一张幻灯片是否恰好对应一页。

HTML 演示不是 PPTX；此工作流不承诺可编辑 PowerPoint 文件转换。

## 特殊模式

空间叙事阅读 [impress.js](../components/impress.js.md)，参考 `{BASE_URL}/templates/presentation-impress.html`。每个 `.step` 设置坐标与必要的缩放/旋转，不把空间动画用于密集正文；保留不支持时的顺序阅读提示。
