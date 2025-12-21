"""
몬스터 이름 패턴을 기반으로 자동으로 regionIds를 할당하는 스크립트
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple


def assign_regions_by_pattern(monster_data_file: str, output_file: str = None):
    """
    몬스터 이름 패턴을 기반으로 regionIds를 자동 할당합니다.
    
    Args:
        monster_data_file: 몬스터 데이터 JSON 파일 경로
        output_file: 출력 파일 경로 (None이면 입력 파일에 덮어쓰기)
    """
    if output_file is None:
        output_file = monster_data_file
    
    # 패턴 매칭 규칙: (패턴, 지역ID)
    # 패턴은 소문자로 변환하여 매칭됩니다.
    # 더 구체적인 패턴을 먼저 배치하여 정확한 매칭 우선
    pattern_rules: List[Tuple[str, str]] = [
        # 리프레 (드래곤 관련 - 구체적인 패턴 먼저)
        ("스켈레곤", "leafre"),
        ("스켈로스", "leafre"),
        ("혼테일", "leafre"),
        ("드래곤", "leafre"),
        
        # 아쿠아로드 (물고기 관련 - 구체적인 패턴 먼저)
        ("버블피쉬", "aqua-road"),
        ("플라워 피쉬", "aqua-road"),
        ("마스크피쉬", "aqua-road"),
        ("스퀴드", "aqua-road"),
        ("물고기", "aqua-road"),
        ("피쉬", "aqua-road"),
        
        # 마가티아 (호문, 실험체)
        ("호문", "nihan-magatia"),
        ("실험체", "nihan-magatia"),
        ("실험", "nihan-magatia"),
        
        # 아리안트 (프릴드, 카투스, 모래 관련)
        ("프릴드", "nihan-ariant"),
        ("카투스", "nihan-ariant"),
        ("모래", "nihan-ariant"),
        
        # 오르비스 (픽시)
        ("픽시", "orbis"),
        
        # 빅토리아 (루팡, 레이스, 달팽이, 슬라임)
        ("루팡", "victoria"),
        ("레이스", "victoria"),
        ("달팽이", "victoria"),
        ("슬라임", "victoria"),
    ]
    
    print(f"몬스터 데이터 파일 읽는 중: {monster_data_file}")
    with open(monster_data_file, 'r', encoding='utf-8') as f:
        monsters = json.load(f)
    
    print(f"\n총 {len(monsters)}개의 몬스터를 처리합니다.\n")
    
    assigned_count = 0
    updated_count = 0
    
    for monster in monsters:
        monster_name = monster.get('name', '')
        monster_id = monster.get('id', '')
        
        # 기존 regionIds 가져오기 (없으면 빈 리스트)
        existing_regions = set(monster.get('regionIds', []))
        matched_regions = set()
        
        # 각 패턴 규칙에 대해 매칭 확인
        for pattern, region_id in pattern_rules:
            if pattern.lower() in monster_name.lower():
                matched_regions.add(region_id)
                print(f"  [매칭] {monster_name} ({monster_id}): '{pattern}' → {region_id}")
        
        # 매칭된 지역이 있으면 추가
        if matched_regions:
            # 기존 지역과 병합
            all_regions = sorted(list(existing_regions | matched_regions))
            monster['regionIds'] = all_regions
            assigned_count += 1
            if existing_regions:
                updated_count += 1
    
    # 파일에 저장
    print(f"\n파일 저장 중: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(monsters, f, ensure_ascii=False, indent=2)
    
    print(f"[완료]")
    print(f"  - {assigned_count}개의 몬스터에 지역이 할당되었습니다.")
    if updated_count > 0:
        print(f"  - {updated_count}개의 몬스터가 기존 지역 정보를 업데이트했습니다.")
    
    return assigned_count


def main():
    """메인 함수"""
    script_dir = Path(__file__).parent
    monster_file = script_dir / 'src' / 'data' / 'monster_data.json'
    
    assign_regions_by_pattern(str(monster_file))


if __name__ == "__main__":
    main()

