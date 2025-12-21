"""
귀장식 민첩 주문서 60% 드랍 정보 업데이트 스크립트
"""
import json

# 귀장식 민첩 주문서 60% ID
ITEM_ID = "2040028"

# 드랍하는 몬스터 ID들 (출시된 몬스터만)
MONSTER_IDS = [
    "5130105",  # 다크 주니어 예티
    "5120506",  # 비급
    "6230600",  # 아이스 드레이크
    "8141000",  # 바이킹
]

def main():
    # 몬스터 데이터 로드
    with open('src/data/monster_data.json', 'r', encoding='utf-8') as f:
        monsters = json.load(f)
    
    updated_count = 0
    
    for monster in monsters:
        if monster['id'] in MONSTER_IDS:
            # dropItemIds 업데이트
            if 'dropItemIds' not in monster:
                monster['dropItemIds'] = []
            if ITEM_ID not in monster['dropItemIds']:
                monster['dropItemIds'].append(ITEM_ID)
            
            # featuredDropItemIds 업데이트 (주요 드랍)
            if 'featuredDropItemIds' not in monster:
                monster['featuredDropItemIds'] = []
            if ITEM_ID not in monster['featuredDropItemIds']:
                monster['featuredDropItemIds'].append(ITEM_ID)
            
            print(f"[OK] {monster['name']} (ID: {monster['id']}) 업데이트됨")
            updated_count += 1
    
    # 저장
    with open('src/data/monster_data.json', 'w', encoding='utf-8') as f:
        json.dump(monsters, f, ensure_ascii=False, indent=2)
    
    print(f"\n총 {updated_count}개 몬스터 업데이트됨")

if __name__ == "__main__":
    main()

