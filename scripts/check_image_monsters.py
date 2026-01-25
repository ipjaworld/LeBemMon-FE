#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이미지에 나온 알파벳별 몬스터가 DB(monster_data.json)에 있는지 체크합니다.
별칭/줄임말 매핑을 적용합니다.
"""

import json

# 이미지 기준 알파벳별 몬스터 (그대로 표기)
IMAGE_ALPHABET_MONSTERS = {
    'H': ['호브', '검켄', '예티', '메카티안', '돼지', '핑크테니', '모래두더지'],
    'A': ['브라운테니', '리셀스퀴드', '벨라모아', '크로노스', '사이티', '망령', '프리져'],
    'P': ['핀호브', '페페', '쿨리좀비', '틱톡', '다크스톤골렘', '뿔버섯'],
    'Y': ['푸켄', '붉켄', '슬라임'],
    'N': ['하프', '주황버섯', '초록버섯', '행키', '주니어페페', '커즈아이', '스타픽시'],
    'E': ['블러드하프', '화팽', '좀비버섯', '듀얼비틀', '루나픽시', '파달', '빨달'],
    'W': ['월묘', '빨달', '다크레쉬', '미요캐츠', '쿨리좀비', '스퀴드', '다크와이번', '스텀프', '주황버섯', '믹스골렘', '흰모래토끼', '마스터크로노스'],
    'R': ['리티', '샐리온', '망둥', '헥터', '페어리', '플래툰크로노스'],
}

# 이미지 표기 → DB 이름 후보 (정규명 + 변형)
NAME_TO_DB = {
    '검켄': ['검은 켄타우로스', '검은켄타우로스'],
    '모래두더지': ['모래 두더지'],
    '쿨리좀비': ['쿨리 좀비', '쿨리좀비'],
    '다크스톤골렘': ['다크 스톤골렘'],
    '푸켄': ['푸른 켄타우로스', '푸른켄타우로스'],
    '붉켄': ['붉은 켄타우로스', '붉은켄타우로스'],
    '행키': ['헹키'],
    '주니어페페': ['주니어 페페', '주니어페페'],
    '블러드하프': ['블러드 하프'],
    '화팽': ['화이트팽'],
    '듀얼비틀': ['듀얼 비틀'],
    '파달': ['파란 달팽이', '파란달팽이'],
    '빨달': ['빨간 달팽이', '빨간달팽이'],
    '다크레쉬': ['다크 레쉬'],
    '다크와이번': ['다크 와이번', '다크와이번'],
    '흰모래토끼': ['흰 모래토끼'],
    '마스터크로노스': ['마스터 크로노스'],
    '망둥': ['망둥이'],
    '플래툰크로노스': ['플래툰 크로노스', '플래툰크로노스'],
}


def normalize(s: str) -> str:
    return s.replace(' ', '').strip()


def main():
    with open('src/data/monster_data.json', 'r', encoding='utf-8') as f:
        monsters = json.load(f)

    db_names = {normalize(m['name']): m['name'] for m in monsters}
    found = []
    not_found = []

    for alphabet, names in IMAGE_ALPHABET_MONSTERS.items():
        for raw in names:
            candidates = NAME_TO_DB.get(raw, [raw])
            matched = None
            for c in candidates:
                key = normalize(c)
                if key in db_names:
                    matched = db_names[key]
                    break
            if matched:
                found.append((alphabet, raw, matched))
            else:
                not_found.append((alphabet, raw))

    lines = [
        '=' * 70,
        '이미지 알파벳 몬스터 ↔ DB 존재 여부',
        '=' * 70,
        '',
        '【 DB에 존재함 】',
    ]
    for a, img, db in sorted(found, key=lambda x: (x[0], x[1])):
        tag = '' if img == db else f'  (이미지: {img})'
        lines.append(f'  {a}: {db}{tag}')
    lines.append('')
    if not_found:
        lines.append('【 DB에 없음 】')
        for a, img in sorted(not_found, key=lambda x: (x[0], x[1])):
            lines.append(f'  {a}: {img}')
    else:
        lines.append('【 DB에 없음 】 (없음)')
    lines.extend([
        '',
        '=' * 70,
        f'존재: {len(found)} / 없음: {len(not_found)} / 전체: {len(found) + len(not_found)}',
        '=' * 70,
    ])
    text = '\n'.join(lines)
    print(text)
    with open('image_monsters_check_result.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print('\n→ 결과 저장: image_monsters_check_result.txt')


if __name__ == '__main__':
    main()
