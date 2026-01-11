#!/usr/bin/env python3
"""
블록퍼스(3230302)의 드랍 테이블을 웹사이트 데이터로 업데이트
아이템 이름으로 매칭하여 업데이트
"""

import json
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리
ROOT_DIR = Path(__file__).parent.parent.parent
MONSTER_DATA_PATH = ROOT_DIR / 'src' / 'data' / 'monster_data.json'
ITEM_DATA_PATH = ROOT_DIR / 'src' / 'data' / 'item_data.json'
MONSTER_ITEM_RELATIONS_PATH = ROOT_DIR / 'src' / 'data' / 'monster_item_relations.json'

# 웹사이트에서 확인한 블록퍼스 드랍 아이템 목록 (이름 기준)
BLOCKPUS_DROP_ITEMS = [
    "문어 열쇠고리",
    "드라이버",
    "하얀 포션",
    "파란 포션",
    "활전용 화살",
    "석궁전용 화살",
    "오팔의 원석",
    "블록퍼스 오목알",
    "블록퍼스의 설계도",
    "금의 원석",
    "행운의 크리스탈 원석",
    "실버 배틀 그리브",
    "아다만티움 가즈",
    "블랙 매직슈즈",
    "레드 매티",
    "다크 레골러",
    "다크 레골러 바지",
    "퍼플 후르츠",
    "크레센트",
    "카키 쉐도우",
    "카키 쉐도우 바지",
    "실버 크로우",
    "망토 행운 주문서 10%",
]

def normalize_item_name(name: str) -> str:
    """아이템 이름 정규화"""
    normalized = name.strip()
    # 공백 정규화 (여러 공백을 하나로)
    normalized = ' '.join(normalized.split())
    return normalized

def remove_spaces(s: str) -> str:
    """공백 제거"""
    return ''.join(s.split())

def main():
    print("블록퍼스 드랍 테이블 업데이트 시작...")
    
    # 아이템 데이터 로드
    print("아이템 데이터 로드 중...")
    with open(ITEM_DATA_PATH, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    # 아이템 이름 -> ID 매핑 생성
    print("아이템 이름 매핑 생성 중...")
    item_name_to_ids = {}
    item_name_no_spaces_to_ids = {}
    
    for item in items:
        normalized_name = normalize_item_name(item.get('name', ''))
        name_no_spaces = remove_spaces(normalized_name)
        
        if normalized_name not in item_name_to_ids:
            item_name_to_ids[normalized_name] = []
        item_name_to_ids[normalized_name].append(item['id'])
        
        if name_no_spaces not in item_name_no_spaces_to_ids:
            item_name_no_spaces_to_ids[name_no_spaces] = []
        item_name_no_spaces_to_ids[name_no_spaces].append(item['id'])
    
    # 드랍 아이템 ID 찾기
    print("드랍 아이템 ID 찾기 중...")
    drop_item_ids = []
    not_found_items = []
    
    for item_name in BLOCKPUS_DROP_ITEMS:
        normalized_name = normalize_item_name(item_name)
        name_no_spaces = remove_spaces(normalized_name)
        
        found = False
        if normalized_name in item_name_to_ids:
            drop_item_ids.extend(item_name_to_ids[normalized_name])
            print(f"  찾음: '{item_name}' -> {item_name_to_ids[normalized_name]}")
            found = True
        elif name_no_spaces in item_name_no_spaces_to_ids:
            drop_item_ids.extend(item_name_no_spaces_to_ids[name_no_spaces])
            print(f"  찾음 (공백 무시): '{item_name}' -> {item_name_no_spaces_to_ids[name_no_spaces]}")
            found = True
        
        if not found:
            not_found_items.append(item_name)
            print(f"  경고: '{item_name}' 아이템을 찾을 수 없습니다.")
    
    if not_found_items:
        print(f"\n찾지 못한 아이템 ({len(not_found_items)}개):")
        for item in not_found_items:
            print(f"  - {item}")
    
    # 중복 제거
    drop_item_ids = list(set(drop_item_ids))
    print(f"\n총 {len(drop_item_ids)}개 아이템 ID 찾음")
    
    # 몬스터 데이터 로드
    print("\n몬스터 데이터 로드 중...")
    with open(MONSTER_DATA_PATH, 'r', encoding='utf-8') as f:
        monsters = json.load(f)
    
    # 블록퍼스 찾기
    blockpus = None
    for monster in monsters:
        if monster.get('name') == '블록퍼스':
            blockpus = monster
            break
    
    if not blockpus:
        print("오류: 블록퍼스 몬스터를 찾을 수 없습니다.")
        sys.exit(1)
    
    print(f"블록퍼스 찾음: ID {blockpus.get('id')}")
    
    # 드랍 아이템 업데이트
    blockpus['dropItemIds'] = drop_item_ids
    print(f"드랍 아이템 업데이트: {len(drop_item_ids)}개")
    
    # 몬스터-아이템 관계 데이터 로드
    print("\n몬스터-아이템 관계 데이터 로드 중...")
    with open(MONSTER_ITEM_RELATIONS_PATH, 'r', encoding='utf-8') as f:
        relations = json.load(f)
    
    # 기존 관계 제거 (블록퍼스의 모든 관계)
    blockpus_id = blockpus.get('id')
    relations = [r for r in relations if r.get('monsterId') != blockpus_id]
    print(f"기존 관계 제거 완료")
    
    # 새로운 관계 추가
    for item_id in drop_item_ids:
        relations.append({
            'monsterId': blockpus_id,
            'itemId': item_id
        })
    
    print(f"새로운 관계 추가: {len(drop_item_ids)}개")
    
    # 데이터 저장
    print("\n데이터 저장 중...")
    with open(MONSTER_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(monsters, f, ensure_ascii=False, indent=2)
    print(f"  몬스터 데이터 저장 완료: {MONSTER_DATA_PATH}")
    
    with open(MONSTER_ITEM_RELATIONS_PATH, 'w', encoding='utf-8') as f:
        json.dump(relations, f, ensure_ascii=False, indent=2)
    print(f"  관계 데이터 저장 완료: {MONSTER_ITEM_RELATIONS_PATH}")
    
    print("\n블록퍼스 드랍 테이블 업데이트 완료!")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"오류 발생: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
