#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
표창(thrown) 아이템 검색 결과에서 아이템 ID를 추출하고,
각 아이템 상세 페이지에서 드롭 몬스터 정보를 파싱하여 monster_item_relations.json에 추가합니다.

참고:
- 검색 URL: https://xn--o80b01o9mlw3kdzc.com/itemnote_search?searchInput=%ED%91%9C%EC%B0%BD
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
SCRAPED_DIR_DEFAULT = ROOT_DIR / "src" / "request" / "scraped_items"

SEARCH_URL_DEFAULT = "https://xn--o80b01o9mlw3kdzc.com/itemnote_search?searchInput=%ED%91%9C%EC%B0%BD"
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


def extract_item_ids_from_search(html_text: str) -> List[str]:
    """검색 결과 페이지에서 아이템 ID 추출"""
    # 패턴: item_detail/{id}
    ids = re.findall(r"item_detail/(\d+)", html_text)
    unique = sorted(set(ids), key=lambda x: sort_key_id(x))
    return unique


def parse_item_detail_html(html_text: str, item_id: str) -> List[Tuple[str, Optional[float]]]:
    """
    아이템 상세 페이지 HTML에서 드롭 몬스터 정보 추출
    
    Returns:
        List[Tuple[str, Optional[float]]]: (monsterId, dropRate) 리스트
    """
    drops: List[Tuple[str, Optional[float]]] = []
    
    # BY 섹션 찾기
    by_section_pattern = re.compile(
        r'<h2[^>]*>BY[^<]*</h2>[\s\S]*?(?=<h2[^>]*>|$)',
        re.IGNORECASE,
    )
    by_match = by_section_pattern.search(html_text)
    
    if not by_match:
        return drops
    
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
    
    return drops


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--search-url", default=SEARCH_URL_DEFAULT)
    parser.add_argument("--output-dir", default=str(SCRAPED_DIR_DEFAULT))
    parser.add_argument("--max-items", type=int, default=None)
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--skip-save-html", action="store_true")
    parser.add_argument("--item-ids", nargs="+", help="직접 아이템 ID 목록 제공 (검색 페이지 스킵)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 아이템 ID 목록 가져오기
    if args.item_ids:
        item_ids = args.item_ids
        print(f"Using provided item IDs: {len(item_ids)} items")
    else:
        print(f"Fetching search page: {args.search_url}")
        search_raw = fetch_bytes(args.search_url)
        search_html = choose_decode(search_raw)
        item_ids = extract_item_ids_from_search(search_html)
        print(f"Found {len(item_ids)} item IDs from search results")

    if args.max_items is not None:
        item_ids = item_ids[: args.max_items]

    if item_ids:
        print("Sample:", item_ids[:10])

    rel_file = DATA_DIR / "monster_item_relations.json"
    relations = load_json(rel_file, [])

    added_rel_total = 0
    updated_rel_total = 0

    for i, item_id in enumerate(item_ids, 1):
        url = DETAIL_URL_TEMPLATE.format(item_id=item_id)
        print(f"\n[{i}/{len(item_ids)}] Fetching {item_id}: {url}")
        raw = fetch_bytes(url)

        if not args.skip_save_html:
            out = output_dir / f"item_{item_id}.html"
            out.write_bytes(raw)
            print(f"  Saved HTML: {out}")

        html_text = choose_decode(raw)
        drops = parse_item_detail_html(html_text, item_id)

        relations, added_rel, updated_rel = merge_monster_item_relations(relations, item_id, drops)
        added_rel_total += added_rel
        updated_rel_total += updated_rel
        print(f"  Drops: {len(drops)} (added rel {added_rel}, updated rel {updated_rel})")

        time.sleep(args.delay)

    save_json(rel_file, relations)

    print("\n" + "=" * 60)
    print("Summary")
    print(f"  - Items processed: {len(item_ids)}")
    print(f"  - Relations: +{added_rel_total} / ~{updated_rel_total} (total {len(relations)})")
    print(f"  - monster_item_relations.json: {rel_file}")


if __name__ == "__main__":
    main()
