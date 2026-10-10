# 图表统计与中文词云

浏览器示例模板：`{BASE_URL}/templates/chart-analysis.html`。生成页面时替换 BASE_URL；不引用公网脚本。

## 统计

表格清洗、分组、连接和透视可选 [Arquero](../components/arquero.md)，浏览器全局为 `aq`；独立统计可选 [simple-statistics](../components/simple-statistics.md)，浏览器全局为 `ss`。这些计算结果可交给 ECharts、D3 或其他图表库，不绑定绘图框架。

```js
const rows = aq.from([{team: '甲', value: 2}, {team: '甲', value: 4}])
  .groupby('team').rollup({total: d => aq.op.sum(d.value)}).objects();
const values = [1, 2, 3, 4];
const median = ss.median(values);
const sd = ss.sampleStandardDeviation(values);
```

计算前过滤缺失及非有限数值；样本标准差至少需要两个有效值。Arquero 的 Arrow 编解码需要另配 Apache Arrow，本包未包含该依赖。

按需读 [echarts-stat](../components/echarts-stat.md)。加载后提供全局 `ecStat`，纯计算不依赖 ECharts。

```js
const data = [[1, 3], [2, 5], [3, 7]];
const result = ecStat.regression('linear', data);
// result.points 是拟合值；示例斜率为 2，截距为 1。
const bins = ecStat.histogram([1, 2, 2, 3, 5]);
const mean = ecStat.statistics.mean([1, 2, 3]);
const clusters = ecStat.clustering.hierarchicalKMeans([[0,0],[0,1],[10,10],[10,11]], 2, false);
```

使用 ECharts dataset transform 时，在核心和 ecStat 加载后先调用 `echarts.registerTransform(ecStat.transform.histogram)` 或相应 regression / clustering transform。过滤非有限数值；空数据提供可见空状态，不将示例拟合视为因果关系。

## 词云

按需读 [wordcloud2](../components/wordcloud2.md)。全局 `WordCloud` 接收 DOM 容器和词频列表：

```js
await document.fonts.load('32px "Noto Sans SC"', '数据分析');
await document.fonts.ready;
WordCloud(canvas, {
  list: [['数据', 50], ['分析', 35]],
  fontFamily: 'Noto Sans SC', rotateRatio: 0
});
```

预先提供分词后的词语和正数权重；过滤空词和无效权重。Canvas 显式设置 width/height，不能只用 CSS 改像素尺寸。`wordcloudstop` 表示布局完成，随后可以用 `canvas.toBlob()` 导出；监听 `wordcloudabort` 提示失败。
