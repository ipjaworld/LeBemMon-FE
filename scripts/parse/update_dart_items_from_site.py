#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
표창(dart/shuriken) 아이템 HTML 파일에서 아이템 ID를 추출하고,
각 아이템 상세 페이지에서 정보를 크롤링하여 item_data.json과 monster_item_relations.json에 추가합니다.

참고:
- HTML 파일: src/request/dart.html
- 상세 예시: https://xn--o80b01o9mlw3kdzc.com/item_detail/2070000
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import ssl
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "src" / "data"
REQUEST_DIR = ROOT_DIR / "src" / "request"
SCRAPED_DIR_DEFAULT = ROOT_DIR / "src" / "request" / "scraped_items"

HTML_FILE_DEFAULT = REQUEST_DIR / "dart.html"
DETAIL_URL_TEMPLATE = "https://xn--o80b01o9mlw3kdzc.com/item_detail/{item_id}"


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


def load_json(path: Path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def sort_key_id(id_value: str):
    try:
        return (0, int(id_value))
    except Exception:
        return (1, id_value)


def extract_item_ids_from_html(html_text: str) -> List[str]:
    """HTML 파일에서 아이템 ID 추출"""
    # 패턴: item_detail/{id}
    ids = re.findall(r"item_detail/(\d+)", html_text)
    unique = sorted(set(ids), key=lambda x: sort_key_id(x))
    return unique


def parse_item_detail_html(html_text: str, item_id: str) -> Tuple[Dict, List[Tuple[str, Optional[float]]]]:
    """
    아이템 상세 페이지 HTML 파싱
    
    Returns:
        (item_data, drops): 아이템 데이터와 (monsterId, dropRate) 리스트
    """
    item = {
        "id": item_id,
        "majorCategory": "consumable",
        "mediumCategory": "shuriken",
        "isReleased": True,
    }
    
    # 아이템 이름 추출 (<h1> 또는 <h2> 태그)
    name_pattern = r'<h[12][^>]*>([^<]+)</h[12]>'
    name_match = re.search(name_pattern, html_text)
    if name_match:
        item["name"] = name_match.group(1).strip()
    else:
        # 대안: title 태그에서 추출
        title_pattern = r'<title>([^<]+)</title>'
        title_match = re.search(title_pattern, html_text)
        if title_match:
            title = title_match.group(1).strip()
            item["name"] = title.replace('메이플노트 클래식 - ', '').strip()
        else:
            item["name"] = f"Item {item_id}"
    
    # 이미지 URL 생성
    item["imageUrl"] = f"https://maplestory.io/api/gms/200/item/{item_id}/icon?resize=2"
    
    # DSC 섹션에서 설명과 공격력 추출
    # DSC 섹션 내의 <div class="req"><h3>...</h3></div> 구조에서 추출
    dsc_pattern = r'<h[23][^>]*>DSC</h[23]>[\s\S]*?<div class="req">[\s\S]*?<h3[^>]*>([^<]+)</h3>'
    dsc_match = re.search(dsc_pattern, html_text, re.IGNORECASE)
    if dsc_match:
        dsc_text = dsc_match.group(1).strip()
        
        # 공격력 추출: "공격력 + 15" 또는 "공격력 15" 패턴
        attack_pattern = r'공격력[+\s]*(\d+)'
        attack_match = re.search(attack_pattern, dsc_text)
        if attack_match:
            try:
                item["attackPower"] = int(attack_match.group(1))
            except Exception:
                pass
        
        # 설명 추출 (공격력 텍스트 제거)
        desc_text = re.sub(r'공격력[+\s]*\d+\s*', '', dsc_text)
        desc_text = desc_text.strip()
        if desc_text:
            item["description"] = desc_text
    
    # 드롭 정보 추출 (BY 섹션)
    drops: List[Tuple[str, Optional[float]]] = []
    
    by_section_pattern = re.compile(
        r'<h2[^>]*>BY[^<]*</h2>[\s\S]*?(?=<h2[^>]*>|$)',
        re.IGNORECASE,
    )
    by_match = by_section_pattern.search(html_text)
    
    if by_match:
        by_section = by_match.group(0)
        
        # BY 섹션 내에서 각 몬스터 블록 찾기
        # 패턴: <a href=".../monster_detail/{id}"> ... <div class="drop-rate-box">{rate}</div> ... </a>
        monster_block_pattern = re.compile(
            r'<a[^>]*href="[^"]*?/monster_detail/(\d+)"[^>]*>[\s\S]*?<div class="drop-rate-box">\s*([^<]+?)\s*</div>[\s\S]*?</a>',
            re.IGNORECASE,
        )
        
        for match in monster_block_pattern.finditer(by_section):
            monster_id = match.group(1)
            rate_text = match.group(2).strip()
            
            drop_rate: Optional[float] = None
            try:
                drop_rate = float(rate_text)
            except Exception:
                pass
            
            drops.append((monster_id, drop_rate))
    
    return item, drops


def merge_item_data(new_item: Dict, item_data: List[Dict]) -> Tuple[List[Dict], int, int]:
    """item_data.json에 아이템 추가/업데이트"""
    items_dict = {item["id"]: item for item in item_data}
    
    item_id = new_item["id"]
    if item_id in items_dict:
        # 기존 아이템 업데이트
        items_dict[item_id] = new_item
        merged_items = list(items_dict.values())
        merged_items.sort(key=lambda x: sort_key_id(x["id"]))
        return merged_items, 0, 1
    else:
        # 새로운 아이템 추가
        items_dict[item_id] = new_item
        merged_items = list(items_dict.values())
        merged_items.sort(key=lambda x: sort_key_id(x["id"]))
        return merged_items, 1, 0


def merge_monster_item_relations(
    existing: List[dict],
    item_id: str,
    drops: List[Tuple[str, Optional[float]]],
) -> Tuple[List[dict], int, int]:
    """monster_item_relations.json 병합"""
    by_key: Dict[Tuple[str, str], dict] = {(r["monsterId"], r["itemId"]): r for r in existing}
    added = 0
    updated = 0

    for monster_id, rate in drops:
        key = (monster_id, item_id)
        if key in by_key:
            if rate is not None:
                prev = by_key[key].get("dropRate")
                if prev != rate:
                    by_key[key]["dropRate"] = rate
                    updated += 1
        else:
            rel = {"monsterId": monster_id, "itemId": item_id}
            if rate is not None:
                rel["dropRate"] = rate
            by_key[key] = rel
            added += 1

    merged = list(by_key.values())
    merged.sort(key=lambda r: (sort_key_id(r["monsterId"]), sort_key_id(r["itemId"])))
    return merged, added, updated


def main():
    parser = argparse.ArgumentParser(description="표창 아이템 데이터 업데이트")
    parser.add_argument(
        "--html-file",
        type=str,
        default=str(HTML_FILE_DEFAULT),
        help="표창 아이템 목록 HTML 파일 경로",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(SCRAPED_DIR_DEFAULT),
        help="HTML 파일 저장 디렉토리",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=None,
        help="최대 처리할 아이템 수 (테스트용)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="각 페이지 사이 대기 시간 (초)",
    )
    parser.add_argument(
        "--skip-save-html",
        action="store_true",
        help="HTML 파일 저장 건너뛰기",
    )
    args = parser.parse_args()

    html_file = Path(args.html_file)
    if not html_file.exists():
        print(f"Error: HTML file not found: {html_file}")
        return

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # HTML 파일에서 아이템 ID 추출
    print(f"Reading HTML file: {html_file}")
    with open(html_file, "r", encoding="utf-8") as f:
        html_text = f.read()

    item_ids = extract_item_ids_from_html(html_text)
    print(f"Found {len(item_ids)} item IDs from HTML file")

    if args.max_items is not None:
        item_ids = item_ids[: args.max_items]

    if item_ids:
        print("Item IDs:", item_ids)

    # 데이터 파일 로드
    item_file = DATA_DIR / "item_data.json"
    rel_file = DATA_DIR / "monster_item_relations.json"
    
    items = load_json(item_file, [])
    relations = load_json(rel_file, [])

    added_items_total = 0
    updated_items_total = 0
    added_rel_total = 0
    updated_rel_total = 0

    for i, item_id in enumerate(item_ids, 1):
        url = DETAIL_URL_TEMPLATE.format(item_id=item_id)
        print(f"\n[{i}/{len(item_ids)}] Fetching {item_id}: {url}")
        
        try:
            raw = fetch_bytes(url)
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
            continue

        if not args.skip_save_html:
            out = output_dir / f"item_{item_id}.html"
            out.write_bytes(raw)
            print(f"  Saved HTML: {out}")

        html_text = choose_decode(raw)
        item_data, drops = parse_item_detail_html(html_text, item_id)

        # 아이템 데이터 병합
        items, added_item, updated_item = merge_item_data(item_data, items)
        added_items_total += added_item
        updated_items_total += updated_item
        print(f"  Item: {item_data.get('name', 'Unknown')} (added {added_item}, updated {updated_item})")
        
        # 공격력 정보 출력
        if "attackPower" in item_data:
            print(f"    Attack Power: {item_data['attackPower']}")

        # 드롭 정보 병합
        relations, added_rel, updated_rel = merge_monster_item_relations(relations, item_id, drops)
        added_rel_total += added_rel
        updated_rel_total += updated_rel
        print(f"  Drops: {len(drops)} (added rel {added_rel}, updated rel {updated_rel})")

        time.sleep(args.delay)

    # 결과 저장
    save_json(item_file, items)
    save_json(rel_file, relations)

    print("\n" + "=" * 60)
    print("Summary")
    print(f"  - Items processed: {len(item_ids)}")
    print(f"  - Items: +{added_items_total} / ~{updated_items_total} (total {len(items)})")
    print(f"  - Relations: +{added_rel_total} / ~{updated_rel_total} (total {len(relations)})")
    print(f"  - item_data.json: {item_file}")
    print(f"  - monster_item_relations.json: {rel_file}")


if __name__ == "__main__":
    main()
