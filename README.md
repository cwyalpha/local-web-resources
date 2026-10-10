# Local Web Resources

面向内网和离线 Agent 的静态前端资源库、配套资源服务器，以及基于 Chromium 的网页产物渲染 Skill。

## 目录

- `local-web-resources/`：指导 Agent 为静态 HTML 选择本地 JS、CSS、字体和图标，并使用已验证的浏览器入口。
- `web-resources-server/`：可直接由 Nginx 等静态服务器托管的前端库、字体、模板和资源清单。
- `render-web-artifacts/`：将 HTML、Markdown、Mermaid 和 ECharts 渲染为 PNG、JPEG、SVG 或 PDF。

`local-web-resources` 与 `web-resources-server` 应保持同一版本。`render-web-artifacts` 可以独立使用，也可以截取前两者生成的网页和图表。

## 安装 Skills

将 Skill 目录复制或挂载到 Agent 的 Skills 目录，例如：

```bash
cp -R local-web-resources /opt/agent/skills/
cp -R render-web-artifacts /opt/agent/skills/
```

部署资源服务器后，修改 `local-web-resources/SKILL.md` 开头唯一的配置行：

```text
BASE_URL = https://web-resources.example/resources
```

将示例域名替换为 Agent 和生成页面实际可访问的 HTTP 或 HTTPS 地址。组件文档中的 `{BASE_URL}` 无需逐个修改。

## 部署资源服务器

将 `web-resources-server/` 作为静态目录交给 Nginx。至少应正确返回 CSS、JavaScript、JSON、字体和 SVG 的 MIME 类型，并让不存在的资源返回 404。

```nginx
location /resources/ {
    alias /srv/web-resources-server/;
    try_files $uri =404;

    add_header Access-Control-Allow-Origin "*" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Cache-Control "public, max-age=86400" always;
}
```

更完整的 Nginx 与 CORS 检查见 `local-web-resources/references/nginx.md`。

## 渲染网页产物

运行环境需要 Node.js、`playwright`、Chromium、`echarts` 和 Pandoc。详细参数见 `render-web-artifacts/SKILL.md`。

```bash
node render-web-artifacts/scripts/render.mjs html \
  --input dashboard.html --selector '#sales-chart' --output sales.png

node render-web-artifacts/scripts/render.mjs markdown \
  --input report.md --output report.pdf --paper A4
```

## 许可证

本仓库自行编写的 Skill、脚本、模板和文档采用 MIT License。`web-resources-server/libs/`、`web-resources-server/fonts/` 以及随 Skill 分发的第三方 bundle 不受本仓库 MIT License 重新授权，仍遵循各自上游许可证。详见 `THIRD_PARTY_NOTICES.md` 和资源目录中随附的许可证文件。

Handsontable、Intro.js、fullPage.js 和 TinyMCE 已保留用于兼容既有环境，但属于 `license-gated` 资源；使用或再分发前必须自行确认适用的开源或商业许可。

## 配套资源更新

当前配套资源为 90 个库、11 个字体家族，包含 Reveal.js / impress.js HTML 演示、数据分析、中文字体与图标。常用选型仅作参考，Agent 可根据任务自主组合已验证资源。

模板位于 `web-resources-server/templates/`，使用前将 `{BASE_URL}` 替换为实际资源地址。版本来源与验证结果见 [升级与核对报告](reports/升级与核对报告.md)，来源哈希由 `web-resources-server/resources.lock.json` 记录。

在仓库根目录执行：

```bash
python local-web-resources/scripts/validate_resources.py --node-check
python local-web-resources/scripts/validate_bundle.py
```

浏览器回归脚本为 `local-web-resources/scripts/browser_check.cjs`，维护环境需提供 Playwright 和 Chrome；静态资源部署不需要 npm 构建。
