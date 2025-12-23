import json
from pathlib import Path

def add_new_monsters(input_file, output_file=None):
    """
    새로운 몬스터들을 JSON 파일에 추가합니다.
    이미지 ID가 제공되지 않았으므로 임시 ID를 사용합니다.
    """
    if output_file is None:
        output_file = input_file
    
    print(f"파일 읽는 중: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        monsters = json.load(f)
    
    # 기존 몬스터 이름 목록 (중복 체크용)
    existing_names = {monster['name'] for monster in monsters}
    
    # 기존 ID들 확인하여 새로운 ID 생성 (가장 큰 ID 찾기)
    existing_ids = {int(monster['id']) for monster in monsters if monster['id'].isdigit()}
    next_id = max(existing_ids) + 1 if existing_ids else 1000000
    
    # 새로운 몬스터 데이터
    new_monsters = [
        {"name": "길거리 슬라임", "level": 19, "hp": 320, "exp": 35, "temp_id": "9900019"},
        {"name": "도심가 버섯", "level": 21, "hp": 350, "exp": 37, "temp_id": "9900021"},
        {"name": "킬라 비", "level": 25, "hp": 730, "exp": 60, "temp_id": "9900025"},
        {"name": "부머", "level": 27, "hp": 700, "exp": 55, "temp_id": "9900027"},
        {"name": "마이티 메이플 이터", "level": 30, "hp": 950, "exp": 65, "temp_id": "9900030"},
        {"name": "파이어 터스크", "level": 36, "hp": 1450, "exp": 85, "temp_id": "9900036"},
        {"name": "일렉트로펀트", "level": 41, "hp": 1600, "exp": 95, "temp_id": "9900041"},
        {"name": "I.AM.ROBOT", "level": 44, "hp": 2490, "exp": 120, "temp_id": "9900044"},
        {"name": "주니어 예티", "level": 50, "hp": 3700, "exp": 135, "temp_id": "9900050"},
        {"name": "그리폰", "level": 50, "hp": 3300, "exp": 220, "temp_id": "9900051"},
        {"name": "파이어봄", "level": 51, "hp": 3600, "exp": 142, "temp_id": "9900052"},
        {"name": "변신한 예티", "level": 65, "hp": 11000, "exp": 390, "temp_id": "9900065"},
        {"name": "울프 스파이더", "level": 80, "hp": 28000, "exp": 1200, "temp_id": "9900080"},
    ]
    
    added_count = 0
    skipped_count = 0
    
    for new_monster in new_monsters:
        if new_monster["name"] in existing_names:
            print(f"  [SKIP] {new_monster['name']} - 이미 존재합니다.")
            skipped_count += 1
            continue
        
        # 몬스터 객체 생성
        monster_obj = {
            "id": new_monster["temp_id"],
            "name": new_monster["name"],
            "imageUrl": f"https://maplestory.io/api/gms/62/mob/{new_monster['temp_id']}/icon?resize=2",
            "level": new_monster["level"],
            "hp": new_monster["hp"],
            "exp": new_monster["exp"],
            "isReleased": False  # 기본값은 false
        }
        
        monsters.append(monster_obj)
        added_count += 1
        print(f"  [ADD] {new_monster['name']} (레벨 {new_monster['level']}) - ID: {new_monster['temp_id']}")
    
    # 레벨순으로 정렬
    monsters.sort(key=lambda x: (x['level'], x['name']))
    
    # 파일에 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(monsters, f, ensure_ascii=False, indent=2)
    
    print(f"\n총 {added_count}개의 몬스터가 추가되었습니다.")
    if skipped_count > 0:
        print(f"{skipped_count}개의 몬스터가 이미 존재하여 건너뛰었습니다.")
    print(f"업데이트된 데이터가 {output_file}에 저장되었습니다.")
    
    return added_count

if __name__ == "__main__":
    # 프로젝트 루트와 src/data 모두 업데이트
    root_file = Path(__file__).parent / "monster_data.json"
    src_file = Path(__file__).parent / "src" / "data" / "monster_data.json"
    
    if root_file.exists():
        print("루트 monster_data.json 업데이트 중...")
        add_new_monsters(root_file)
    
    if src_file.exists():
        print("\nsrc/data/monster_data.json 업데이트 중...")
        add_new_monsters(src_file)
