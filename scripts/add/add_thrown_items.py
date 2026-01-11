#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
누락된 표창 아이템(2070005, 2070010)을 item_data.json에 추가합니다.
"""

from __future__ import annotations

import json
import re
import ssl
from pathlib import Path
from urllib.request import Request, urlopen

ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "src" / "data"
DETAIL_URL_TEMPLATE = "https://xn--o80b01o9mlw3kdzc.com/item_detail/{item_id}"

THROWN_ITEM_IDS = ["2070005", "2070010"]


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    req = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    )
    return urlopen(req, context=ssl.create_default_context(), timeout=timeout).read()


def choose_decode(raw: bytes) -> str:
    candidates = []
    for enc in ("utf-8", "cp949"):
        s = raw.decode(enc, "ignore")
        hangul = sum(1 for ch in s if "\uac00" <= ch <= "\ud7a3")
        candidates.append((hangul, enc, s))
    candidates.sort(reverse=True)
    return candidates[0][2]


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def sort_key_id(id_value: str):
    try:
        return (0, int(id_value))
    except Exception:
        return (1, id_value)


def parse_item_from_html(html_text: str, item_id: str) -> dict:
    """HTML에서 아이템 정보 파싱"""
    item = {"id": item_id}
    
    # 이름 추출
    name_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html_text)
    if name_match:
        item["name"] = name_match.group(1).strip()
    
    # 설명 추출 (DSC 섹션)
    desc_match = re.search(r'<h2[^>]*>DSC[^<]*</h2>\s*<h3[^>]*>([^<]+)</h3>', html_text)
    if desc_match:
        item["description"] = desc_match.group(1).strip()
    
    # 카테고리 정보
    item["majorCategory"] = "consumable"
    item["mediumCategory"] = "shuriken"  # 표창
    
    # 이미지 URL
    item["imageUrl"] = f"https://maplestory.io/api/gms/200/item/{item_id}/icon?resize=2"
    
    # 기본값
    item["isReleased"] = True
    
    return item


def main():
    item_file = DATA_DIR / "item_data.json"
    items = load_json(item_file)
    items_by_id = {item["id"]: item for item in items}
    
    added_count = 0
    updated_count = 0
    
    for item_id in THROWN_ITEM_IDS:
        url = DETAIL_URL_TEMPLATE.format(item_id=item_id)
        print(f"Fetching {item_id}: {url}")
        
        raw = fetch_bytes(url)
        html_text = choose_decode(raw)
        parsed_item = parse_item_from_html(html_text, item_id)
        
        if item_id in items_by_id:
            # 기존 아이템 업데이트 (카테고리만)
            items_by_id[item_id]["mediumCategory"] = "shuriken"
            updated_count += 1
            print(f"  Updated: {parsed_item.get('name', item_id)}")
        else:
            # 새 아이템 추가
            items.append(parsed_item)
            items_by_id[item_id] = parsed_item
            added_count += 1
            print(f"  Added: {parsed_item.get('name', item_id)}")
    
    # ID 정렬
    items.sort(key=lambda x: sort_key_id(x["id"]))
    
    save_json(item_file, items)
    
    print(f"\nSummary:")
    print(f"  - Items added: {added_count}")
    print(f"  - Items updated: {updated_count}")
    print(f"  - Total items: {len(items)}")


if __name__ == "__main__":
    main()
