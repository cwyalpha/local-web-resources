---
name: render-web-artifacts
description: 使用真实 Chromium 将 HTML、网页、Markdown、Mermaid 和 ECharts 渲染为桌面端 PNG、SVG 或 PDF。用于网页整页截图、唯一元素或图表截图、中文 Markdown 转 PDF、流程图与数据图表导出，以及需要等待字体、图片、静态 JSON 或前端异步渲染完成的可视化产物生成。
---

# 渲染网页产物

统一使用 `scripts/render.mjs`，不要临时编写 Puppeteer 或 Playwright 脚本。输入内容视为可信；此工具不会隔离恶意 HTML 或 JavaScript。

## 工作流

1. 根据输入选子命令：现有网页用 `html`，Markdown 文档用 `markdown`，纯 Mermaid 源码用 `mermaid`，严格 JSON 格式的 ECharts option 用 `echarts`。
2. 先确定输出格式。HTML 和 Markdown 支持 PNG、JPEG、PDF；Mermaid 和 ECharts 支持 PNG、SVG、PDF。
3. 截取网页中的单个图表或区域时传唯一 `--selector`。不要传可能匹配多个元素的宽泛选择器。
4. 对异步图表，在页面初始阶段设置 `window.__RENDER_READY__ = false`，渲染结束后改为 `true`；或使用根元素的 `data-render-ready="false|true"`。
5. 执行脚本，检查退出码和 stdout 的 JSON 摘要；不要只检查输出文件是否存在。
6. 生成 PNG 或 PDF 后进行视觉检查，重点检查中文字体、图例、坐标轴、分页、裁切和空白区域。

## 快速命令

执行前，根据当前加载的这个 `SKILL.md` 的实际位置设置一次 `SKILL_DIR`。它必须指向包含本文件的 Skill 根目录；不要假设固定安装目录，也不要在命令中保留下方占位符。

```bash
SKILL_DIR="<当前 render-web-artifacts/SKILL.md 所在目录>"
test -f "$SKILL_DIR/scripts/render.mjs"

# HTML 整页
node "$SKILL_DIR/scripts/render.mjs" html \
  --input report.html --output report.png

# 唯一图表元素；Canvas、SVG、WebGL 和普通 DOM 均可
node "$SKILL_DIR/scripts/render.mjs" html \
  --input dashboard.html --selector '#sales-chart' --output sales.png

# 中文 Markdown 转 PDF
node "$SKILL_DIR/scripts/render.mjs" markdown \
  --input report.md --output report.pdf --paper A4

# Mermaid 与 ECharts
node "$SKILL_DIR/scripts/render.mjs" mermaid \
  --input flow.mmd --output flow.svg
node "$SKILL_DIR/scripts/render.mjs" echarts \
  --input option.json --output chart.png --width 1200 --height 675
```

## 关键规则

- 本地 HTML 和 Markdown 由临时 loopback HTTP 服务打开，因此相对 CSS、JS、图片、页面链接和静态 JSON 可正常解析。
- 引用 `local-web-resources` 的 HTML 必须已经写入容器可访问的真实内网 URL；本 Skill 不读取或替换其 `BASE_URL`。
- `--selector` 必须恰好匹配一个可见元素。浮层若挂载在该元素外，应选择共同父容器或改用整页截图。
- 默认关闭截图动画，并等待 load、网络短暂空闲、图片、字体、ready 标志及元素边界稳定。只有确实需要捕获动画状态时才传 `--keep-animations`。
- ECharts 输入必须是 JSON，不接受 JavaScript 函数。需要 formatter 函数等逻辑时，改用完整 HTML。
- Mermaid 和 ECharts 的 SVG/PDF 走矢量渲染；任意 HTML 的元素截图输出 PNG/JPEG。
- 默认允许网络请求。资源失败会写入警告；需要任何 4xx/5xx、请求失败或 console error 都导致失败时传 `--strict`。
- 整页截图最大高度为 30,000px；超出时拆分页面或使用 PDF。
- 若输出用于 Word，先生成 PNG、SVG 或 PDF，再交给现有 docx Skill 组装。

完整参数、Markdown fenced block 格式、ready 协议和故障说明见 `references/options.md`。
