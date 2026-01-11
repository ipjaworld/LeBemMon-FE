#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 테이블에서 무기 아이템 데이터를 파싱하는 스크립트
"""
import re
import json
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리
ROOT_DIR = Path(__file__).parent.parent.parent

# 무기 카테고리 매핑
WEAPON_CATEGORY_MAP = {
    '한손검': 'one-handed-sword',
    '두손검': 'two-handed-sword',
    '한손도끼': 'one-handed-axe',
    '두손도끼': 'two-handed-axe',
    '한손둔기': 'one-handed-blunt',
    '두손둔기': 'two-handed-blunt',
    '창': 'spear',
    '폴암': 'polearm',
    '활': 'bow',
    '석궁': 'crossbow',
    '완드': 'wand',
    '스태프': 'staff',
    '단검': 'dagger',
    '아대': 'gauntlet',
    '너클': 'knuckle',
    '총': 'gun',
}


def parse_weapon_table_html(html_text):
    """HTML 테이블에서 무기 아이템 파싱"""
    items = []
    
    # 각 무기 카테고리별로 파싱
    # 형식 1: ``` 카테고리명으로 시작 (기존 형식)
    # 형식 2: <!-- 카테고리명 --> ... <!-- 카테고리명 끝 --> (HTML 주석 형식)
    
    # 먼저 코드 블록 형식 시도 (기존 형식)
    pattern_code_block = r'```\s*([^\n]+)\s*\n(.*?)```'
    matches_code_block = re.findall(pattern_code_block, html_text, re.DOTALL)
    
    if matches_code_block:
        # 코드 블록 형식
        for category_name, table_html in matches_code_block:
            category_key = category_name.strip()
            medium_category = WEAPON_CATEGORY_MAP.get(category_key)
            
            if not medium_category:
                print(f"Warning: Unknown category: {category_key}")
                continue
            
            # 테이블 행 파싱
            row_pattern = r'<tr>\s*<td>(\d+)</td>.*?item_detail/(\d+)".*?<td>([^<]+)</td>'
            rows = re.findall(row_pattern, table_html, re.DOTALL)
            
            for level, item_id, name in rows:
                level = int(level)
                name = name.strip()
                
                item = {
                    "id": item_id,
                    "name": name,
                    "imageUrl": f"https://maplestory.io/api/gms/200/item/{item_id}/icon?resize=2",
                    "majorCategory": "weapon",
                    "mediumCategory": medium_category,
                    "reqLevel": level,
                    "isReleased": True
                }
                
                items.append(item)
    else:
        # HTML 주석 형식
        # <!-- 카테고리명 --> ... <!-- 카테고리명 끝 --> 또는 <!--  --> (다음 카테고리 전까지)
        pattern_html_comment = r'<!--\s*([^-]+?)\s*-->\s*\n(.*?)(?=<!--\s*[^-]|\Z)'
        matches_html_comment = re.findall(pattern_html_comment, html_text, re.DOTALL)
        
        for category_name, table_html in matches_html_comment:
            category_key = category_name.strip()
            
            # 빈 주석이나 "끝" 포함된 주석은 건너뛰기
            if not category_key or '끝' in category_key:
                continue
            
            medium_category = WEAPON_CATEGORY_MAP.get(category_key)
            
            if not medium_category:
                print(f"Warning: Unknown category: {category_key}")
                continue
            
            # 테이블 행 파싱
            row_pattern = r'<tr>\s*<td>(\d+)</td>.*?item_detail/(\d+)".*?<td>([^<]+)</td>'
            rows = re.findall(row_pattern, table_html, re.DOTALL)
            
            for level, item_id, name in rows:
                level = int(level)
                name = name.strip()
                
                item = {
                    "id": item_id,
                    "name": name,
                    "imageUrl": f"https://maplestory.io/api/gms/200/item/{item_id}/icon?resize=2",
                    "majorCategory": "weapon",
                    "mediumCategory": medium_category,
                    "reqLevel": level,
                    "isReleased": True
                }
                
                items.append(item)
    
    return items


def merge_with_existing_data(new_items, existing_file_path):
    """기존 item_data.json과 병합"""
    # 기존 데이터 로드
    with open(existing_file_path, 'r', encoding='utf-8') as f:
        existing_items = json.load(f)
    
    # ID를 키로 하는 딕셔너리 생성 (중복 제거 및 업데이트)
    items_dict = {item['id']: item for item in existing_items}
    
    # 새로운 아이템 추가/업데이트
    updated_count = 0
    added_count = 0
    for new_item in new_items:
        item_id = new_item['id']
        if item_id in items_dict:
            # 기존 아이템 업데이트
            items_dict[item_id] = new_item
            updated_count += 1
        else:
            # 새로운 아이템 추가
            items_dict[item_id] = new_item
            added_count += 1
    
    # 리스트로 변환
    merged_items = list(items_dict.values())
    
    # ID로 정렬 (숫자 ID는 숫자로, 문자 ID는 문자열로 정렬)
    def sort_key(item):
        item_id = item['id']
        try:
            return (0, int(item_id))  # 숫자 ID는 (0, 숫자)
        except ValueError:
            return (1, item_id)  # 문자 ID는 (1, 문자열)
    
    merged_items.sort(key=sort_key)
    
    return merged_items, added_count, updated_count


def main():
    # 표준 입력에서 HTML 텍스트 읽기 (또는 파일 경로를 인자로 받기)
    if len(sys.argv) > 1:
        # 파일 경로가 제공된 경우
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            html_text = f.read()
    else:
        # 표준 입력에서 읽기
        html_text = sys.stdin.read()
    
    print("Parsing weapon items from HTML tables...")
    items = parse_weapon_table_html(html_text)
    print(f"Found {len(items)} items")
    
    if not items:
        print("No items found. Please check the HTML structure.")
        sys.exit(1)
    
    output_file = ROOT_DIR / 'src' / 'data' / 'item_data.json'
    
    # 기존 데이터와 병합
    print(f"Merging with existing data: {output_file}")
    merged_items, added_count, updated_count = merge_with_existing_data(items, output_file)
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_items, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults:")
    print(f"  - Total items: {len(merged_items)}")
    print(f"  - Added: {added_count}")
    print(f"  - Updated: {updated_count}")
    print(f"  - Output: {output_file}")
    
    # 카테고리별 통계
    by_category = {}
    for item in items:
        cat = item['mediumCategory']
        by_category[cat] = by_category.get(cat, 0) + 1
    
    print(f"\nItems by category:")
    for cat, count in sorted(by_category.items()):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()

