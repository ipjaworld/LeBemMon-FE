"""
item_data.json에 itemType 필드 추가

매핑 규칙:
- majorCategory가 weapon, common, warrior, mage, archer, rogue, pirate → itemType: 'equipment'
- majorCategory가 consumable → itemType: 'consumable' + consumableType 추가
"""

import json
from pathlib import Path

INPUT_PATH = Path("src/domains/entities/item/data/item_data.json")
OUTPUT_PATH = INPUT_PATH  # 덮어쓰기

# majorCategory → itemType 매핑
EQUIPMENT_CATEGORIES = {'weapon', 'common', 'warrior', 'mage', 'archer', 'rogue', 'pirate'}

# mediumCategory → consumableType 매핑
CONSUMABLE_TYPE_MAP = {
    'equip-scroll': 'scroll',
    'mastery-book': 'mastery-book',
    'shuriken': 'throwing',
    'etc': 'other',  # 포션 등
}


def migrate_item(item: dict) -> dict:
    """단일 아이템에 itemType 필드 추가"""
    major = item.get('majorCategory', '')
    medium = item.get('mediumCategory', '')
    
    if major in EQUIPMENT_CATEGORIES:
        item['itemType'] = 'equipment'
    elif major == 'consumable':
        item['itemType'] = 'consumable'
        item['consumableType'] = CONSUMABLE_TYPE_MAP.get(medium, 'other')
    else:
        # 알 수 없는 카테고리는 etc로 처리
        item['itemType'] = 'etc'
        item['etcType'] = 'other'
    
    return item


def main():
    # 데이터 로드
    with open(INPUT_PATH, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    print(f"총 {len(items)}개 아이템 처리 중...")
    
    # 변환
    migrated_items = [migrate_item(item) for item in items]
    
    # 통계
    type_counts = {}
    for item in migrated_items:
        t = item.get('itemType', 'unknown')
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print(f"itemType 분포: {type_counts}")
    
    # 저장
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(migrated_items, f, ensure_ascii=False, indent=2)
    
    print(f"완료: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
