# 字体资源

**入口 CSS**（一行引入全部中英文字体）:
`{BASE_URL}/fonts/fonts.css`

| 字体 | CSS font-family | 说明 |
|------|----------------|------|
| inter | `'Inter'` | 英文 UI 无衬线字体 |
| roboto | `'Roboto'` | 英文通用无衬线字体 |
| jetbrains-mono | `'JetBrains Mono'` | 代码等宽字体 |
| noto-sans-sc | `'Noto Sans SC'` | 思源黑体（替代黑体/微软雅黑） |
| noto-serif-sc | `'Noto Serif SC'` | 思源宋体（宋体风格的正式报告和长篇正文） |
| lxgw-wenkai | `'LXGW WenKai'` | 霞鹜文楷（替代楷体） |
| lxgw-wenkai-mono | `'LXGW WenKai Mono'` | 霞鹜文楷等宽（代码用） |
| zhuque-fangsong | `'Zhuque Fangsong'` | 朱雀仿宋 v0.212 预览版（公文、正式报告仿宋正文） |
| merriweather | `'Merriweather'` | 英文正文衬线字体 |

**推荐组合**:
```css
body { font-family: 'Noto Sans SC', 'Inter', sans-serif; }                 /* 通用界面 */
body { font-family: 'Noto Serif SC', 'Merriweather', serif; }              /* 正式报告 */
.fangsong { font-family: 'Zhuque Fangsong', 'Noto Serif SC', serif; }      /* 仿宋正文 */
.literary { font-family: 'LXGW WenKai', 'Noto Serif SC', serif; }          /* 文艺/楷体 */
code { font-family: 'JetBrains Mono', 'LXGW WenKai Mono', monospace; }     /* 代码 */
```
