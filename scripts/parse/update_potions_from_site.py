#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포션 아이템 목록 HTML 파일에서:
1. 각 포션 아이템의 상세 페이지 스크래핑
2. item_data.json에 포션 아이템 추가
3. monster_item_relations.json에 몬스터 드롭 관계 추가 (dropRate 없이)

참고 사이트:
- https://xn--o80b01o9mlw3kdzc.com/item_detail/{itemId}
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
SCRAPED_DIR_DEFAULT = REQUEST_DIR / "scraped_items"

DETAIL_URL_TEMPLATE = "https://xn--o80b01o9mlw3kdzc.com/item_detail/{item_id}"


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    return urlopen(req, context=ssl.create_default_context(), timeout=timeout).read()


def choose_decode(raw: bytes) -> str:
    """
    사이트가 UTF-8로 선언되어 있어도, 실제 바이트가 CP949 계열로 오는 경우가 있어
    (특히 윈도 환경) 한글 글자 수가 더 많은 디코딩 결과를 채택합니다.
    """
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


def extract_item_ids_from_html(html_file: Path) -> List[Tuple[str, str]]:
    """HTML 파일에서 아이템 ID와 이름 추출"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_text = f.read()
    
    items = []
    # 패턴: <a href="/item_detail/{id}"> ... <div>...{name}</div> ... </a>
    pattern = r'<a[^>]*href="[^"]*/item_detail/(\d+)"[^>]*>.*?<div[^>]*>([^<]+)</div>.*?</a>'
    matches = re.findall(pattern, html_text, re.DOTALL)
    
    for item_id, name in matches:
        # 이름에서 불필요한 텍스트 제거
        name = name.strip()
        if name and name != "이미지":
            items.append((item_id, name))
    
    return items


def parse_item_detail_html(html_text: str, item_id: str) -> Tuple[Dict, List[str]]:
    """
    아이템 상세 페이지 HTML 파싱
    Returns: (item_data, monster_names)
    """
    item = {
        "id": item_id,
        "majorCategory": "consumable",
        "mediumCategory": "etc",
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
    
    # 카테고리 정보 추출 (CATEGORY 섹션)
    category_pattern = r'중분류[:\s]+([^\n<]+)|소분류[:\s]+([^\n<]+)'
    category_matches = re.findall(category_pattern, html_text)
    for match in category_matches:
        if match[0]:  # 중분류
            medium_cat = match[0].strip()
            # mediumCategory 매핑
            if "Food" in medium_cat or "Drink" in medium_cat:
                item["mediumCategory"] = "etc"
            elif "Consumable" in medium_cat:
                item["mediumCategory"] = "etc"
    
    # 설명 추출 (DSC 섹션 다음의 텍스트)
    desc_pattern = r'<h[23][^>]*>DSC</h[23]>\s*<p[^>]*>([^<]+)</p>|<h[23][^>]*>DSC</h[23]>\s*([^<]+?)(?=<h[123]|<div|$)'
    desc_match = re.search(desc_pattern, html_text, re.DOTALL | re.IGNORECASE)
    if desc_match:
        description = desc_match.group(1) or desc_match.group(2)
        if description:
            description = description.strip()
            # HTML 태그 제거
            description = re.sub(r'<[^>]+>', '', description)
            if description:
                item["description"] = description
    
    # 몬스터 드롭 정보 추출 (BY 섹션)
    monster_names = []
    # BY 섹션 찾기: monster_detail 링크 내부의 h3 태그에서 몬스터 이름 추출
    # 가장 안전한 방법: monster_detail 링크 내부의 h3 태그만 찾기
    monster_box_pattern = r'<a[^>]*href="[^"]*monster_detail/\d+"[^>]*>.*?<h3[^>]*>([^<]+)</h3>'
    monster_names_matches = re.findall(monster_box_pattern, html_text, re.DOTALL | re.IGNORECASE)
    for name in monster_names_matches:
        monster_name = name.strip()
        if monster_name:
            monster_names.append(monster_name)
    
    # 중복 제거
    monster_names = list(dict.fromkeys(monster_names))  # 순서 유지하며 중복 제거
    
    return item, monster_names


def find_monster_id_by_name(monster_name: str, monster_data: List[Dict]) -> Optional[str]:
    """monster_data.json에서 몬스터 이름으로 ID 찾기"""
    for monster in monster_data:
        if monster.get("name") == monster_name:
            return monster["id"]
    return None


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
    item_id: str,
    monster_names: List[str],
    monster_data: List[Dict],
    relations: List[Dict],
) -> Tuple[List[Dict], int]:
    """monster_item_relations.json에 관계 추가"""
    # 기존 관계를 (monsterId, itemId) 쌍으로 관리
    relations_set = {(rel["monsterId"], rel["itemId"]) for rel in relations}
    
    added_count = 0
    for monster_name in monster_names:
        monster_id = find_monster_id_by_name(monster_name, monster_data)
        if monster_id and (monster_id, item_id) not in relations_set:
            relations.append({
                "monsterId": monster_id,
                "itemId": item_id,
                # dropRate는 이미지로 제공되어 추출 불가능하므로 추가하지 않음
            })
            relations_set.add((monster_id, item_id))
            added_count += 1
        elif not monster_id:
            print(f"  Warning: Monster '{monster_name}' not found in monster_data.json")
    
    # 정렬: (monsterId, itemId) 순서
    relations.sort(key=lambda x: (sort_key_id(x["monsterId"]), sort_key_id(x["itemId"])))
    
    return relations, added_count


def main():
    parser = argparse.ArgumentParser(description="포션 아이템 데이터 업데이트")
    parser.add_argument(
        "--html-file",
        type=str,
        default=str(REQUEST_DIR / "potion.html"),
        help="포션 아이템 목록 HTML 파일 경로",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(SCRAPED_DIR_DEFAULT),
        help="스크래핑한 HTML 저장 디렉토리",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=None,
        help="최대 처리할 아이템 수 (테스트용, 선택적)",
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
        help="HTML 저장 건너뛰기",
    )
    
    args = parser.parse_args()
    
    html_file = Path(args.html_file)
    output_dir = Path(args.output_dir)
    
    if not html_file.exists():
        print(f"Error: HTML file not found: {html_file}")
        return 1
    
    # 데이터 파일 경로
    item_data_file = DATA_DIR / "item_data.json"
    monster_data_file = DATA_DIR / "monster_data.json"
    relations_file = DATA_DIR / "monster_item_relations.json"
    
    # 기존 데이터 로드
    print("Loading existing data...")
    item_data = load_json(item_data_file, [])
    monster_data = load_json(monster_data_file, [])
    relations = load_json(relations_file, [])
    
    # HTML 파일에서 아이템 ID 추출
    print(f"Extracting item IDs from {html_file}...")
    items_to_process = extract_item_ids_from_html(html_file)
    print(f"Found {len(items_to_process)} items")
    
    if args.max_items:
        items_to_process = items_to_process[:args.max_items]
        print(f"Processing first {len(items_to_process)} items (--max-items={args.max_items})")
    
    # 통계
    total_items_added = 0
    total_items_updated = 0
    total_relations_added = 0
    items_failed = []
    
    # 각 아이템 처리
    for idx, (item_id, item_name) in enumerate(items_to_process, 1):
        print(f"\n[{idx}/{len(items_to_process)}] Processing item {item_id} ({item_name})...")
        
        try:
            # 상세 페이지 스크래핑
            detail_url = DETAIL_URL_TEMPLATE.format(item_id=item_id)
            print(f"  Fetching: {detail_url}")
            raw_html = fetch_bytes(detail_url)
            html_text = choose_decode(raw_html)
            
            # HTML 저장
            if not args.skip_save_html:
                html_file_path = output_dir / f"item_{item_id}.html"
                html_file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(html_file_path, "wb") as f:
                    f.write(raw_html)
            
            # HTML 파싱
            item, monster_names = parse_item_detail_html(html_text, item_id)
            print(f"  Parsed: {item.get('name', 'Unknown')}")
            print(f"  Monsters dropping this item: {len(monster_names)}")
            
            # item_data.json에 추가/업데이트
            item_data, added, updated = merge_item_data(item, item_data)
            if added:
                total_items_added += 1
                print(f"  [OK] Added to item_data.json")
            elif updated:
                total_items_updated += 1
                print(f"  [OK] Updated in item_data.json")
            
            # monster_item_relations.json에 관계 추가
            if monster_names:
                relations, rel_added = merge_monster_item_relations(
                    item_id, monster_names, monster_data, relations
                )
                total_relations_added += rel_added
                print(f"  [OK] Added {rel_added} monster-item relations")
            else:
                print(f"  [INFO] No monster drop information found")
            
            # 대기 (서버 부하 방지)
            if idx < len(items_to_process):
                time.sleep(args.delay)
                
        except Exception as e:
            print(f"  [ERROR] Error processing item {item_id}: {e}")
            items_failed.append((item_id, item_name, str(e)))
            continue
    
    # 결과 저장
    print("\n" + "=" * 60)
    print("Saving results...")
    save_json(item_data_file, item_data)
    save_json(relations_file, relations)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total items processed: {len(items_to_process)}")
    print(f"  - Items added: {total_items_added}")
    print(f"  - Items updated: {total_items_updated}")
    print(f"  - Monster-item relations added: {total_relations_added}")
    print(f"  - Items failed: {len(items_failed)}")
    
    if items_failed:
        print("\nFailed items:")
        for item_id, item_name, error in items_failed:
            print(f"  - {item_id} ({item_name}): {error}")
    
    print(f"\nOutput files:")
    print(f"  - {item_data_file}")
    print(f"  - {relations_file}")
    if not args.skip_save_html:
        print(f"  - HTML files: {output_dir}")
    
    return 0


if __name__ == "__main__":
    exit(main())
