#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
귀고리 아이템 목록 페이지에서:
1. 귀고리 아이템 ID 목록 수집
2. 각 귀고리 아이템의 상세 페이지 스크래핑 (2초 이상 인터벌)
3. item_data.json에 귀고리 아이템 업데이트 (magicDefense, upgradeSlots, shopPrice, maxHP, maxMP)

참고 사이트:
- https://xn--o80b01o9mlw3kdzc.com/itemnote?category=공용&subCategory=0-Earrings
- https://xn--o80b01o9mlw3kdzc.com/item_detail/{itemId}
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "src" / "data"
REQUEST_DIR = ROOT_DIR / "src" / "request"
SCRAPED_DIR_DEFAULT = REQUEST_DIR / "scraped_earrings"

LIST_URL_DEFAULT = "https://xn--o80b01o9mlw3kdzc.com/itemnote?category=%EA%B3%B5%EC%9A%A9&subCategory=0-Earrings"
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


def extract_item_ids_from_list_html(html_text: str) -> List[Tuple[str, str]]:
    """
    목록 페이지 HTML에서 귀고리 아이템 ID와 이름 추출
    테이블 형식: <a href="...item_detail/{id}"> ... </a> 또는 <a href="...item_detail/{id}"> ... 이름 ... </a>
    """
    items = []
    seen_ids = set()
    
    # 패턴 1: 테이블 행에서 ID와 이름 추출 (같은 tr 내에서)
    # 예: <tr> ... <a href="...item_detail/1032006"> ... </a> ... <td>번개 귀고리</td> ... </tr>
    tr_pattern = r'<tr[^>]*>.*?</tr>'
    tr_matches = re.findall(tr_pattern, html_text, re.DOTALL | re.IGNORECASE)
    for tr_html in tr_matches:
        # tr 내에서 item_detail 링크 찾기
        id_match = re.search(r'href="[^"]*/item_detail/(\d+)"', tr_html, re.IGNORECASE)
        if id_match:
            item_id = id_match.group(1)
            # 같은 tr 내에서 이름 찾기 (td 태그 내 텍스트)
            name_matches = re.findall(r'<td[^>]*>([^<]+)</td>', tr_html, re.IGNORECASE)
            # 링크가 아닌 일반 텍스트 td를 이름으로 사용
            for name_candidate in name_matches:
                name_candidate = name_candidate.strip()
                if name_candidate and name_candidate != "이미지" and not name_candidate.startswith("http"):
                    if item_id not in seen_ids:
                        items.append((item_id, name_candidate))
                        seen_ids.add(item_id)
                    break
    
    # 패턴 2: 링크 내부에 이름이 있는 경우
    # 예: <a href="...item_detail/1032006"> 번개 귀고리 </a>
    if not items:
        pattern2 = r'<a[^>]*href="[^"]*/item_detail/(\d+)"[^>]*>.*?([^<\s]+[^<]*?)</a>'
        matches = re.findall(pattern2, html_text, re.DOTALL)
        for item_id, name in matches:
            item_id = item_id.strip()
            name = name.strip()
            # 이름에서 불필요한 텍스트 제거
            name = re.sub(r'\s+', ' ', name)
            if item_id and name and item_id not in seen_ids:
                if name != "이미지" and not name.startswith("http"):
                    items.append((item_id, name))
                    seen_ids.add(item_id)
    
    return items


def parse_earring_detail_html(html_text: str, item_id: str) -> Dict:
    """
    귀고리 상세 페이지 HTML 파싱
    EFFECT 섹션에서 다음 정보 추출:
    - magicDefense (마법방어력): + 10(8~12) 형식 -> 10 추출 (범위가 있으면 첫 번째 값 사용)
    - upgradeSlots (업그레이드 가능 횟수): 업그레이드 가능 횟수: 5
    - shopPrice (상점가): 20000메소 -> 20000 추출
    - maxHP (최대HP): 있을 경우
    - maxMP (최대MP): 있을 경우
    """
    item: Dict = {
        "id": item_id,
        "majorCategory": "common",
        "mediumCategory": "earring",
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
    
    # REQ 섹션에서 요구 레벨 추출
    req_level_pattern = r'REQ LEV[:\s]*(\d+)'
    req_level_match = re.search(req_level_pattern, html_text, re.IGNORECASE)
    if req_level_match:
        item["reqLevel"] = int(req_level_match.group(1))
    
    # EFFECT 섹션 찾기
    effect_section_pattern = r'<h[23][^>]*>EFFECT</h[23]>(.*?)(?=<h[123]|<div|$)'
    effect_match = re.search(effect_section_pattern, html_text, re.DOTALL | re.IGNORECASE)
    
    if effect_match:
        effect_text = effect_match.group(1)
        
        # 마법방어력 추출: "마법방어력 : + 10(8~12)" 또는 "마법방어력 : + 10" 형식
        magic_def_pattern = r'마법방어력[:\s]*\+?\s*(\d+)(?:\([^)]+\))?'
        magic_def_match = re.search(magic_def_pattern, effect_text, re.IGNORECASE)
        if magic_def_match:
            item["magicDefense"] = int(magic_def_match.group(1))
        
        # 업그레이드 가능 횟수 추출: "업그레이드 가능 횟수: 5"
        upgrade_pattern = r'업그레이드\s*가능\s*횟수[:\s]*(\d+)'
        upgrade_match = re.search(upgrade_pattern, effect_text, re.IGNORECASE)
        if upgrade_match:
            item["upgradeSlots"] = int(upgrade_match.group(1))
        
        # 상점가 추출: "상점가: 20000메소" 또는 "상점가: 20,000메소"
        shop_price_pattern = r'상점가[:\s]*([\d,]+)\s*메소'
        shop_price_match = re.search(shop_price_pattern, effect_text, re.IGNORECASE)
        if shop_price_match:
            price_str = shop_price_match.group(1).replace(',', '')
            item["shopPrice"] = int(price_str)
        
        # 최대HP 추출: "최대HP" 또는 "HP" + 숫자
        max_hp_pattern = r'(?:최대\s*)?HP[:\s]*\+?\s*(\d+)'
        max_hp_match = re.search(max_hp_pattern, effect_text, re.IGNORECASE)
        if max_hp_match:
            item["maxHP"] = int(max_hp_match.group(1))
        
        # 최대MP 추출: "최대MP" 또는 "MP" + 숫자
        max_mp_pattern = r'(?:최대\s*)?MP[:\s]*\+?\s*(\d+)'
        max_mp_match = re.search(max_mp_pattern, effect_text, re.IGNORECASE)
        if max_mp_match:
            item["maxMP"] = int(max_mp_match.group(1))
    
    # EFFECT 섹션에서 찾지 못한 경우 전체 HTML에서 검색 (maxHP, maxMP만)
    if "maxHP" not in item:
        max_hp_pattern = r'(?:최대\s*)?HP[:\s]*\+?\s*(\d+)'
        max_hp_match = re.search(max_hp_pattern, html_text, re.IGNORECASE)
        if max_hp_match:
            item["maxHP"] = int(max_hp_match.group(1))
    
    if "maxMP" not in item:
        max_mp_pattern = r'(?:최대\s*)?MP[:\s]*\+?\s*(\d+)'
        max_mp_match = re.search(max_mp_pattern, html_text, re.IGNORECASE)
        if max_mp_match:
            item["maxMP"] = int(max_mp_match.group(1))
    
    return item


def merge_item_data(updated_item: Dict, item_data: List[Dict]) -> Tuple[List[Dict], int, int]:
    """
    item_data.json에 아이템 업데이트
    기존 아이템이 있으면 업데이트, 없으면 추가
    """
    items_dict = {item["id"]: item for item in item_data}
    
    item_id = updated_item["id"]
    if item_id in items_dict:
        # 기존 아이템 업데이트 (새로운 필드만 업데이트, 기존 필드는 유지)
        existing_item = items_dict[item_id]
        for key, value in updated_item.items():
            if value is not None:
                existing_item[key] = value
        items_dict[item_id] = existing_item
        merged_items = list(items_dict.values())
        merged_items.sort(key=lambda x: sort_key_id(x["id"]))
        return merged_items, 0, 1
    else:
        # 새로운 아이템 추가
        items_dict[item_id] = updated_item
        merged_items = list(items_dict.values())
        merged_items.sort(key=lambda x: sort_key_id(x["id"]))
        return merged_items, 1, 0


def main():
    parser = argparse.ArgumentParser(description="귀고리 아이템 데이터 업데이트")
    parser.add_argument(
        "--list-url",
        type=str,
        default=LIST_URL_DEFAULT,
        help="귀고리 목록 페이지 URL",
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
        help="각 페이지 사이 대기 시간 (초, 기본값: 2.0)",
    )
    parser.add_argument(
        "--skip-save-html",
        action="store_true",
        help="HTML 저장 건너뛰기",
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    
    # 데이터 파일 경로
    item_data_file = DATA_DIR / "item_data.json"
    
    # 기존 데이터 로드
    print("Loading existing data...")
    item_data = load_json(item_data_file, [])
    
    # 목록 페이지에서 아이템 ID 추출
    print(f"Fetching list page: {args.list_url}")
    try:
        raw_html = fetch_bytes(args.list_url)
        list_html = choose_decode(raw_html)
        
        # 목록 HTML 저장 (디버깅용)
        if not args.skip_save_html:
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(output_dir / "earrings_list.html", "wb") as f:
                f.write(raw_html)
        
        items_to_process = extract_item_ids_from_list_html(list_html)
        print(f"Found {len(items_to_process)} earring items")
        
        if not items_to_process:
            print("Error: No items found in list page")
            return 1
        
    except Exception as e:
        print(f"Error fetching list page: {e}")
        return 1
    
    if args.max_items:
        items_to_process = items_to_process[:args.max_items]
        print(f"Processing first {len(items_to_process)} items (--max-items={args.max_items})")
    
    # 통계
    total_items_added = 0
    total_items_updated = 0
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
                html_file_path = output_dir / f"earring_{item_id}.html"
                html_file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(html_file_path, "wb") as f:
                    f.write(raw_html)
            
            # HTML 파싱
            item = parse_earring_detail_html(html_text, item_id)
            print(f"  Parsed: {item.get('name', 'Unknown')}")
            
            # 파싱된 필드 출력
            if "magicDefense" in item:
                print(f"    magicDefense: {item['magicDefense']}")
            if "upgradeSlots" in item:
                print(f"    upgradeSlots: {item['upgradeSlots']}")
            if "shopPrice" in item:
                print(f"    shopPrice: {item['shopPrice']}")
            if "maxHP" in item:
                print(f"    maxHP: {item['maxHP']}")
            if "maxMP" in item:
                print(f"    maxMP: {item['maxMP']}")
            
            # item_data.json에 추가/업데이트
            item_data, added, updated = merge_item_data(item, item_data)
            if added:
                total_items_added += 1
                print(f"  [OK] Added to item_data.json")
            elif updated:
                total_items_updated += 1
                print(f"  [OK] Updated in item_data.json")
            
            # 대기 (서버 부하 방지)
            if idx < len(items_to_process):
                time.sleep(args.delay)
                
        except Exception as e:
            print(f"  [ERROR] Error processing item {item_id}: {e}")
            import traceback
            traceback.print_exc()
            items_failed.append((item_id, item_name, str(e)))
            continue
    
    # 결과 저장
    print("\n" + "=" * 60)
    print("Saving results...")
    save_json(item_data_file, item_data)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total items processed: {len(items_to_process)}")
    print(f"  - Items added: {total_items_added}")
    print(f"  - Items updated: {total_items_updated}")
    print(f"  - Items failed: {len(items_failed)}")
    
    if items_failed:
        print("\nFailed items:")
        for item_id, item_name, error in items_failed:
            print(f"  - {item_id} ({item_name}): {error}")
    
    print(f"\nOutput file: {item_data_file}")
    if not args.skip_save_html:
        print(f"HTML files: {output_dir}")
    
    return 0


if __name__ == "__main__":
    exit(main())
