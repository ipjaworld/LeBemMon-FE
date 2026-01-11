#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
파싱 결과를 확인하는 스크립트
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from parse_item_detail import parse_item_detail_from_html

# 샘플 HTML 파일 확인
sample_files = [
    'src/request/scraped/item_2040000.html',
    'src/request/scraped/item_2040001.html',
    'src/request/scraped/item_2040002.html',
]

print("Checking parsing results...")
for html_file in sample_files:
    html_path = Path(__file__).parent.parent.parent / html_file
    if html_path.exists():
        item_id = html_path.stem.replace('item_', '')
        with open(html_path, 'r', encoding='utf-8') as f:
            html_text = f.read()
        
        item = parse_item_detail_from_html(html_text, item_id)
        if item:
            print(f"\n{item_id}:")
            print(f"  Name: {item.get('name', 'N/A')}")
            print(f"  Major: {item.get('majorCategory', 'N/A')}")
            print(f"  Medium: {item.get('mediumCategory', 'N/A')}")
            print(f"  Minor: {item.get('minorCategory', 'N/A')}")
        else:
            print(f"\n{item_id}: Failed to parse")

# JSON 파일 확인
json_file = Path(__file__).parent.parent.parent / 'src' / 'data' / 'item_data.json'
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

scrolls = [item for item in data if item.get('majorCategory') == 'consumable' and item.get('mediumCategory') == 'equip-scroll']
print(f"\n\nTotal scroll items in JSON: {len(scrolls)}")

broken = [item for item in scrolls if 'Ŭ' in item.get('name', '') or 'ĸ' in item.get('name', '')]
print(f"Items with broken names: {len(broken)}")

if broken:
    print("\nSample broken items:")
    for item in broken[:5]:
        print(f"  {item['id']}: {item.get('name', 'N/A')[:50]}")
