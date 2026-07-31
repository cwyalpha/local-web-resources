# Third-Party Notices

This repository redistributes browser libraries and fonts for offline and
intranet use. The root MIT License applies only to the original Skills,
scripts, templates, and documentation authored for this repository. It does
not replace or supersede any third-party license.

## Bundled resources

- `web-resources-server/libs/` contains third-party JavaScript, CSS, images,
  workers, and webfonts. Copyright and license terms belong to their respective
  upstream projects. License files retained in individual library directories
  take precedence.
- `web-resources-server/fonts/` contains Inter, Roboto, Merriweather,
  JetBrains Mono, Noto Sans SC, Noto Serif SC, LXGW WenKai, and Zhuque
  Fangsong font assets. These remain under their upstream font licenses,
  including the SIL Open Font License where applicable.
- `render-web-artifacts/assets/mermaid.min.js` is Mermaid and remains under
  the MIT License included in `render-web-artifacts/assets/mermaid.LICENSE`.

The machine-readable and human-readable resource catalogs are available in
`web-resources-server/inventory.json` and
`local-web-resources/components/catalog.md`.

## License-gated resources

The following resources are retained for compatibility and are never selected
by default by the Skill:

| Resource | Version | License note |
|---|---:|---|
| Handsontable | 16.1.1 | Commercial use requires confirming the applicable Handsontable license. |
| Intro.js | 8.3.2 | AGPL or commercial license. |
| fullPage.js | 4.0.37 | GPLv3 or commercial license. |
| TinyMCE | 8.1.2 | GPLv2-or-later or commercial license. |

Downstream users are responsible for confirming that their use, modification,
deployment, and redistribution comply with the applicable upstream terms.
