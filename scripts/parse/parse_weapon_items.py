#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
무기 아이템 텍스트 데이터를 파싱하는 스크립트
"""
import re
import json
from pathlib import Path

# 프로젝트 루트 디렉토리
ROOT_DIR = Path(__file__).parent.parent.parent

# 무기 카테고리 매핑
WEAPON_CATEGORY_MAP = {
    '한손검': 'one-handed-sword',
    '두손검': 'two-handed-sword',
    '한손도끼': 'one-handed-axe',
    '두손도끼': 'two-handed-axe',
    '한손둔기': 'one-handed-blunt',
    '두손둔기': 'two-handed-blunt',
}

def parse_weapon_data(text_data):
    """텍스트 데이터에서 무기 아이템 파싱"""
    items = []
    
    # 각 무기 카테고리별로 파싱
    pattern = r'```\s*([^\n]+)\s*\n(.*?)```'
    matches = re.findall(pattern, text_data, re.DOTALL)
    
    for category_name, content in matches:
        category_key = category_name.strip()
        medium_category = WEAPON_CATEGORY_MAP.get(category_key)
        
        if not medium_category:
            print(f"Warning: Unknown category: {category_key}")
            continue
        
        # 레벨과 이름 추출 (헤더 라인 제외)
        lines = content.strip().split('\n')
        for line in lines[1:]:  # 첫 번째 줄(헤더) 제외
            line = line.strip()
            if not line or line.startswith('레벨'):
                continue
            
            # 탭 또는 공백으로 구분된 레벨과 이름 추출
            parts = re.split(r'\s+', line, 2)
            if len(parts) >= 3:
                try:
                    level = int(parts[0])
                    name = parts[2].strip()
                except (ValueError, IndexError):
                    # 레벨이 0이거나 숫자가 아닌 경우
                    if parts[0] == '0':
                        level = 0
                        name = parts[-1].strip() if len(parts) > 1 else ''
                    else:
                        continue
            elif len(parts) >= 2:
                # 레벨만 있는 경우
                try:
                    level = int(parts[0])
                    name = parts[1].strip() if len(parts) > 1 else ''
                except ValueError:
                    continue
            else:
                continue
            
            if name:
                items.append({
                    'name': name,
                    'reqLevel': level,
                    'mediumCategory': medium_category,
                    'majorCategory': 'weapon',
                })
    
    return items

def main():
    # 사용자가 제공한 데이터
    text_data = """
``` 한손검

레벨	아이콘	이름
0		검
0		하늘색 우산
0		낡은 글라디우스
10		카알 대검
15		사브르
20		바이킹 소드
20		쿠크리
25		일룬
30		글라디우스
35		붉은 채찍
35		커틀러스
35		메이플 소드
38		화염의 카타나
40		노란색 우산
40		트라우스
40		광선채찍
43		메이플 켈트 소드
45		영웅의 글라디우스
50		쥬얼 쿠아다라
60		네오코라
64		메이플 글로리 소드
70		레드 카타나
80		아츠
90		프라우테
100		스파타
110		드래곤 카라벨라

```

``` 두손검

레벨	아이콘	이름
0		나무 야구 방망이
10		목검
15		환목검
20		양손검
25		클러디
30		왕푸
30		알루미늄 야구 방망이
35		하이랜더
40		쟈드
50		호검
60		그리스
64		메이플 소울 로헨
70		그륜힐
80		그레이트 로헨
80		청운검
90		라 투핸더
90		참마도
100		참화도
110		드래곤 클레이모어
```

``` 한손도끼

레벨	아이콘	이름
0		손 도끼
10		양날 도끼
15		전투 도끼
20		콘트라 엑스
25		미스릴 도끼
30		파이어 잭
35		당커
40		블루 카운터
50		벅
60		호크헤드
64		메이플 스틸 엑스
70		미하일
80		리프 엑스
90		비펜니스
100		토마호크
110		드래곤 엑스

```

``` 두손도끼

레벨	아이콘	이름
10		쇠 도끼
15		철제 도끼
20		강철 도끼
25		양손 도끼
30		버크
35		니암
40		버드빌
43		메이플 투핸디드 엑스
50		라이징
60		샤이닝
64		메이플 데몬엑스
70		크로노
80		헬리오스
90		클로니안 엑스
100		타바르
110		드래곤 배틀엑스
```

``` 한손둔기

레벨	아이콘	이름
0		파란색 꽃무늬 튜브
0		몽둥이
15		메이스
15		망치
15		가죽 핸드백
20		강철 메이스
20		007 가방
25		뚜러
25		세계의 돼지도감
25		퓨전 메이스
25		빨간색 꽃무늬 튜브
30		막대 사탕
30		프라이팬
30		워해머
35		호스맨즈
40		젝커
40		보라색 튜브
50		너클메이스
50		검은색 튜브
60		타무스
60		구명 튜브
64		메이플 해버크 해머
65		도깨비 방망이
70		파노 튜브
70		스튬
75		모던스튬
80		골든해머
90		루인해머
100		배틀해머
110		드래곤 메이스
```

``` 두손둔기
레벨	아이콘	이름
10		나무 망치
15		강철구 망치
20		사각 망치
20		곡괭이
25		몽키 스페너
30		미스릴 모울
35		빅해머
40		타이탄
43		메이플 빅 모울
50		골든 모울
60		플루튬
64		메이플 벨제트
70		호프만
80		크롬
90		레오마이트
100		골든 스미스해머
110		드래곤 플레임

```
"""
    
    items = parse_weapon_data(text_data)
    
    print(f"Parsed {len(items)} weapon items")
    print("\nParsed items:")
    print(json.dumps(items, ensure_ascii=False, indent=2))
    
    # 통계 출력
    by_category = {}
    for item in items:
        cat = item['mediumCategory']
        by_category[cat] = by_category.get(cat, 0) + 1
    
    print("\nItems by category:")
    for cat, count in sorted(by_category.items()):
        print(f"  {cat}: {count}")

if __name__ == "__main__":
    main()

