"""
몬스터 데이터에 regionIds 필드를 추가하는 스크립트

사용법:
1. monster_regions.txt 파일을 생성하고 아래 형식으로 작성:
   # 형식: 몬스터ID|지역ID1,지역ID2,지역ID3
   100100|victoria-perion,victoria-henesys
   100101|victoria-perion
   
2. 스크립트 실행:
   python add_region_ids.py

또는 직접 Python 코드로 사용:
   add_region_ids('monster_regions.txt', 'src/data/monster_data.json')
"""

import json
from pathlib import Path


def add_region_ids(region_mapping_file, monster_data_file, output_file=None):
    """
    몬스터 데이터에 regionIds 필드를 추가합니다.
    
    Args:
        region_mapping_file: 몬스터-지역 매핑 파일 경로 (텍스트 파일)
        monster_data_file: 몬스터 데이터 JSON 파일 경로
        output_file: 출력 파일 경로 (None이면 입력 파일에 덮어쓰기)
    """
    if output_file is None:
        output_file = monster_data_file
    
    # 몬스터-지역 매핑 파일 읽기
    print(f"매핑 파일 읽는 중: {region_mapping_file}")
    region_mapping = {}
    
    if not Path(region_mapping_file).exists():
        print(f"⚠️  경고: {region_mapping_file} 파일이 없습니다.")
        print("샘플 파일을 생성합니다...")
        create_sample_mapping_file(region_mapping_file)
        return
    
    with open(region_mapping_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            # 빈 줄이나 주석 건너뛰기
            if not line or line.startswith('#'):
                continue
            
            try:
                # 형식: 몬스터ID|지역ID1,지역ID2,지역ID3
                if '|' not in line:
                    print(f"⚠️  경고 (줄 {line_num}): '|' 구분자가 없습니다. 건너뜁니다: {line}")
                    continue
                
                monster_id, regions_str = line.split('|', 1)
                monster_id = monster_id.strip()
                regions = [r.strip() for r in regions_str.split(',') if r.strip()]
                
                if monster_id and regions:
                    region_mapping[monster_id] = regions
                    print(f"  [매핑] {monster_id}: {regions}")
                    
            except Exception as e:
                print(f"⚠️  경고 (줄 {line_num}): 파싱 오류 - {e}")
                continue
    
    if not region_mapping:
        print("❌ 매핑 데이터가 없습니다.")
        return
    
    print(f"\n총 {len(region_mapping)}개의 몬스터-지역 매핑을 읽었습니다.")
    
    # 몬스터 데이터 파일 읽기
    print(f"\n몬스터 데이터 파일 읽는 중: {monster_data_file}")
    with open(monster_data_file, 'r', encoding='utf-8') as f:
        monsters = json.load(f)
    
    # regionIds 추가
    updated_count = 0
    not_found_count = 0
    
    for monster in monsters:
        monster_id = monster['id']
        
        if monster_id in region_mapping:
            # 기존 regionIds가 있으면 병합, 없으면 새로 생성
            existing_regions = set(monster.get('regionIds', []))
            new_regions = set(region_mapping[monster_id])
            merged_regions = sorted(list(existing_regions | new_regions))
            
            monster['regionIds'] = merged_regions
            updated_count += 1
            print(f"  [UPDATE] {monster['name']} ({monster_id}): {merged_regions}")
        else:
            # 매핑에 없는 경우, regionIds 필드가 없으면 빈 배열 추가 (선택적)
            if 'regionIds' not in monster:
                monster['regionIds'] = []
    
    # 파일에 저장
    print(f"\n파일 저장 중: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(monsters, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 완료!")
    print(f"  - {updated_count}개의 몬스터에 regionIds가 추가/업데이트되었습니다.")
    if not_found_count > 0:
        print(f"  - {not_found_count}개의 매핑이 몬스터 데이터에 없습니다.")


def create_sample_mapping_file(file_path):
    """샘플 매핑 파일 생성"""
    sample_content = """# 몬스터-지역 매핑 파일
# 형식: 몬스터ID|지역ID1,지역ID2,지역ID3
# 여러 지역은 쉼표(,)로 구분합니다.
# 주석은 #으로 시작합니다.

# 예시:
# 100100|victoria-perion,victoria-henesys
# 100101|victoria-perion
# 210100|victoria-kerning,victoria-lith

# 아래에 실제 매핑 데이터를 입력하세요:

"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    print(f"✅ 샘플 파일이 생성되었습니다: {file_path}")
    print("파일을 열어서 몬스터-지역 매핑 데이터를 추가한 후 다시 실행하세요.")


def main():
    """메인 함수"""
    import sys
    
    # 기본 경로
    script_dir = Path(__file__).parent
    mapping_file = script_dir / 'monster_regions.txt'
    monster_file = script_dir / 'src' / 'data' / 'monster_data.json'
    
    # 커맨드라인 인자로 경로 지정 가능
    if len(sys.argv) > 1:
        mapping_file = Path(sys.argv[1])
    if len(sys.argv) > 2:
        monster_file = Path(sys.argv[2])
    
    add_region_ids(mapping_file, monster_file)


if __name__ == "__main__":
    main()

