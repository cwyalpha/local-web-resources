# katex

- 版本：0.16.47
- 分类：JS 核心
- 推荐级别：conditional
- 状态：available
- 说明：数学公式渲染
- 浏览器全局：`katex`
- 许可：MIT
- 注意：长块级公式可能撑宽较窄的卡片或分栏；为 .katex-display 或其容器设置 overflow-x: auto。

## 推荐入口

- CSS（head）：`{BASE_URL}/libs/js-core/katex/katex.min.css`
- JS（body-end）：`{BASE_URL}/libs/js-core/katex/katex.min.js`

## 按需入口

- 需要自动扫描公式时；JS（after-katex）：`{BASE_URL}/libs/js-core/katex/contrib/auto-render.min.js`

以下是文件库存，不代表独立浏览器入口。优先使用上面的推荐入口；ESM、CommonJS、内部插件源码可能需要构建工具及额外依赖，不要作为普通 script 直接引用。

## CSS 文件

- `{BASE_URL}/libs/js-core/katex/dist/katex.min.css` (23.4 KB)
- `{BASE_URL}/libs/js-core/katex/katex.min.css` (23.3 KB)

## JS 文件

- `{BASE_URL}/libs/js-core/katex/contrib/auto-render.min.js` (3.4 KB)
- `{BASE_URL}/libs/js-core/katex/contrib/copy-tex.min.js` (1.6 KB)
- `{BASE_URL}/libs/js-core/katex/contrib/mathtex-script-type.min.js` (1.3 KB)
- `{BASE_URL}/libs/js-core/katex/contrib/mhchem.min.js` (32.9 KB)
- `{BASE_URL}/libs/js-core/katex/contrib/render-a11y-string.min.js` (8.3 KB)
- `{BASE_URL}/libs/js-core/katex/dist/contrib/auto-render.min.js` (3.4 KB)
- `{BASE_URL}/libs/js-core/katex/dist/contrib/mhchem.min.js` (32.9 KB)
- `{BASE_URL}/libs/js-core/katex/dist/katex.min.js` (266.1 KB)
- `{BASE_URL}/libs/js-core/katex/katex.min.js` (266.1 KB)

## 字体文件

- `{BASE_URL}/libs/js-core/katex/fonts/KaTeX_AMS-Regular.ttf` (62.1 KB)
- `{BASE_URL}/libs/js-core/katex/fonts/KaTeX_AMS-Regular.woff` (32.7 KB)
- `{BASE_URL}/libs/js-core/katex/fonts/KaTeX_AMS-Regular.woff2` (27.4 KB)
- `{BASE_URL}/libs/js-core/katex/fonts/KaTeX_Caligraphic-Bold.ttf` (12.1 KB)
- `{BASE_URL}/libs/js-core/katex/fonts/KaTeX_Caligraphic-Bold.woff` (7.5 KB)
- `{BASE_URL}/libs/js-core/katex/fonts/KaTeX_Caligraphic-Bold.woff2` (6.8 KB)
- `{BASE_URL}/libs/js-core/katex/fonts/KaTeX_Caligraphic-Regular.ttf` (12.1 KB)
- `{BASE_URL}/libs/js-core/katex/fonts/KaTeX_Caligraphic-Regular.woff` (7.5 KB)
- `{BASE_URL}/libs/js-core/katex/fonts/KaTeX_Caligraphic-Regular.woff2` (6.7 KB)
- `{BASE_URL}/libs/js-core/katex/fonts/KaTeX_Fraktur-Bold.ttf` (19.1 KB)
- `{BASE_URL}/libs/js-core/katex/fonts/KaTeX_Fraktur-Bold.woff` (13.0 KB)
- `{BASE_URL}/libs/js-core/katex/fonts/KaTeX_Fraktur-Bold.woff2` (11.1 KB)
- ……其余 48 个文件可通过 `components/index.json` 或服务器目录检索。

## 其他文件

- `{BASE_URL}/libs/js-core/katex/LICENSE` (1.1 KB)
