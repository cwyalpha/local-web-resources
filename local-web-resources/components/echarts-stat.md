# echarts-stat

- 版本：1.2.0
- 分类：数据可视化
- 推荐级别：conditional
- 状态：available
- 说明：统计、直方图、回归和聚类。
- 浏览器全局：`ecStat`
- 依赖：ECharts（仅用于可视化时）
- 许可：BSD（上游包元数据声明；上游发行包未附独立许可文本）
- 注意：可独立计算；ECharts dataset 转换需 echarts.registerTransform(ecStat.transform.histogram) 等显式注册。

## 推荐入口

- JS（body-end）：`{BASE_URL}/libs/charts/echarts-stat/ecStat.min.js`

以下是文件库存，不代表独立浏览器入口。优先使用上面的推荐入口；ESM、CommonJS、内部插件源码可能需要构建工具及额外依赖，不要作为普通 script 直接引用。

## JS 文件

- `{BASE_URL}/libs/charts/echarts-stat/ecStat.min.js` (15.7 KB)
