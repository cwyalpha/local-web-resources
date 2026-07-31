# 静态页面模式

## 目录

- [页面间跳转](#页面间跳转)
- [加载静态 JSON](#加载静态-json)
- [支持双击打开](#支持双击打开)
- [表单和选择框](#表单和选择框)
- [图表尺寸](#图表尺寸)
- [图标](#图标)
- [导出](#导出)

## 页面间跳转

使用相对地址并保留普通链接行为：

```html
<a href="./detail.html?id=42">查看详情</a>
<a href="../index.html">返回首页</a>
```

用 `URLSearchParams` 读取查询参数。不要依赖 History API 服务端回退规则。

## 加载静态 JSON

```html
<p id="status" role="status">正在加载数据……</p>
<div id="content" hidden></div>
<script>
async function loadPageData() {
  const status = document.getElementById('status');
  try {
    const response = await fetch('./data/report.json', { cache: 'no-cache' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    status.textContent = data.length ? '' : '暂无数据';
    document.getElementById('content').hidden = false;
    renderPage(data);
  } catch (error) {
    console.error(error);
    status.textContent = '数据加载失败，请确认页面通过 HTTP 打开且 JSON 文件存在。';
  }
}
loadPageData();
</script>
```

始终处理空数组、缺字段、404 和非法 JSON。外部文本用 `textContent`，不要直接赋给 `innerHTML`。

## 支持双击打开

浏览器通常不允许 `file://` 页面使用 `fetch()` 读取旁边的 JSON。必须支持双击打开时，二选一：

1. 数据量小时直接内嵌 `<script type="application/json" id="page-data">`。
2. 使用 `data.js`：

```js
window.PAGE_DATA = [{"name": "示例", "value": 1}];
```

然后用普通 `<script src="./data.js"></script>` 加载。不要通过动态代码执行解析数据。

## 表单和选择框

- 普通单选、多选和少量选项：原生 `<select>`、checkbox、radio。
- 可搜索、多选标签、选项很多：Choices.js。
- 多组筛选条件、显示隐藏、计算属性：Alpine.js。
- 可访问性：每个控件关联 `<label>`，动态结果区域使用 `aria-live`。
- 筛选结果应显示“共 N 条”，无结果时提供清晰空状态。

Alpine.js 必须这样加载：

```html
<script defer src="{BASE_URL}/libs/js-core/alpinejs/cdn.min.js"></script>
```

## 图表尺寸

```css
.chart-box { width: 100%; height: 460px; min-height: 320px; }
.card-body, .tab-pane { min-width: 0; }
```

```js
const charts = [];
function resizeCharts() {
  requestAnimationFrame(() => charts.forEach(chart => chart.resize()));
}
window.addEventListener('resize', resizeCharts);
document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
  tab.addEventListener('shown.bs.tab', resizeCharts);
});
setTimeout(resizeCharts, 0);
setTimeout(resizeCharts, 250);
```

图表处于初始隐藏容器时，优先在首次显示后初始化。

## 图标

```html
<i data-lucide="chart-no-axes-combined" aria-hidden="true"></i>
<script src="{BASE_URL}/libs/icons/lucide/lucide.min.js"></script>
<script>lucide.createIcons();</script>
```

动态更新 DOM 后再次调用 `lucide.createIcons()`。有文字标签的装饰图标使用 `aria-hidden="true"`。

## 导出

- CSV：PapaParse 或手工生成简单 CSV。
- Excel：SheetJS `xlsx.full.min.js`，浏览器全局为 `XLSX`。
- 图片：优先 html-to-image；导出前等待字体加载 `await document.fonts.ready`。
- PDF：现有 jsPDF 适合程序化文档；复杂中文页面优先浏览器打印为 PDF。

文件名需清理 `/\:*?"<>|` 等非法字符，并提供导出失败提示。
