#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
알파벳 이벤트 아이템 드롭 몬스터 데이터 분석 스크립트
표를 기반으로 지역별 몬스터와 획득 가능 알파벳을 정리합니다.
"""

import json
from collections import defaultdict
from typing import Dict, List, Set

# 표에서 추출한 알파벳별 몬스터 목록
ALPHABET_MONSTERS = {
    'H': [
        '주황버섯', '콜드샤크', '좀비버섯', '주니어스톤볼', '파이어스톤볼', 
        '레쉬', '울트라그레이', '다크와이번', '돼지', '아이스드레이크', '검은 켄타우로스'
    ],
    'A': [
        '리티', '타우로스피어', '루나픽시', '본피쉬', '비틀', '호돌이', 
        '초록버섯', '마스터크로노스', '화이트팽', '스텀프', '주니어페페 인형',
        '트위터', '마이너 좀비', '페어리'
    ],
    'P': [
        '쿨리좀비', '헥터', '포이즌푸퍼', '다크클라크', '주니어씰', 
        '블루와이번', '깨비', '레이스', '검은 켄타우로스', '레드와이번', '와일드보어', 
        '파이어보어', '페페', '엑스텀프', '호문쿨루', '머미독'
    ],
    'Y': [
        '리티', '파란달팽이', '주니어페페', '버크', '스쿠버페페', '파이렛', 
        '구름여우', '하프', '헹키', '스켈독', '버블링', '플라이아이', '마티안',
        '붉은 켄타우로스', '푸른 켄타우로스'
    ],
    'N': [
        '리본돼지', '뿔버섯', '프리져', '클라크', '망령', '타우로마시스', 
        '호브', '스켈레톤지휘관', '아이스스톤볼', '푸퍼', '빨간달팽이', 
        '주니어예티', '루이넬', '주니어 샐리온'  # 일본 루이넬 추가
    ],
    'E': [
        '아이언호그', '마스크피쉬', '듀얼버크', '다크리티', '스타픽시', 
        '크로노스', '옐로우버블티', '레츠', '스켈레톤장교', '다크코니언', 
        '큰구름여우', '주니어 예티', '블랙 라츠', '핑크세이버', '스톤볼'
    ],
    'W': [
        '삼미호', '러스터픽시', '믹스골렘', '스텀프', '초록버섯', '커즈아이', 
        '마티안', '옐로우버블티', '핑크테니', '푸른 켄타우로스', '바이킹', '주니어부기',
        '고스텀프', '레쉬'
    ],
    'R': [
        '물도깨비', '망둥이', '푸른 켄타우로스', '블록골렘', '다크엑스텀프', 
        '플래툰크로노스', '분리된페페', '라츠', '스켈레톤사병', '루이넬', 
        '스포어', '붉은 켄타우로스', '월묘', '씨클', '캡틴'  # 월묘는 R만 줌 (P 제거)
    ]
}

# 이름 변형 매핑 (공백 제거, 별칭 등)
NAME_VARIANTS = {
    '파란달팽이': ['파란 달팽이'],
    '빨간달팽이': ['빨간 달팽이'],
    '스포어': ['스포아'],
    '검은 켄타우로스': ['검은켄타우로스', '검켄'],
    '마스크피쉬': ['마스크피시'],
    '붉은 켄타우로스': ['붉은켄타로우스', '붉은켄타우로스'],
    '하프': ['일반하프'],
    '주니어페페 인형': ['주니어페페인형', '페페인형'],
    '푸른 켄타우로스': ['푸른켄타우로스', '푸켄'],
    '헹키': ['행키'],
    '마이너 좀비': ['마이너좀비'],
    '주니어 예티': ['주니어예티'],
    '주니어 샐리온': ['주니어샐리온'],
    '블랙 라츠': ['블랙라츠'],
    '스톤볼': ['주니어 스톤볼', '주니어스톤볼'],  # 일반 스톤볼
}


def normalize_name(name: str) -> str:
    """이름 정규화 (공백 제거)"""
    return name.replace(' ', '')


def find_monster_by_name(monsters: List[Dict], target_name: str) -> List[Dict]:
    """몬스터 이름으로 찾기 (정규화 및 변형 포함)"""
    normalized_target = normalize_name(target_name)
    results = []
    
    for monster in monsters:
        monster_name = monster.get('name', '')
        normalized_monster = normalize_name(monster_name)
        
        # 정확히 일치
        if normalized_monster == normalized_target:
            results.append(monster)
            continue
        
        # 변형 이름 확인
        variants = NAME_VARIANTS.get(target_name, [])
        for variant in variants:
            if normalize_name(variant) == normalized_monster:
                results.append(monster)
                break
    
    return results


def main():
    # 데이터 로드
    with open('src/data/monster_data.json', 'r', encoding='utf-8') as f:
        monsters = json.load(f)
    
    with open('src/data/region_data.json', 'r', encoding='utf-8') as f:
        regions = json.load(f)
    
    # 지역 ID -> 이름 매핑
    region_map = {r['id']: r['name'] for r in regions}
    
    # 결과 구조: {region_id: {monster_name: [알파벳들]}}
    result: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
    
    # 찾지 못한 몬스터 추적
    not_found = set()
    
    # 각 알파벳별로 처리
    for alphabet, monster_names in ALPHABET_MONSTERS.items():
        for monster_name in monster_names:
            found_monsters = find_monster_by_name(monsters, monster_name)
            
            if not found_monsters:
                not_found.add(monster_name)
                continue
            
            # 각 매칭된 몬스터에 대해
            for monster in found_monsters:
                region_ids = monster.get('regionIds', [])
                
                if not region_ids:
                    # regionIds가 없는 경우도 추적
                    print(f"[WARNING] {monster_name} (ID: {monster.get('id')}) - regionIds 없음")
                    continue
                
                # 각 지역에 알파벳 추가
                for region_id in region_ids:
                    result[region_id][monster_name].add(alphabet)
    
    # 결과를 파일로 저장
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("지역별 알파벳 드롭 몬스터 정리")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # 지역 이름으로 정렬
    sorted_regions = sorted(result.items(), key=lambda x: region_map.get(x[0], x[0]))
    
    for region_id, monster_alphabet_map in sorted_regions:
        region_name = region_map.get(region_id, region_id)
        output_lines.append(f"## {region_name} ({region_id})")
        output_lines.append("")
        
        # 몬스터 이름으로 정렬
        sorted_monsters = sorted(monster_alphabet_map.items())
        
        for monster_name, alphabets in sorted_monsters:
            sorted_alphabets = sorted(alphabets)
            output_lines.append(f"- **{monster_name}**: {', '.join(sorted_alphabets)}")
        
        output_lines.append("")
    
    # 찾지 못한 몬스터 출력
    if not_found:
        output_lines.append("=" * 80)
        output_lines.append("[WARNING] 데이터에서 찾지 못한 몬스터:")
        output_lines.append("=" * 80)
        for name in sorted(not_found):
            output_lines.append(f"- {name}")
        output_lines.append("")
    
    # 통계
    output_lines.append("=" * 80)
    output_lines.append("통계")
    output_lines.append("=" * 80)
    total_monsters = sum(len(monsters) for monsters in result.values())
    output_lines.append(f"총 지역 수: {len(result)}")
    output_lines.append(f"총 몬스터 수 (중복 포함): {total_monsters}")
    output_lines.append(f"찾지 못한 몬스터 수: {len(not_found)}")
    
    # 파일로 저장
    output_text = '\n'.join(output_lines)
    with open('alphabet_drops_by_region.md', 'w', encoding='utf-8') as f:
        f.write(output_text)
    
    # 콘솔에도 출력
    print(output_text)


if __name__ == '__main__':
    main()
