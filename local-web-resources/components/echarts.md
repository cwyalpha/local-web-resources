# echarts

- 版本：6.0.0
- 分类：数据可视化
- 推荐级别：default
- 状态：available
- 说明：全功能图表（推荐）。含中国地图: map/china.js（自动注册），省份: map/province/{pinyin}.js
- 浏览器全局：`echarts`
- 许可：Apache-2.0
- 注意：省级地图按需加载 map/province/{pinyin}.js；地图注册文件必须在 ECharts 核心之后。

## 推荐入口

- JS（body-end）：`{BASE_URL}/libs/charts/echarts/echarts.min.js`

## 按需入口

- 使用中国地图时；JS（after-echarts）：`{BASE_URL}/libs/charts/echarts/map/china.js`

## 目录

- [JS 文件](#js-文件)
- [其他文件](#其他文件)

## JS 文件

- `{BASE_URL}/libs/charts/echarts/echarts.common.min.js` (688.6 KB)
- `{BASE_URL}/libs/charts/echarts/echarts.esm.js` (3250.4 KB)
- `{BASE_URL}/libs/charts/echarts/echarts.esm.min.js` (1091.5 KB)
- `{BASE_URL}/libs/charts/echarts/echarts.js` (3613.2 KB)
- `{BASE_URL}/libs/charts/echarts/echarts.min.js` (1091.7 KB)
- `{BASE_URL}/libs/charts/echarts/echarts.simple.min.js` (481.6 KB)
- `{BASE_URL}/libs/charts/echarts/i18n/langEN-obj.js` (4.9 KB)
- `{BASE_URL}/libs/charts/echarts/i18n/langEN-obj.min.js` (2.2 KB)
- `{BASE_URL}/libs/charts/echarts/i18n/langEN.js` (4.9 KB)
- `{BASE_URL}/libs/charts/echarts/i18n/langEN.min.js` (2.2 KB)
- `{BASE_URL}/libs/charts/echarts/i18n/langZH-obj.js` (5.0 KB)
- `{BASE_URL}/libs/charts/echarts/i18n/langZH-obj.min.js` (2.3 KB)
- `{BASE_URL}/libs/charts/echarts/i18n/langZH.js` (4.9 KB)
- `{BASE_URL}/libs/charts/echarts/i18n/langZH.min.js` (2.3 KB)
- `{BASE_URL}/libs/charts/echarts/map/china.js` (569.0 KB)
- `{BASE_URL}/libs/charts/echarts/map/province/anhui.js` (124.5 KB)
- `{BASE_URL}/libs/charts/echarts/map/province/aomen.js` (13.3 KB)
- `{BASE_URL}/libs/charts/echarts/map/province/beijing.js` (98.9 KB)
- `{BASE_URL}/libs/charts/echarts/map/province/chongqing.js` (158.5 KB)
- `{BASE_URL}/libs/charts/echarts/map/province/fujian.js` (111.7 KB)
- ……其余 42 个文件可通过 `components/index.json` 或服务器目录检索。

## 其他文件

- `{BASE_URL}/libs/charts/echarts/map/json/anhui.json` (124.3 KB)
- `{BASE_URL}/libs/charts/echarts/map/json/aomen.json` (13.1 KB)
- `{BASE_URL}/libs/charts/echarts/map/json/beijing.json` (98.7 KB)
- `{BASE_URL}/libs/charts/echarts/map/json/china-outline.json` (158.9 KB)
- `{BASE_URL}/libs/charts/echarts/map/json/china.json` (568.9 KB)
- `{BASE_URL}/libs/charts/echarts/map/json/chongqing.json` (158.3 KB)
- `{BASE_URL}/libs/charts/echarts/map/json/fujian.json` (111.6 KB)
- `{BASE_URL}/libs/charts/echarts/map/json/gansu.json` (103.1 KB)
- `{BASE_URL}/libs/charts/echarts/map/json/guangdong.json` (188.4 KB)
- `{BASE_URL}/libs/charts/echarts/map/json/guangxi.json` (164.0 KB)
- `{BASE_URL}/libs/charts/echarts/map/json/guizhou.json` (127.1 KB)
- `{BASE_URL}/libs/charts/echarts/map/json/hainan.json` (33.3 KB)
- ……其余 24 个文件可通过 `components/index.json` 或服务器目录检索。
