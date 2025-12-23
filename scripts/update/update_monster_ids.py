import json
from pathlib import Path

def update_monster_ids(input_file, output_file=None):
    """
    몬스터의 ID와 imageUrl을 업데이트합니다.
    """
    if output_file is None:
        output_file = input_file
    
    print(f"파일 읽는 중: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        monsters = json.load(f)
    
    # 몬스터 이름별 실제 ID 매핑
    monster_id_mapping = {
        "길거리 슬라임": "9400538",
        "도심가 버섯": "9400539",
        "킬라 비": "9400540",
        "부머": "9400547",
        "마이티 메이플 이터": "9400548",
        "파이어 터스크": "9400542",
        "일렉트로펀트": "9400543",
        "I.AM.ROBOT": "9400546",
        "주니어 예티": "5100000",
        "그리폰": "9400544",
        "파이어봄": "5100002",
        "변신한 예티": "6300001",
        "울프 스파이더": "9400545",
    }
    
    updated_count = 0
    
    for monster in monsters:
        monster_name = monster['name']
        if monster_name in monster_id_mapping:
            new_id = monster_id_mapping[monster_name]
            old_id = monster['id']
            
            # ID와 imageUrl 업데이트
            monster['id'] = new_id
            monster['imageUrl'] = f"https://maplestory.io/api/gms/62/mob/{new_id}/icon?resize=2"
            
            updated_count += 1
            print(f"  [UPDATE] {monster_name}: {old_id} -> {new_id}")
    
    # 파일에 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(monsters, f, ensure_ascii=False, indent=2)
    
    print(f"\n총 {updated_count}개의 몬스터 ID가 업데이트되었습니다.")
    print(f"업데이트된 데이터가 {output_file}에 저장되었습니다.")
    
    return updated_count

if __name__ == "__main__":
    # 프로젝트 루트와 src/data 모두 업데이트
    root_file = Path(__file__).parent / "monster_data.json"
    src_file = Path(__file__).parent / "src" / "data" / "monster_data.json"
    
    if root_file.exists():
        print("루트 monster_data.json 업데이트 중...")
        update_monster_ids(root_file)
    
    if src_file.exists():
        print("\nsrc/data/monster_data.json 업데이트 중...")
        update_monster_ids(src_file)
