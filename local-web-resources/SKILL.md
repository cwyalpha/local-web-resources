---
name: local-web-resources
description: 为无后端支撑的内网/离线静态 HTML 页面选择并引用本地 HTTP 前端资源。用于创建或修改仪表盘、报告、HTML 幻灯片、多页面静态站点、图表、表格、表单、静态 JSON 数据页面、中文字体和图标；禁止引用公网 CDN，并从本 Skill 的组件文档选择已验证的浏览器入口。
---

# 内网静态页面资源

## 配置

```text
BASE_URL = https://web-resources.example/resources
```

上面的 `.example` 域名仅用于公开示例。部署前，将此处单点配置替换为 Agent 和最终浏览器均可访问的实际资源地址；用户提供的真实 `BASE_URL` 优先。如果配置仍是示例且用户未提供实际地址，先确认实际地址，再生成成品页面。

所有组件文档用 `{BASE_URL}` 表示该地址。生成 HTML 时必须替换成已确认的实际完整地址；禁止在交付文件中留下示例域名、`{BASE_URL}`、`RESOURCE_SERVER` 等占位符。

## 工作流

1. 根据用户目标、内容特点和视觉风格选择合适的资源。“常用选型参考”提供起点，不是白名单；可以从完整资源目录自主选择并组合已验证的库，以实现所需的表现力和交互。不以库的数量最少为目标；兼顾效果、性能和维护成本，仅加载实际使用的资源，避免无意义的功能重复。
2. 用户已提供真实 `BASE_URL` 且“高频入口速查”已覆盖需求时，直接生成页面；不要先用 `curl`、目录遍历或读取组件文档重复探测资源。只有需要可选入口、插件、主题或特殊初始化时，才读取 `components/{name}.md`。禁止根据文件名猜测 ESM、UMD、Worker 或插件入口。
3. 需要更多能力或视觉选择时，读取 `components/catalog.md`，再读取选中组件文档。推荐级别用于导航，不限制选择；无需等待用户点名，AI 可根据任务自主采用专业库。
4. CSS 通常放在 `<head>`；普通经典脚本放在内容之后；遵循组件文档记录的 `head-defer`、依赖和加载顺序。
5. 完成后检查：无公网运行时资源 URL、无未替换占位符、无缺失路径、无控制台错误；在桌面视口验证主要交互，并检查布局无横向溢出、裁切或难看的强制换行。

## 常用选型参考

| 需求 | 常用资源 | 选型参考 |
|---|---|---|
| HTML 幻灯片、汇报、培训 | Reveal.js | 空间缩放叙事才用 impress.js；按需读 `references/presentations.md` |
| 数据统计、回归、聚类 | echarts-stat + ECharts | 简单汇总直接使用原生 JS |
| 表格数据整理、关联、透视 | Arquero | 简单数据直接使用原生 JS；Arrow 文件需额外依赖，本包未配套 |
| 独立统计计算 | simple-statistics | 已有图表统计能力足够时可复用 |
| 中文词云 | wordcloud2 | 需先提供词语及权重，不负责分词 |
| 页面布局、按钮、弹窗、原生选框 | Bootstrap | 极简文档可只写少量 CSS |
| 图标 | Lucide；多粗细或双色风格可用 Phosphor | 按页面风格选择，也可使用目录中其他图标库 |
| 图表、仪表盘、中国地图 | ECharts | 可根据图表类型、风格与交互选择 Chart.js、Plotly 等 |
| 自定义 SVG、复杂数据驱动图形 | D3 | 普通业务图表继续使用 ECharts |
| 流程图、时序图、甘特图 | Mermaid | 需要高度定制交互时再用 D3/图编辑器 |
| 搜索、排序、分页、筛选表格 | Tabulator | 仅有几十行数据时用原生表格；旧 jQuery 页面可用 DataTables |
| 少量页面状态、选框联动、折叠 | 原生 JS；复杂后使用 Alpine.js | 纯展示页不要引入 |
| 可搜索或多选下拉框 | Choices.js | 普通单选框使用原生 `<select>` |
| Excel 导入导出 | SheetJS | 仅 CSV 时使用 PapaParse |
| 日期格式化 | Day.js | 简单格式可用原生 `Intl.DateTimeFormat` |
| 模糊搜索 | Fuse.js | 精确筛选用原生数组方法 |
| HTML 区域导出图片 | html-to-image | 复杂 Canvas 场景再考虑 html2canvas |
| Markdown 渲染 | Marked + DOMPurify | 内容完全受信任时仍建议保留净化 |
| 代码高亮 | highlight.js | 需要 Prism 插件体系时可选 Prism |

## 高频入口速查

下表地址应与本配套包一致；实际内网连通性以部署复验为准。能满足任务时直接使用，不必再读取组件文档；不要因此把未使用的库全部引入。

| 资源 | CSS / JS 入口 |
|---|---|
| 中文与英文字体 | CSS: `{BASE_URL}/fonts/fonts.css` |
| Bootstrap | CSS: `{BASE_URL}/libs/css-frameworks/bootstrap/css/bootstrap.min.css`；JS: `{BASE_URL}/libs/css-frameworks/bootstrap/js/bootstrap.bundle.min.js` |
| Lucide | JS: `{BASE_URL}/libs/icons/lucide/lucide.min.js` |
| Alpine.js | head + `defer`: `{BASE_URL}/libs/js-core/alpinejs/cdn.min.js` |
| ECharts | JS: `{BASE_URL}/libs/charts/echarts/echarts.min.js`；中国地图按需在其后加载 `{BASE_URL}/libs/charts/echarts/map/china.js` |
| D3 | JS: `{BASE_URL}/libs/charts/d3/d3.min.js` |
| Mermaid | JS: `{BASE_URL}/libs/charts/mermaid/mermaid.min.js` |
| Tabulator | Bootstrap CSS 后加载 CSS: `{BASE_URL}/libs/tables/tabulator-tables/css/tabulator_bootstrap5.min.css`；JS: `{BASE_URL}/libs/tables/tabulator-tables/js/tabulator.min.js` |
| Choices.js | CSS: `{BASE_URL}/libs/ui-components/choices.js/choices.min.css`；JS: `{BASE_URL}/libs/ui-components/choices.js/choices.min.js` |
| SheetJS | JS: `{BASE_URL}/libs/utils/xlsx/xlsx.full.min.js` |

## 静态页面约束

- 页面间跳转使用相对 URL，例如 `reports/detail.html?id=42`；不要发明服务端路由。
- 静态 JSON 使用相对 URL，并为加载中、空数据、404、解析失败提供可见状态。
- `fetch('./data.json')` 需要通过 HTTP/HTTPS 打开页面；如果页面必须支持 `file://` 双击打开，将数据内嵌，或改为同目录 `data.js` 给 `window.PAGE_DATA` 赋值。
- 简单交互优先原生表单控件和 JS。Alpine.js 必须以 `defer` 加载，不要放在正文末尾后再猜初始化时机。
- 不使用 htmx，不生成依赖后端返回 HTML 片段、API 写操作、登录会话或 WebSocket 的方案。
- 多页面共享导航可复制静态片段；没有构建步骤时，不要使用运行时 `fetch` HTML 片段作为必需导航。

详见 `references/static-pages.md`。

## 稳健与安全规则

- 不要把“文件存在”等同于“可直接用”。`components/index.json` 中的 `entrypoints`、`global`、`dependencies`、`tier` 和 `status` 才是机器可用依据。
- 不要笼统地选择所有 `.min.js`；`.min` 只表示压缩，不表示适合普通 `<script>`。
- 不要从 CSS 主题推断 JS 依赖；例如 Tabulator 的 Bootstrap 5 主题需要 Bootstrap CSS，但 Tabulator JS 不依赖 bootstrap.bundle。
- 图表容器必须有明确高度；窗口尺寸变化以及 Bootstrap tab/modal 展示后调用 `chart.resize()`。
- 使用 ECharts 地图时，先加载 `echarts.min.js`，再加载地图注册文件。
- 用 Lucide 时，在 DOM 就绪后调用 `lucide.createIcons()`；动态插入后再次调用。图标名用官方 kebab-case，例如 `qr-code`，不要写成 `qrcode`。
- 不可信 Markdown/HTML 必须通过 DOMPurify；不要假设 Markdown 解析器会自动净化。
- 解析用户提供的 JSON、CSV、Excel 文件时限制大小、捕获异常，不把文件内容拼接进 `innerHTML`。

## 字体

统一入口见“高频入口速查”。

- 通用中文界面：`'Noto Sans SC', 'Inter', sans-serif`
- 正式报告、长篇正文：`'Noto Serif SC', 'Merriweather', serif`
- 公文仿宋、正式说明文字：`'Zhuque Fangsong', 'Noto Serif SC', serif`
- 文艺、文化或楷体风格：`'LXGW WenKai', 'Noto Serif SC', serif`
- 封面与表现性标题：`'Smiley Sans', sans-serif`，使用 `font-style: oblique; font-weight: 400`，字体本身为倾斜设计。
- 圆润风格页面：`'Resource Han Rounded CN', 'Noto Sans SC', sans-serif`，提供 400 和 700 字重。
- 纯英文衬线正文：`'Merriweather', Georgia, serif`
- 中文等宽内容：`'LXGW WenKai Mono', 'JetBrains Mono', monospace`
- 纯代码：`'JetBrains Mono', monospace`

不要用 Zhuque Fangsong 代替所有中文正文；它适合仿宋语义。不要为同一文本同时堆叠多个风格相近的首选字体。

Canvas 不继承 `body` 的 CSS 字体，也不会因为字体稍后加载而自动重绘。ECharts 使用 Web 字体时，先等待所用字体，再初始化；在 option 中显式设置字体后 `setOption`，最后设置渲染就绪标志：

```js
window.__RENDER_READY__ = false;
await Promise.all([
  document.fonts.load('16px "Noto Sans SC"', '中文字体检查'),
  document.fonts.ready
]);
const chart = echarts.init(document.getElementById('chart'));
option.textStyle = {
  ...option.textStyle,
  fontFamily: '"Noto Sans SC", sans-serif'
};
chart.setOption(option);
requestAnimationFrame(() => { window.__RENDER_READY__ = true; });
```

需要不同字形时，在 `title.textStyle`、`legend.textStyle`、`axisLabel` 或 `series.label` 中显式覆盖；不要假设 ECharts Canvas 会继承页面 CSS。

Mermaid、SVG 和普通 DOM 也使用上述 CSS `font-family`；截图前等待 `document.fonts.ready`。

完整字体信息见 `components/fonts.md`。

## 进一步查阅

- HTML 幻灯片、插件与图表生命周期：`references/presentations.md`
- 图表统计和中文词云：`references/chart-analysis.md`
- 配套更新和校验：`references/maintenance.md`
- 全部资源及推荐级别：`components/catalog.md`
- 机器索引：`components/index.json`
- 静态 JSON、多页面、表单、图表和导出模式：`references/static-pages.md`
- Nginx MIME、CORS 和缓存检查：`references/nginx.md`
- 本地检查：运行 `python scripts/validate_resources.py`
