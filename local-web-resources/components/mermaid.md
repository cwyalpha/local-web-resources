# mermaid

- 版本：11.12.0
- 分类：数据可视化
- 推荐级别：common
- 状态：available
- 说明：文本转图表（流程图/时序图/甘特图等）
- 浏览器全局：`mermaid`
- 许可：MIT
- 注意：适合流程图、时序图、甘特图等文本图。自动扫描 .mermaid 与手动 render/run 二选一；手动渲染时尽早 initialize({startOnLoad:false})，等待 Promise 并捕获失败，避免再次读取已渲染 SVG。

## 推荐入口

- JS（body-end）：`{BASE_URL}/libs/charts/mermaid/mermaid.min.js`

## JS 文件

- `{BASE_URL}/libs/charts/mermaid/mermaid.min.js` (2684.6 KB)
