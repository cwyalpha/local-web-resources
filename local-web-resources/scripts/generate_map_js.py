#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate china.js and province JS files for ECharts map registration."""

import argparse
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MAP_DIR = SCRIPT_DIR.parent.parent / "web-resources-server" / "libs" / "charts" / "echarts" / "map"

# Province name mapping (pinyin -> Chinese)
PROVINCE_NAMES = {
    "beijing": "北京", "tianjin": "天津", "hebei": "河北",
    "shanxi": "山西", "neimenggu": "内蒙古", "liaoning": "辽宁",
    "jilin": "吉林", "heilongjiang": "黑龙江", "shanghai": "上海",
    "jiangsu": "江苏", "zhejiang": "浙江", "anhui": "安徽",
    "fujian": "福建", "jiangxi": "江西", "shandong": "山东",
    "henan": "河南", "hubei": "湖北", "hunan": "湖南",
    "guangdong": "广东", "guangxi": "广西", "hainan": "海南",
    "chongqing": "重庆", "sichuan": "四川", "guizhou": "贵州",
    "yunnan": "云南", "xizang": "西藏", "shaanxi": "陕西",
    "gansu": "甘肃", "qinghai": "青海", "ningxia": "宁夏",
    "xinjiang": "新疆", "xianggang": "香港", "aomen": "澳门",
}


def create_register_js(map_name, geojson_path, output_path):
    """Create a JS file that auto-registers GeoJSON with ECharts."""
    data = geojson_path.read_text(encoding="utf-8").strip()

    js = (
        f'// ECharts map: {map_name}\n'
        f'// Auto-registers when loaded after echarts.min.js\n'
        f'(function(){{\n'
        f'  var d = {data};\n'
        f'  if(typeof echarts!=="undefined")echarts.registerMap("{map_name}",d);\n'
        f'}})();\n'
    )

    output_path.write_text(js, encoding="utf-8")
    return output_path.stat().st_size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map-dir", type=Path, default=DEFAULT_MAP_DIR)
    args = parser.parse_args()
    map_dir = args.map_dir.expanduser().resolve()
    json_dir = map_dir / "json"
    if not json_dir.is_dir():
        raise SystemExit(f"Map JSON directory not found: {json_dir}")

    # 1. Generate china.js
    china_json = json_dir / "china.json"
    china_js = map_dir / "china.js"
    size = create_register_js("china", china_json, china_js)
    print(f"[OK] china.js ({size // 1024} KB)")

    # 2. Generate province JS files in province/ directory
    province_dir = map_dir / "province"
    province_dir.mkdir(exist_ok=True)

    count = 0
    for json_file in sorted(json_dir.glob("*.json")):
        name = json_file.stem
        if name in ("china", "china-outline"):
            continue

        cn_name = PROVINCE_NAMES.get(name, name)
        output = province_dir / f"{name}.js"
        size = create_register_js(cn_name, json_file, output)
        count += 1

    print(f"[OK] {count} province JS files in map/province/")

    # 3. Create provinces index
    index = {}
    for name, cn in sorted(PROVINCE_NAMES.items()):
        json_path = json_dir / f"{name}.json"
        if json_path.exists():
            index[cn] = {
                "pinyin": name,
                "js": f"province/{name}.js",
                "json": f"json/{name}.json",
            }

    (map_dir / "provinces-index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"[OK] provinces-index.json ({len(index)} provinces)")

    # Summary
    total_size = sum(f.stat().st_size for f in map_dir.rglob("*") if f.is_file())
    print(f"\nTotal map data: {total_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
