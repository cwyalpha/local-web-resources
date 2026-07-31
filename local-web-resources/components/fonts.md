# 字体资源

**入口 CSS**（一行引入全部中英文字体）:
`{BASE_URL}/fonts/fonts.css`

| 字体 | CSS font-family | 说明 |
|------|----------------|------|
| inter | `'Inter'` | 英文 UI 无衬线字体 |
| roboto | `'Roboto'` | 英文通用无衬线字体 |
| jetbrains-mono | `'JetBrains Mono'` | 代码等宽字体 |
| noto-sans-sc | `'Noto Sans SC'` | 思源黑体（替代黑体/微软雅黑） |
| noto-serif-sc | `'Noto Serif SC'` | 思源宋体（替代宋体，公文用） |
| lxgw-wenkai | `'LXGW WenKai'` | 霞鹜文楷（替代楷体） |
| lxgw-wenkai-mono | `'LXGW WenKai Mono'` | 霞鹜文楷等宽（代码用） |

**推荐组合**:
```css
body { font-family: 'Noto Sans SC', 'Inter', sans-serif; }  /* 通用 */
body { font-family: 'Noto Serif SC', 'Georgia', serif; }    /* 公文 */
code { font-family: 'JetBrains Mono', monospace; }          /* 代码 */
```
