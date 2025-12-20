import json
from pathlib import Path
from collections import defaultdict

def remove_duplicate_monsters(input_file, output_file=None):
    """
    exp가 0보다 크고 이름이 겹치는 몬스터는 1건만 남기고 나머지를 제거합니다.
    exp가 가장 높은 것을 우선으로 남기고, 같으면 level이 높은 것을, 그것도 같으면 id가 작은 것을 남깁니다.
    """
    if output_file is None:
        output_file = input_file
    
    print(f"파일 읽는 중: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        monsters = json.load(f)
    
    print(f"총 {len(monsters)}개의 몬스터 로드됨")
    
    # exp > 0인 몬스터들만 필터링
    valid_monsters = [m for m in monsters if m.get('exp', 0) > 0]
    print(f"exp > 0인 몬스터: {len(valid_monsters)}개")
    
    # 이름별로 그룹화
    name_groups = defaultdict(list)
    for monster in valid_monsters:
        name_groups[monster['name']].append(monster)
    
    # 중복이 있는 이름 찾기
    duplicate_names = {name: group for name, group in name_groups.items() if len(group) > 1}
    print(f"중복된 이름: {len(duplicate_names)}개")
    
    # 제거할 몬스터 ID 수집
    monsters_to_remove_ids = set()
    kept_monsters_info = []
    
    for name, group in duplicate_names.items():
        # 정렬: exp 높은 순 -> level 높은 순 -> id 작은 순
        sorted_group = sorted(
            group,
            key=lambda x: (-x.get('exp', 0), -x.get('level', 0), x.get('id', ''))
        )
        
        # 첫 번째(가장 좋은 것)를 남기고 나머지는 제거 목록에 추가
        kept = sorted_group[0]
        to_remove = sorted_group[1:]
        
        kept_monsters_info.append({
            'name': name,
            'kept': kept['id'],
            'removed': [m['id'] for m in to_remove],
            'count': len(to_remove)
        })
        
        for monster in to_remove:
            monsters_to_remove_ids.add(monster['id'])
    
    # 제거 정보 출력
    if kept_monsters_info:
        print("\n제거되는 몬스터 목록:")
        for info in kept_monsters_info:
            print(f"  {info['name']}: ID {info['kept']} 유지, {info['count']}개 제거 (IDs: {', '.join(info['removed'])})")
    
    # exp <= 0인 몬스터는 그대로 유지
    # exp > 0이고 중복이 아닌 몬스터도 유지
    # exp > 0이고 중복이지만 선택된 것만 유지
    filtered_monsters = []
    removed_count = 0
    
    for monster in monsters:
        monster_id = monster.get('id', '')
        monster_exp = monster.get('exp', 0)
        monster_name = monster.get('name', '')
        
        # exp <= 0이면 항상 유지
        if monster_exp <= 0:
            filtered_monsters.append(monster)
        # exp > 0이고 제거 목록에 없으면 유지
        elif monster_id not in monsters_to_remove_ids:
            filtered_monsters.append(monster)
        else:
            removed_count += 1
    
    # 레벨순으로 정렬
    filtered_monsters.sort(key=lambda x: (x.get('level', 0), x.get('name', '')))
    
    # 파일에 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_monsters, f, ensure_ascii=False, indent=2)
    
    print(f"\n총 {removed_count}개의 중복 몬스터가 제거되었습니다.")
    print(f"최종 몬스터 수: {len(filtered_monsters)}개 (기존: {len(monsters)}개)")
    print(f"업데이트된 데이터가 {output_file}에 저장되었습니다.")
    
    return removed_count

if __name__ == "__main__":
    # 프로젝트 루트와 src/data 모두 업데이트
    root_file = Path(__file__).parent / "monster_data.json"
    src_file = Path(__file__).parent / "src" / "data" / "monster_data.json"
    
    if root_file.exists():
        print("루트 monster_data.json 업데이트 중...")
        remove_duplicate_monsters(root_file)
    
    if src_file.exists():
        print("\nsrc/data/monster_data.json 업데이트 중...")
        remove_duplicate_monsters(src_file)
