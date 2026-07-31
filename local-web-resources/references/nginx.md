# Nginx 静态资源检查

资源服务器至少满足：

```nginx
location /public/resources/ {
    alias /srv/web-resources-server/;
    try_files $uri =404;

    add_header Access-Control-Allow-Origin "*" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Cache-Control "public, max-age=86400" always;
}

types {
    text/css css;
    application/javascript js mjs;
    application/json json;
    font/woff woff;
    font/woff2 woff2;
    font/ttf ttf;
    image/svg+xml svg;
}
```

如果站点与资源服务同源，可以收紧 `Access-Control-Allow-Origin`。跨域字体、地图 JSON 或模块脚本必须返回允许页面 origin 的 CORS 头。

部署后抽查：

- CSS 返回 `text/css`。
- JS/MJS 返回 JavaScript MIME。
- WOFF2 返回 `font/woff2`。
- JSON 返回 `application/json`。
- 不存在的文件返回 404，而不是 HTML 首页。
- `{BASE_URL}/fonts/fonts.css` 及其字体子请求均为 200。
