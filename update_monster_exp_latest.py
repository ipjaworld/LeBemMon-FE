"""
최신 패치(2025년 12월 23일) 몬스터 경험치 업데이트 스크립트
"""
import json

# 최신 패치에서 업데이트할 몬스터의 경험치 정보
# (몬스터 ID, 기존 경험치, 새로운 경험치)
EXP_UPDATES = [
    ("6300001", 390, 481),  # 예티(변신)
    ("6300006", 455, 619),  # 예티(분리)
    ("6130102", 420, 584),  # 페페(분리)
    ("6400001", 445, 589),  # 다크 예티(변신)
    ("6400002", 715, 792),  # 다크 예티(분리)
    ("6230201", 700, 777),  # 다크 페페(분리)
]

def main():
    # 몬스터 데이터 로드
    with open('src/data/monster_data.json', 'r', encoding='utf-8') as f:
        monsters = json.load(f)
    
    updated_count = 0
    not_found = []
    
    # 각 업데이트 규칙을 적용
    for monster_id, old_exp, new_exp in EXP_UPDATES:
        found = False
        for monster in monsters:
            if monster.get('id') == monster_id:
                if monster.get('exp') == old_exp:
                    monster['exp'] = new_exp
                    updated_count += 1
                    print(f"  [OK] {monster.get('name')} (ID: {monster_id}) {old_exp} -> {new_exp}")
                    found = True
                else:
                    print(f"  [WARN] {monster.get('name')} (ID: {monster_id}) 현재 경험치가 {monster.get('exp')}입니다. 예상: {old_exp}")
                    found = True
                break
        
        if not found:
            not_found.append((monster_id, old_exp, new_exp))
    
    if not_found:
        print(f"\n[WARN] 다음 몬스터를 찾을 수 없습니다:")
        for monster_id, old_exp, new_exp in not_found:
            print(f"  ID: {monster_id}, 예상 경험치: {old_exp} -> {new_exp}")
    
    # 파일에 저장
    with open('src/data/monster_data.json', 'w', encoding='utf-8') as f:
        json.dump(monsters, f, ensure_ascii=False, indent=2)
    
    print(f"\n총 {updated_count}개의 몬스터 경험치가 업데이트되었습니다.")
    print(f"업데이트된 데이터가 src/data/monster_data.json에 저장되었습니다.")
    
    return updated_count

if __name__ == "__main__":
    main()

