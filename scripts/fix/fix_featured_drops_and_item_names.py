#!/usr/bin/env python3
"""
주요 드랍 필드 초기화 및 재설정 + 아이템 이름 통일 스크립트

1. 모든 몬스터의 featuredDropItemIds 초기화
2. 아이템 이름 통일 (전신 갑옷, 신발 점프력 주문서)
3. 제공된 리스트 기준으로 주요 드랍 재설정
"""

import json
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리
ROOT_DIR = Path(__file__).parent.parent.parent
MONSTER_DATA_PATH = ROOT_DIR / 'src' / 'data' / 'monster_data.json'
ITEM_DATA_PATH = ROOT_DIR / 'src' / 'data' / 'item_data.json'
MONSTER_ITEM_RELATIONS_PATH = ROOT_DIR / 'src' / 'data' / 'monster_item_relations.json'

# 주요 드랍 아이템 목록 (사용자 제공)
FEATURED_DROP_ITEM_NAMES = [
    "일비표창",
    "뇌전수리검",
    "화비표창",
    "투구 민첩 주문서 60%",
    "투구 민첩 주문서 100%",
    "투구 민첩 주문서 10%",
    "투구 지력 주문서 100%",
    "투구 지력 주문서 60%",
    "투구 지력 주문서 10%",
    "귀장식 민첩 주문서 60%",
    "귀장식 민첩 주문서 10%",
    "귀장식 행운 주문서 60%",
    "귀장식 행운 주문서 10%",
    "귀장식 지력 주문서 60%",
    "귀장식 지력 주문서 10%",
    "전신 갑옷 지력 주문서 60%",
    "전신 갑옷 행운 주문서 100%",
    "전신 갑옷 행운 주문서 60%",
    "전신 갑옷 행운 주문서 10%",
    "전신 갑옷 지력 주문서 10%",
    "전신 갑옷 민첩 주문서 60%",
    "전신 갑옷 민첩 주문서 10%",
    "레드 크리븐",
    "캐스터스",
    "블러드 대거",
    "블루마린",
    "케이그",
    "레이든 스태프",
    "이블윙즈",
    "다이몬의 완드",
    "마기코라스",
    "피닉스완드",
    "화이트 네쉐르",
    "골든 네쉐르",
    "화이트 니스록",
    "골든 니스록",
    "다크 니스록",
    "제드버그",
    "피나카",
    "라 투핸더",
    "프라우테",
    "스파타",
    "다크 파쵸네",
    "다크 와이즈",
    "다크 로린",
    "다크 마누트",
    "에스터 실드",
    "장갑 공격력 주문서 60%",
    "장갑 공격력 주문서 10%",
    "퍼플 후르츠",
    "블루 후르츠",
    "레드 후르츠",
    "다크 후르츠",
    "신발 점프력 주문서 10%",
    "주르건 리스트",
    "한손검 공격력 주문서 10%",
    "단검 공격력 주문서 10%",
    "완드 마력 주문서 10%",
    "스태프 마력 주문서 10%",
    "두손검 공격력 주문서 10%",
    "창 공격력 주문서 10%",
    "활 공격력 주문서 10%",
    "석궁 공격력 주문서 10%",
    "아대 공격력 주문서 10%",
    "아대 공격력 주문서 60%",
    "망토 힘 주문서 60%",
    "망토 민첩 주문서 60%",
    "망토 지력 주문서 60%",
    "망토 행운 주문서 60%",
    "신문지 투구",
    "냄비뚜껑",
    "장미꽃 귀고리",
]

# 아이템 이름 통일 규칙
ITEM_NAME_NORMALIZATIONS = {
    "전신갑옷 지력 주문서": "전신 갑옷 지력 주문서",
    # "신발 점프력 주문서 10%"는 중복 제거만 하면 됨 (이름은 동일)
}

def normalize_item_name(name: str) -> str:
    """아이템 이름 정규화"""
    normalized = name.strip()
    # 공백 정규화 (여러 공백을 하나로)
    normalized = ' '.join(normalized.split())
    
    # 특정 패턴 통일
    for old, new in ITEM_NAME_NORMALIZATIONS.items():
        if old in normalized:
            normalized = normalized.replace(old, new)
    
    return normalized

def main():
    print("데이터 정리 작업 시작...")
    
    # 아이템 데이터 로드
    print("아이템 데이터 로드 중...")
    with open(ITEM_DATA_PATH, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    # 아이템 이름 통일 및 ID 매핑 생성
    print("아이템 이름 통일 중...")
    item_name_to_ids = {}
    item_id_to_normalized_name = {}
    duplicate_item_ids = set()
    
    for item in items:
        original_name = item.get('name', '')
        normalized_name = normalize_item_name(original_name)
        
        # 이름 통일
        if original_name != normalized_name:
            item['name'] = normalized_name
            print(f"  이름 통일: '{original_name}' -> '{normalized_name}'")
        
        # 이름 -> ID 목록 매핑 (같은 이름의 아이템이 여러 개일 수 있음)
        if normalized_name not in item_name_to_ids:
            item_name_to_ids[normalized_name] = []
        item_name_to_ids[normalized_name].append(item['id'])
        
        # ID -> 정규화된 이름 매핑
        item_id_to_normalized_name[item['id']] = normalized_name
    
    # 중복 아이템 찾기 (같은 이름의 아이템이 여러 개인 경우)
    for name, ids in item_name_to_ids.items():
        if len(ids) > 1:
            # 첫 번째 ID만 유지하고 나머지는 중복으로 표시
            duplicate_item_ids.update(ids[1:])
            print(f"  중복 아이템 발견: '{name}' (ID: {ids})")
    
    # 주요 드랍 아이템 ID 목록 생성
    print("주요 드랍 아이템 ID 목록 생성 중...")
    featured_drop_item_ids = set()
    
    # 공백을 제거한 이름으로 매칭하는 함수
    def remove_spaces(s: str) -> str:
        return ''.join(s.split())
    
    # 공백 제거 버전의 이름 -> ID 매핑 생성
    item_name_no_spaces_to_ids = {}
    for normalized_name, ids in item_name_to_ids.items():
        name_no_spaces = remove_spaces(normalized_name)
        if name_no_spaces not in item_name_no_spaces_to_ids:
            item_name_no_spaces_to_ids[name_no_spaces] = []
        item_name_no_spaces_to_ids[name_no_spaces].extend(ids)
    
    for name in FEATURED_DROP_ITEM_NAMES:
        normalized_name = normalize_item_name(name)
        name_no_spaces = remove_spaces(normalized_name)
        
        # 정확한 이름 매칭 시도
        if normalized_name in item_name_to_ids:
            featured_drop_item_ids.update(item_name_to_ids[normalized_name])
        # 공백 제거 버전으로 매칭 시도
        elif name_no_spaces in item_name_no_spaces_to_ids:
            featured_drop_item_ids.update(item_name_no_spaces_to_ids[name_no_spaces])
            print(f"  공백 무시 매칭: '{name}' -> {len(item_name_no_spaces_to_ids[name_no_spaces])}개 아이템")
        else:
            print(f"  경고: '{name}' (정규화: '{normalized_name}') 아이템을 찾을 수 없습니다.")
    
    print(f"  주요 드랍 아이템 ID 개수: {len(featured_drop_item_ids)}")
    
    # 몬스터 데이터 로드
    print("몬스터 데이터 로드 중...")
    with open(MONSTER_DATA_PATH, 'r', encoding='utf-8') as f:
        monsters = json.load(f)
    
    # 몬스터-아이템 관계 데이터 로드
    print("몬스터-아이템 관계 데이터 로드 중...")
    with open(MONSTER_ITEM_RELATIONS_PATH, 'r', encoding='utf-8') as f:
        relations = json.load(f)
    
    # 몬스터 ID -> 드랍 아이템 ID 목록 매핑 생성 (관계 데이터에서)
    monster_id_to_drop_item_ids = {}
    for relation in relations:
        monster_id = relation.get('monsterId')
        item_id = relation.get('itemId')
        if monster_id and item_id:
            if monster_id not in monster_id_to_drop_item_ids:
                monster_id_to_drop_item_ids[monster_id] = []
            monster_id_to_drop_item_ids[monster_id].append(item_id)
    
    print(f"  관계 데이터에서 {len(monster_id_to_drop_item_ids)}개 몬스터의 드랍 정보 확인")
    
    # 몬스터 데이터 처리
    print("몬스터 데이터 처리 중...")
    updated_count = 0
    featured_drop_updated_count = 0
    
    for monster in monsters:
        monster_id = monster.get('id')
        if not monster_id:
            continue
        
        # 1. 주요 드랍 필드 초기화
        monster['featuredDropItemIds'] = []
        
        # 2. dropItemIds에서 주요 드랍 아이템 찾기
        drop_item_ids_from_monster = set(monster.get('dropItemIds', []))
        
        # 3. monster_item_relations.json에서도 드랍 아이템 찾기
        drop_item_ids_from_relations = set(monster_id_to_drop_item_ids.get(monster_id, []))
        
        # 4. 두 소스 통합
        all_drop_item_ids = drop_item_ids_from_monster | drop_item_ids_from_relations
        
        if all_drop_item_ids:
            # 주요 드랍 아이템 ID 목록에 포함된 아이템만 추가
            new_featured_drops = [
                item_id for item_id in all_drop_item_ids
                if item_id in featured_drop_item_ids
            ]
            
            if new_featured_drops:
                monster['featuredDropItemIds'] = new_featured_drops
                featured_drop_updated_count += 1
        
        updated_count += 1
    
    print(f"  처리된 몬스터 수: {updated_count}")
    print(f"  주요 드랍이 설정된 몬스터 수: {featured_drop_updated_count}")
    
    # 데이터 저장
    print("데이터 저장 중...")
    with open(ITEM_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"  아이템 데이터 저장 완료: {ITEM_DATA_PATH}")
    
    with open(MONSTER_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(monsters, f, ensure_ascii=False, indent=2)
    print(f"  몬스터 데이터 저장 완료: {MONSTER_DATA_PATH}")
    
    print("\n데이터 정리 작업 완료!")
    print(f"- 아이템 이름 통일 완료")
    print(f"- 주요 드랍 필드 초기화 및 재설정 완료")
    print(f"- {featured_drop_updated_count}개 몬스터에 주요 드랍 설정됨")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"오류 발생: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
