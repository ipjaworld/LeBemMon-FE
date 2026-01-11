#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 파일에서 result-list-box 클래스의 아이템 데이터를 파싱하는 스크립트
"""
import re
import json
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리
ROOT_DIR = Path(__file__).parent.parent.parent


def parse_minor_category(name):
    """아이템 이름에서 minorCategory 추출"""
    if '귀환 주문서' in name:
        return None  # 귀환 주문서는 minorCategory 없음
    if '투구' in name:
        return 'hat'
    if '귀 장식' in name or '귀장식' in name:
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
    if '전신 갑옷' in name:
        return 'full-body'
    # 무기 주문서들은 minorCategory 없음
    return None


def parse_items_from_html(html_file_path):
    """HTML 파일에서 아이템 정보 추출"""
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_text = f.read()
    
    items = []
    
    # result-list-box 클래스 시작 위치 찾기
    result_list_start = html_text.find('<div class="result-list-box"')
    if result_list_start == -1:
        result_list_start = html_text.find('class="result-list-box"')
    
    if result_list_start != -1:
        # result-list-box 이후의 내용만 사용 (끝은 전체 HTML의 끝까지)
        content = html_text[result_list_start:]
    else:
        # 전체 HTML에서 추출
        content = html_text
    
    # 패턴: <a> 태그에서 href에 item_detail/{id}가 있고, 그 안에 <h3>{name}</h3>가 있는 패턴
    # 좀 더 정확한 패턴: <a ... href="...item_detail/{id}"> ... <h3>{name}</h3> ... </a>
    pattern = r'<a[^>]*href="[^"]*item_detail/(\d+)"[^>]*>.*?<h3>([^<]+)</h3>.*?</a>'
    
    matches = re.findall(pattern, content, re.DOTALL)
    
    for item_id, name in matches:
        name = name.strip()
        minor_category = parse_minor_category(name)
        
        item = {
            "id": item_id,
            "name": name,
            "imageUrl": f"https://maplestory.io/api/gms/200/item/{item_id}/icon?resize=2",
            "majorCategory": "consumable",
            "mediumCategory": "equip-scroll",
            "isReleased": True
        }
        
        if minor_category:
            item["minorCategory"] = minor_category
        
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
            # 기존 아이템 업데이트 (이름이 다른 경우)
            if items_dict[item_id]['name'] != new_item['name']:
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
    html_file = ROOT_DIR / 'src' / 'request' / 'scroll.html'
    output_file = ROOT_DIR / 'src' / 'data' / 'item_data.json'
    
    if not html_file.exists():
        print(f"Error: HTML file not found: {html_file}")
        sys.exit(1)
    
    print(f"Parsing HTML file: {html_file}")
    items = parse_items_from_html(html_file)
    print(f"Found {len(items)} items in HTML")
    
    if not items:
        print("No items found. Please check the HTML structure.")
        sys.exit(1)
    
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


if __name__ == "__main__":
    main()

