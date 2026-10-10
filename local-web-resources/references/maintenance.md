# 配套资源维护

Skill 与同级 `web-resources-server` 是一套。首次部署只改 SKILL.md 的 BASE_URL；Nginx 说明见 [nginx.md](nginx.md)。不要从组件文件名推断可用入口。

维护顺序：固定上游版本和依赖 → 校验下载内容 → 更新 `scripts/resource_metadata.json` → 重建组件文档与服务器清单 → 浏览器回归 → 更新锁文件。

```text
python scripts/build_component_index.py
python scripts/build_inventory.py
python scripts/validate_resources.py --node-check
python scripts/validate_bundle.py
```

命令从 Skill 目录执行；脚本根据自身位置定位同级服务器。`build_component_index.py` 保留原有参数，人工维护的 v5 版本/入口覆盖项在 `scripts/resource_metadata.json`，不要只改会被重建覆盖的组件文档。索引 schema_version 保持 2。

服务器 `resources.lock.json` 记录每个文件的 SHA-256、来源、版本和打包路径。它用于部署核对而不是自动联网更新。锁文件与内容不符时先调查差异，不通过重写锁文件掩盖失败。

维护者确认变更后，更新配套包的 `reports/file-sources.json`，再运行 `python scripts/build_lock.py` 重建锁文件。该步骤属于发布维护，普通页面生成不需要运行。

浏览器回归脚本为 `scripts/browser_check.cjs`，维护环境需安装 Playwright，并使用 `--browser` 指定本机 Chromium/Chrome 可执行文件；不会把 Node 或 Playwright 依赖放入部署资源目录。可用 `--filter` 仅复测受影响项，完整发布应保留总报告。

`copy_resources.py` / `copy_additional.py` 只从指定离线镜像的锁定版本复制，预检全部文件和校验值后才写入。找不到准确版本或附属资源时明确失败，不取“目录第一个版本”，不退化为只复制 `.min` 文件。

联网升级属于维护工作；运行生成的页面不需要公网。未纳入推荐入口的 ESM、开发文件或插件片段不保证可以作为独立经典脚本使用。

本地验证与真实内网 TLS、CORS、MIME 的部署验证分开记录，详见配套包 reports。需要回滚时重新部署保留的旧配套包。
