#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 테이블에서 장비 아이템 데이터를 파싱하는 스크립트
"""
import re
import json
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리
ROOT_DIR = Path(__file__).parent.parent.parent

# 장비 카테고리 매핑 (한글 -> 영문 mediumCategory)
EQUIPMENT_CATEGORY_MAP = {
    '모자(헬멧)': 'hat',
    '모자': 'hat',
    '헬멧': 'hat',
    '장갑': 'gloves',
    '신발': 'shoes',
    '전신': 'full-body',
    '상의': 'top',
    '하의': 'bottom',
    '방패': 'shield',
    '귀걸이': 'earring',
    '귀고리': 'earring',
    '망토': 'cape',
}

# 직업군 매핑 (한글 -> 영문 majorCategory)
# 현재는 전직업 공용만 처리
JOB_CATEGORY_MAP = {
    '전직업 공용': 'common',
    '전사': 'warrior',
    '마법사': 'mage',
    '궁수': 'archer',
    '도적': 'rogue',
    '해적': 'pirate',
}


def parse_equipment_table_html(html_text, job_category='common'):
    """HTML 테이블에서 장비 아이템 파싱"""
    items = []
    
    # HTML 주석 형식 지원:
    # 형식 1: <!-- ``` 카테고리명 --> ... <!-- ``` -->
    # 형식 2: <!-- 카테고리명 --> ... <!-- 카테고리명 끝 -->
    
    # 먼저 형식 1 시도 (``` 포함 형식)
    pattern_category_start_v1 = r'<!--\s*```\s*([^-]+?)\s*-->'
    pattern_category_end_v1 = r'<!--\s*```\s*-->'
    
    category_starts_v1 = list(re.finditer(pattern_category_start_v1, html_text))
    
    if category_starts_v1:
        # 형식 1 사용
        for i, match_start in enumerate(category_starts_v1):
            category_key = match_start.group(1).strip()
            
            if not category_key or category_key == '```':
                continue
            
            start_pos = match_start.end()
            if i + 1 < len(category_starts_v1):
                end_match = re.search(pattern_category_end_v1, html_text[start_pos:category_starts_v1[i+1].start()])
                if end_match:
                    end_pos = start_pos + end_match.start()
                else:
                    end_pos = category_starts_v1[i+1].start()
            else:
                end_match = re.search(pattern_category_end_v1, html_text[start_pos:])
                if end_match:
                    end_pos = start_pos + end_match.start()
                else:
                    end_pos = len(html_text)
            
            table_html = html_text[start_pos:end_pos]
            
            medium_category = EQUIPMENT_CATEGORY_MAP.get(category_key)
            if not medium_category:
                category_key_no_paren = re.sub(r'\([^)]*\)', '', category_key).strip()
                medium_category = EQUIPMENT_CATEGORY_MAP.get(category_key_no_paren)
            
            if not medium_category:
                print(f"Warning: Unknown category: {category_key}")
                continue
            
            # 테이블 행 파싱
            row_pattern = r'<tr>\s*<td>(\d*)</td>.*?item_detail/(\d+)".*?<td>([^<]+)</td>'
            rows = re.findall(row_pattern, table_html, re.DOTALL)
            
            for level_str, item_id, name in rows:
                level = int(level_str) if level_str.strip() else None
                name = name.strip()
                
                item = {
                    "id": item_id,
                    "name": name,
                    "imageUrl": f"https://maplestory.io/api/gms/200/item/{item_id}/icon?resize=2",
                    "majorCategory": job_category,
                    "mediumCategory": medium_category,
                    "isReleased": True
                }
                
                if level is not None:
                    item["reqLevel"] = level
                
                items.append(item)
    else:
        # 형식 2 사용: <!-- 카테고리명 --> ... <!-- 카테고리명 끝 -->
        pattern_category_start_v2 = r'<!--\s*([^-]+?)\s*-->'
        category_starts_v2 = list(re.finditer(pattern_category_start_v2, html_text))
        
        for i, match_start in enumerate(category_starts_v2):
            category_key = match_start.group(1).strip()
            
            # "끝"이 포함된 주석은 건너뛰기
            if not category_key or '끝' in category_key:
                continue
            
            # 카테고리명 끝 주석 패턴 찾기
            category_end_pattern = re.compile(re.escape(f'<!-- {category_key} 끝 -->'))
            
            start_pos = match_start.end()
            if i + 1 < len(category_starts_v2):
                # 다음 카테고리 시작 전까지
                end_match = category_end_pattern.search(html_text[start_pos:category_starts_v2[i+1].start()])
                if end_match:
                    end_pos = start_pos + end_match.start()
                else:
                    end_pos = category_starts_v2[i+1].start()
            else:
                # 마지막 카테고리인 경우
                end_match = category_end_pattern.search(html_text[start_pos:])
                if end_match:
                    end_pos = start_pos + end_match.start()
                else:
                    end_pos = len(html_text)
            
            table_html = html_text[start_pos:end_pos]
            
            medium_category = EQUIPMENT_CATEGORY_MAP.get(category_key)
            if not medium_category:
                category_key_no_paren = re.sub(r'\([^)]*\)', '', category_key).strip()
                medium_category = EQUIPMENT_CATEGORY_MAP.get(category_key_no_paren)
            
            if not medium_category:
                print(f"Warning: Unknown category: {category_key}")
                continue
            
            # 테이블 행 파싱
            row_pattern = r'<tr>\s*<td>(\d*)</td>.*?item_detail/(\d+)".*?<td>([^<]+)</td>'
            rows = re.findall(row_pattern, table_html, re.DOTALL)
            
            for level_str, item_id, name in rows:
                level = int(level_str) if level_str.strip() else None
                name = name.strip()
                
                item = {
                    "id": item_id,
                    "name": name,
                    "imageUrl": f"https://maplestory.io/api/gms/200/item/{item_id}/icon?resize=2",
                    "majorCategory": job_category,
                    "mediumCategory": medium_category,
                    "isReleased": True
                }
                
                if level is not None:
                    item["reqLevel"] = level
                
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
    
    # 직업군 (기본값: common)
    job_category = sys.argv[2] if len(sys.argv) > 2 else 'common'
    
    print(f"Parsing equipment items from HTML tables (job: {job_category})...")
    items = parse_equipment_table_html(html_text, job_category)
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
