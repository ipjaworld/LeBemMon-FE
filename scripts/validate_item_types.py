"""
item_data.json 타입 정합성 검증 스크립트

검증 항목:
1. 모든 아이템에 itemType 필드가 있는지
2. itemType 값이 유효한지 (equipment, consumable, etc, cash, mountable)
3. equipment 아이템에 majorCategory, mediumCategory가 있는지
4. consumable 아이템에 consumableType이 있는지
5. 마스터리북에 필수 필드가 있는지
"""

import json
from pathlib import Path

INPUT_PATH = Path("src/domains/entities/item/data/item_data.json")

VALID_ITEM_TYPES = {'equipment', 'consumable', 'etc', 'cash', 'mountable'}

VALID_EQUIPMENT_MAJOR = {'weapon', 'common', 'warrior', 'mage', 'archer', 'rogue', 'pirate'}

VALID_CONSUMABLE_TYPES = {'potion', 'scroll', 'mastery-book', 'throwing', 'other'}


def validate():
    with open(INPUT_PATH, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    errors = []
    warnings = []
    stats = {
        'total': len(items),
        'by_type': {},
        'consumable_by_subtype': {},
    }
    
    for i, item in enumerate(items):
        item_id = item.get('id', f'index_{i}')
        item_name = item.get('name', 'unknown')
        
        # 1. itemType 필드 존재 확인
        item_type = item.get('itemType')
        if not item_type:
            errors.append(f"[{item_id}] {item_name}: itemType 필드 없음")
            continue
        
        # 2. itemType 값 유효성
        if item_type not in VALID_ITEM_TYPES:
            errors.append(f"[{item_id}] {item_name}: 유효하지 않은 itemType '{item_type}'")
            continue
        
        # 통계
        stats['by_type'][item_type] = stats['by_type'].get(item_type, 0) + 1
        
        # 3. equipment 검증
        if item_type == 'equipment':
            major = item.get('majorCategory')
            medium = item.get('mediumCategory')
            
            if not major:
                errors.append(f"[{item_id}] {item_name}: equipment인데 majorCategory 없음")
            elif major not in VALID_EQUIPMENT_MAJOR:
                warnings.append(f"[{item_id}] {item_name}: 알 수 없는 majorCategory '{major}'")
            
            if not medium:
                errors.append(f"[{item_id}] {item_name}: equipment인데 mediumCategory 없음")
        
        # 4. consumable 검증
        elif item_type == 'consumable':
            consumable_type = item.get('consumableType')
            
            if not consumable_type:
                errors.append(f"[{item_id}] {item_name}: consumable인데 consumableType 없음")
            elif consumable_type not in VALID_CONSUMABLE_TYPES:
                warnings.append(f"[{item_id}] {item_name}: 알 수 없는 consumableType '{consumable_type}'")
            else:
                stats['consumable_by_subtype'][consumable_type] = stats['consumable_by_subtype'].get(consumable_type, 0) + 1
            
            # 5. 마스터리북 검증
            if consumable_type == 'mastery-book':
                if not item.get('skillName'):
                    warnings.append(f"[{item_id}] {item_name}: 마스터리북인데 skillName 없음")
    
    # 결과 출력
    print("=" * 60)
    print("아이템 타입 정합성 검증 결과")
    print("=" * 60)
    print(f"\n총 아이템 수: {stats['total']}")
    print(f"\nitemType 분포:")
    for t, count in sorted(stats['by_type'].items()):
        print(f"  - {t}: {count}")
    
    if stats['consumable_by_subtype']:
        print(f"\nconsumableType 분포:")
        for t, count in sorted(stats['consumable_by_subtype'].items()):
            print(f"  - {t}: {count}")
    
    print(f"\n오류: {len(errors)}개")
    for err in errors[:10]:  # 최대 10개만 출력
        print(f"  ❌ {err}")
    if len(errors) > 10:
        print(f"  ... 외 {len(errors) - 10}개")
    
    print(f"\n경고: {len(warnings)}개")
    for warn in warnings[:10]:
        print(f"  ⚠️ {warn}")
    if len(warnings) > 10:
        print(f"  ... 외 {len(warnings) - 10}개")
    
    print("\n" + "=" * 60)
    if len(errors) == 0:
        print("✅ 검증 통과: 모든 아이템이 정합성을 만족합니다.")
        return 0
    else:
        print("❌ 검증 실패: 오류를 수정해주세요.")
        return 1


if __name__ == '__main__':
    exit(validate())
