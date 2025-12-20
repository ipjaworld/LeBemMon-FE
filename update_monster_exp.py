import json
from pathlib import Path

# 업데이트할 몬스터의 경험치 정보
# (몬스터 이름, 기존 경험치, 새로운 경험치)
EXP_UPDATES = [
    ("예티", 255, 346),  # 예티(일반) - exp가 255인 예티
    ("호문", 255, 346),  # exp가 255인 호문
    ("묘선", 255, 283),  # exp가 255인 묘선
    ("레이지 버피", 260, 296),
    ("마스터 소울테니", 265, 346),  # exp가 265인 마스터 소울테니
    ("다크 드레이크", 265, 409),
    ("다크 예티", 265, 409),  # 다크 예티(일반) - exp가 265인 다크 예티
    ("사이티", 265, 409),
    ("크루", 265, 393),
    ("클라크", 270, 472),
    ("캡틴", 282, 472),
    ("레쉬", 270, 456),
    ("타우로마시스", 270, 472),
    ("불독", 295, 478),
    ("비틀", 295, 478),
    ("호브", 295, 472),
    ("스켈레톤 지휘관", 315, 481),
    ("루이넬", 320, 488),
    ("호문쿨루", 320, 488),
    ("버푼", 340, 504),
    ("다크 레쉬", 340, 488),
    ("타우로스피어", 350, 567),
    ("웨어울프", 350, 504),
    ("다크 클라크", 370, 567),
    ("듀얼 비틀", 370, 567),
    ("핀호브", 370, 567),  # 공백 없음
    ("딥 버푼", 385, 598),
    ("헹키", 400, 630),
]

def update_monster_exp(input_file, output_file=None):
    """
    몬스터 JSON 파일에서 경험치를 업데이트합니다.
    """
    if output_file is None:
        output_file = input_file
    
    print(f"파일 읽는 중: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        monsters = json.load(f)
    
    updated_count = 0
    
    # 각 업데이트 규칙을 적용
    for monster_name, old_exp, new_exp in EXP_UPDATES:
        count = 0
        for monster in monsters:
            if monster.get('name') == monster_name and monster.get('exp') == old_exp:
                monster['exp'] = new_exp
                count += 1
                updated_count += 1
                print(f"  [OK] {monster_name} (기존: {old_exp} -> 변경: {new_exp})")
        
        if count == 0:
            print(f"  [WARN] {monster_name} (기존 exp: {old_exp})를 찾을 수 없습니다.")
    
    # 파일에 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(monsters, f, ensure_ascii=False, indent=2)
    
    print(f"\n총 {updated_count}개의 몬스터 경험치가 업데이트되었습니다.")
    print(f"업데이트된 데이터가 {output_file}에 저장되었습니다.")
    
    return updated_count

if __name__ == "__main__":
    input_file = Path(__file__).parent / "monster_data.json"
    update_monster_exp(input_file)
