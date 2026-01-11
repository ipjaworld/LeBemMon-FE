#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
아이템 상세 페이지 HTML에서 데이터를 파싱하는 스크립트
"""
import re
import json
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리
ROOT_DIR = Path(__file__).parent.parent.parent


def parse_minor_category(name, medium_category):
    """아이템 이름에서 minorCategory 추출"""
    if medium_category != "equip-scroll":
        return None
    
    if '귀환 주문서' in name:
        return None  # 귀환 주문서는 minorCategory 없음
    if '투구' in name:
        return 'hat'
    if '귀 장식' in name or '귀장식' in name or '귀걸이' in name:
        return 'earring'
    if '상의' in name:
        return 'top'
    if '하의' in name:
        return 'bottom'
    if '신발' in name:
        return 'shoes'
    if '장갑' in name:
        return 'gloves'
    if '방패' in name:
        return 'shield'
    if '망토' in name:
        return 'cape'
    if '전신' in name:
        return 'full-body'
    return None


def parse_category_from_html(html_text):
    """HTML에서 카테고리 정보 추출"""
    # 카테고리 정보 찾기 (CATEGORY 섹션)
    category_pattern = r'대분류[:\s]+([^\n<]+)|중분류[:\s]+([^\n<]+)|소분류[:\s]+([^\n<]+)'
    matches = re.findall(category_pattern, html_text)
    
    major_category = None
    medium_category = None
    minor_category_text = None
    
    for match in matches:
        if match[0]:  # 대분류
            major_category = match[0].strip()
        if match[1]:  # 중분류
            medium_category = match[1].strip()
        if match[2]:  # 소분류
            minor_category_text = match[2].strip()
    
    # 한글 카테고리를 영문으로 변환
    major_category_map = {
        '소비': 'consumable',
        '무기': 'weapon',
        '장비': 'common',  # 기본값, 직업군에 따라 다를 수 있음
    }
    
    medium_category_map = {
        'Armor Scroll': 'equip-scroll',
        'Weapon Scroll': 'equip-scroll',
        'Accessory Scroll': 'equip-scroll',
        'equip-scroll': 'equip-scroll',
    }
    
    major_cat = major_category_map.get(major_category, 'consumable') if major_category else 'consumable'
    medium_cat = medium_category_map.get(medium_category, 'equip-scroll') if medium_category else 'equip-scroll'
    
    return major_cat, medium_cat, minor_category_text


def parse_item_detail_from_html(html_text, item_id=None):
    """상세 페이지 HTML에서 아이템 정보 추출"""
    item = {}
    
    # 아이템 ID 추출 (URL에서)
    if item_id:
        item['id'] = item_id
    else:
        id_pattern = r'item_detail/(\d+)'
        id_match = re.search(id_pattern, html_text)
        if id_match:
            item['id'] = id_match.group(1)
        else:
            return None
    
    # 아이템 이름 추출 (<h1> 또는 <h2> 태그에서)
    name_pattern = r'<h[12][^>]*>([^<]+)</h[12]>'
    name_match = re.search(name_pattern, html_text)
    if name_match:
        item['name'] = name_match.group(1).strip()
    else:
        # 대안: <title> 태그에서 추출
        title_pattern = r'<title>([^<]+)</title>'
        title_match = re.search(title_pattern, html_text)
        if title_match:
            title = title_match.group(1).strip()
            # "메이플노트 클래식 - " 제거
            item['name'] = title.replace('메이플노트 클래식 - ', '').strip()
    
    if 'name' not in item:
        return None
    
    # 이미지 URL 생성
    item['imageUrl'] = f"https://maplestory.io/api/gms/200/item/{item['id']}/icon?resize=2"
    
    # 카테고리 정보 추출
    major_cat, medium_cat, minor_category_text = parse_category_from_html(html_text)
    item['majorCategory'] = major_cat
    item['mediumCategory'] = medium_cat
    
    # minorCategory 추출 (이름 기반)
    minor_cat = parse_minor_category(item['name'], medium_cat)
    if minor_cat:
        item['minorCategory'] = minor_cat
    
    # 설명 추출 (선택적)
    desc_pattern = r'<div[^>]*class="[^"]*description[^"]*"[^>]*>.*?([^<]+)</div>'
    desc_match = re.search(desc_pattern, html_text, re.DOTALL)
    if desc_match:
        description = desc_match.group(1).strip()
        # #c 태그 제거
        description = re.sub(r'#c([^#]+)#', r'\1', description)
        item['description'] = description
    
    # 기본값 설정
    item['isReleased'] = True
    
    return item


def merge_with_existing_data(new_item, existing_file_path):
    """기존 item_data.json과 병합"""
    # 기존 데이터 로드
    with open(existing_file_path, 'r', encoding='utf-8') as f:
        existing_items = json.load(f)
    
    # ID를 키로 하는 딕셔너리 생성
    items_dict = {item['id']: item for item in existing_items}
    
    # 새로운 아이템 추가/업데이트
    item_id = new_item['id']
    if item_id in items_dict:
        # 기존 아이템 업데이트
        items_dict[item_id] = new_item
        return list(items_dict.values()), 0, 1
    else:
        # 새로운 아이템 추가
        items_dict[item_id] = new_item
        merged_items = list(items_dict.values())
        
        # ID로 정렬
        def sort_key(item):
            item_id = item['id']
            try:
                return (0, int(item_id))
            except ValueError:
                return (1, item_id)
        
        merged_items.sort(key=sort_key)
        return merged_items, 1, 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_item_detail.py <html_file_path> [item_id]")
        sys.exit(1)
    
    html_file = Path(sys.argv[1])
    item_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not html_file.exists():
        print(f"Error: HTML file not found: {html_file}")
        sys.exit(1)
    
    output_file = ROOT_DIR / 'src' / 'data' / 'item_data.json'
    
    print(f"Parsing HTML file: {html_file}")
    with open(html_file, 'r', encoding='utf-8') as f:
        html_text = f.read()
    
    item = parse_item_detail_from_html(html_text, item_id)
    
    if not item:
        print("Error: Failed to parse item data from HTML")
        sys.exit(1)
    
    print(f"Parsed item: {item['name']} (ID: {item['id']})")
    
    # 기존 데이터와 병합
    print(f"Merging with existing data: {output_file}")
    merged_items, added_count, updated_count = merge_with_existing_data(item, output_file)
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_items, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults:")
    print(f"  - Total items: {len(merged_items)}")
    print(f"  - Added: {added_count}")
    print(f"  - Updated: {updated_count}")
    print(f"  - Output: {output_file}")


if __name__ == "__main__":
    main()
