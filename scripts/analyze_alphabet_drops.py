#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
알파벳 드롭 분석 스크립트
1. 3개 이상 알파벳을 드롭하는 몬스터 찾기
2. 제보 자료에 포함되지 않은 기존 데이터 비율 계산
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# 프로젝트 루트 디렉토리
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# 제보 자료 (오늘 받은 데이터)
REPORTED_DATA = {
    'H': ['파랑버섯', '옥토퍼스', '스톤골렘', '듀얼 파이렛', '다크레쉬', '아이스 드레이크', '검은 켄타우로스', '하급닌자', '블랙라츠', '비급', '본피쉬'],
    'A': ['사이티', 'G팬텀워치', '머미독', '브라운테니', '크로노스', '포이즌 푸퍼', '프리저', '도라지'],
    'P': ['뿔버섯', '플래툰크로노스', '사이티', '믹스골렘', '쿨리좀비', '콜드아이', '호저', '흑저', '별다람쥐', '바나드그레이', '호문클루', '주니어카투스', '러스터픽시', '루모', '트리플루모', '훈련용짚인형', '파이어보어', '스켈레톤사병'],
    'Y': ['뿔버섯', '슬라임', '호돌이', '네펜데스', '다크네펜데스', '미스릴뮤테', '라츠', '레츠', '묘선', '푸른 켄타우로스', '다크 코니언'],
    'N': ['루나픽시', '커즈아이', '네오휴로이드', '헹키', '루이넬', '마티안', '초록버섯', '리본돼지', '깨비', '뉴트주니어'],
    'E': ['옥토퍼스', '루나픽시', '화이트팽', '스타픽시', '데스테니', '좀비버섯', '듀얼버크', '스켈독', '팬더테니', '타우로마시스'],
    'W': ['파랑버섯', '다크와이번', '스텀프', '빨간달팽이', '늙은도라지', '레쉬', '마스터크로노스', '미요캐츠', '강화된 미스릴뮤테', '양', '타우로스피어', '네스트골렘', '스켈로스'],
    'R': ['플래툰 크로노스', '리게이터', '크로코', '주니어스톤볼', '헥터', '마이너 좀비', '망둥이', '틱톡', '스콜피언', '울트라그레이', '바이킹'],
}

# 기존 데이터 (사용자가 제공한 이전 데이터)
ORIGINAL_DATA = {
    'H': ['검은 켄타우로스', '파란버섯', '삼미호', '블루와이번', '본피쉬', '비급', '예티', '호브', '메카티안', '돼지', '핑크테니', '다크와이번'],
    'A': ['스파커', '와일드보어', '브라운테니', '포이즌푸퍼', '구름여우', '크로노스', '리셀스퀴드', '다크엑스텀프', '벨라모아', '사이티', '스켈레톤지휘관', '라이오너', '망령', '프리져', '샐리온'],
    'P': ['믹스골렘', '쿨리좀비', '호문쿨루', '뿔버섯', '러스터픽시', '페페', '핀호브'],
    'Y': ['붉은 켄타우로스', '푸른 켄타우로스', '레쉬', '호걸', '슬라임', '스티지', '비틀', '묘선'],
    'N': ['루이넬', '커즈아이', '스타픽시', '네오 휴로이드', '헹키', '하프', '마티안', '주니어페페', '리티', '파란달팽이', '로이드', '상급닌자', '주황버섯', '초록버섯', '옐로우 버블티'],
    'E': ['데스테니', '좀비버섯', '화이트팽', '루나픽시', '블러드 하프', '물도깨비', '버크', '듀얼버크', '삼미호', '주니어레이스', '듀얼 비틀'],
    'W': ['다크와이번', '주황버섯', '월묘', '마스터크로노스', '와일드보어', '늙은 도라지', '미요캐츠', '쿨리좀비', '스텀프', '믹스골렘'],
    'R': ['바이킹', '리게이터', '크로코', '주니어스톤볼', '헥터', '망둥이', '플래툰크로노스', '리티', '샐리온', '페어리'],
}

# 현재 파일의 데이터 (EventPageClient.tsx에서 읽어야 함)
CURRENT_DATA = {
    'H': ['검은 켄타우로스', '파란버섯', '파랑버섯', '옥토퍼스', '스톤골렘', '듀얼 파이렛', '다크레쉬', '다크 레쉬', '아이스 드레이크', '아이스드레이크', '하급닌자', '블랙라츠', '블랙 라츠', '비급', '본피쉬', '본 피쉬', '삼미호', '블루와이번', '예티', '호브', '메카티안', '돼지', '핑크테니', '다크와이번'],
    'A': ['사이티', 'G팬텀워치', '머미독', '브라운테니', '크로노스', '포이즌 푸퍼', '포이즌푸퍼', '프리저', '프리져', '도라지', '스파커', '와일드보어', '구름여우', '리셀스퀴드', '다크엑스텀프', '벨라모아', '스켈레톤지휘관', '라이오너', '망령', '샐리온'],
    'P': ['뿔버섯', '플래툰크로노스', '플래툰 크로노스', '사이티', '믹스골렘', '쿨리좀비', '콜드아이', '호저', '흑저', '별다람쥐', '바나드그레이', '호문클루', '호문쿨루', '주니어카투스', '러스터픽시', '루모', '트리플루모', '훈련용짚인형', '파이어보어', '스켈레톤사병', '페페', '핀호브'],
    'Y': ['뿔버섯', '슬라임', '호돌이', '네펜데스', '다크네펜데스', '미스릴뮤테', '라츠', '레츠', '묘선', '푸른 켄타우로스', '다크 코니언', '다크코니언', '붉은 켄타우로스', '레쉬', '호걸', '스티지', '비틀'],
    'N': ['루나픽시', '커즈아이', '네오휴로이드', '네오 휴로이드', '헹키', '루이넬', '마티안', '초록버섯', '리본돼지', '깨비', '뉴트주니어', '스타픽시', '하프', '주니어페페', '리티', '파란달팽이', '로이드', '상급닌자', '주황버섯', '옐로우 버블티'],
    'E': ['옥토퍼스', '루나픽시', '화이트팽', '스타픽시', '데스테니', '좀비버섯', '듀얼버크', '스켈독', '팬더테니', '타우로마시스', '블러드 하프', '물도깨비', '버크', '삼미호', '주니어레이스', '듀얼 비틀'],
    'W': ['파랑버섯', '파란버섯', '다크와이번', '스텀프', '빨간달팽이', '늙은도라지', '늙은 도라지', '레쉬', '마스터크로노스', '마스터 크로노스', '미요캐츠', '강화된 미스릴뮤테', '양', '타우로스피어', '네스트골렘', '스켈로스', '주황버섯', '월묘', '와일드보어', '쿨리좀비', '믹스골렘'],
    'R': ['플래툰 크로노스', '플래툰크로노스', '리게이터', '크로코', '주니어스톤볼', '헥터', '마이너 좀비', '마이너좀비', '망둥이', '틱톡', '스콜피언', '울트라그레이', '바이킹', '리티', '샐리온', '페어리'],
}

def normalize_name(name: str) -> str:
    """이름 정규화 (공백 제거)"""
    return name.replace(' ', '').replace('　', '').strip()

def get_monster_alphabet_count(data: dict) -> dict:
    """각 몬스터가 몇 개의 알파벳을 드롭하는지 계산"""
    monster_counts = defaultdict(set)
    
    for alphabet, monsters in data.items():
        for monster in monsters:
            normalized = normalize_name(monster)
            monster_counts[normalized].add(alphabet)
    
    # 딕셔너리로 변환 (몬스터명 -> 알파벳 개수)
    result = {}
    for monster, alphabets in monster_counts.items():
        result[monster] = len(alphabets)
    
    return result

def main():
    print("=" * 80)
    print("알파벳 드롭 분석")
    print("=" * 80)
    print()
    
    # 1. 현재 데이터에서 3개 이상 알파벳을 드롭하는 몬스터 찾기
    print("【1. 3개 이상 알파벳을 드롭하는 몬스터】")
    print("-" * 80)
    
    current_counts = get_monster_alphabet_count(CURRENT_DATA)
    three_or_more = {name: count for name, count in current_counts.items() if count >= 3}
    
    if three_or_more:
        for monster, count in sorted(three_or_more.items(), key=lambda x: (-x[1], x[0])):
            # 어떤 알파벳들을 드롭하는지 찾기
            alphabets = []
            for alphabet, monsters in CURRENT_DATA.items():
                for m in monsters:
                    if normalize_name(m) == monster:
                        alphabets.append(alphabet)
            alphabets = sorted(set(alphabets))
            print(f"  {monster}: {count}개 ({', '.join(alphabets)})")
    else:
        print("  없음")
    
    print()
    
    # 2. 제보 자료에 포함되지 않은 기존 데이터 비율 계산
    print("【2. 제보 자료에 포함되지 않은 기존 데이터】")
    print("-" * 80)
    
    # 기존 데이터의 모든 몬스터 (정규화)
    original_monsters = set()
    for monsters in ORIGINAL_DATA.values():
        for monster in monsters:
            original_monsters.add(normalize_name(monster))
    
    # 제보 자료의 모든 몬스터 (정규화)
    reported_monsters = set()
    for monsters in REPORTED_DATA.values():
        for monster in monsters:
            reported_monsters.add(normalize_name(monster))
    
    # 제보 자료에 포함되지 않은 기존 몬스터
    not_in_reported = original_monsters - reported_monsters
    
    total_original = len(original_monsters)
    not_included = len(not_in_reported)
    percentage = (not_included / total_original * 100) if total_original > 0 else 0
    
    print(f"  기존 데이터 총 몬스터 수: {total_original}개")
    print(f"  제보 자료에 포함되지 않은 몬스터 수: {not_included}개")
    print(f"  비율: {percentage:.1f}%")
    print()
    
    if not_in_reported:
        print("  포함되지 않은 몬스터 목록:")
        # 어떤 알파벳을 드롭했는지 표시
        for monster in sorted(not_in_reported):
            alphabets = []
            for alphabet, monsters in ORIGINAL_DATA.items():
                for m in monsters:
                    if normalize_name(m) == monster:
                        alphabets.append(alphabet)
            alphabets = sorted(set(alphabets))
            print(f"    - {monster}: {', '.join(alphabets)}")
    
    print()
    print("=" * 80)

if __name__ == '__main__':
    main()
