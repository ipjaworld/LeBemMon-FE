import json
from pathlib import Path

def add_isReleased_field(input_file, output_file=None):
    """
    몬스터 JSON 파일에 isReleased 필드를 false로 추가합니다.
    """
    if output_file is None:
        output_file = input_file
    
    print(f"파일 읽는 중: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        monsters = json.load(f)
    
    updated_count = 0
    
    for monster in monsters:
        if 'isReleased' not in monster:
            monster['isReleased'] = False
            updated_count += 1
    
    # 파일에 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(monsters, f, ensure_ascii=False, indent=2)
    
    print(f"총 {updated_count}개의 몬스터에 isReleased 필드가 추가되었습니다.")
    print(f"업데이트된 데이터가 {output_file}에 저장되었습니다.")
    
    return updated_count

if __name__ == "__main__":
    # 프로젝트 루트와 src/data 모두 업데이트
    root_file = Path(__file__).parent / "monster_data.json"
    src_file = Path(__file__).parent / "src" / "data" / "monster_data.json"
    
    if root_file.exists():
        print("루트 monster_data.json 업데이트 중...")
        add_isReleased_field(root_file)
    
    if src_file.exists():
        print("\nsrc/data/monster_data.json 업데이트 중...")
        add_isReleased_field(src_file)
