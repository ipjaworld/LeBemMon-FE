"""
마스터리북 데이터 생성 스크립트
"""
import json
from pathlib import Path
from typing import Optional

# 인기 마스터리북 목록
POPULAR_MASTERY_BOOKS = [
    "샤프아이즈 20", "샤프아이즈 30", 
    "돌진 30", 
    "버서크 30", 
    "빅뱅 30", 
    "제네시스 20", "제네시스 30", 
    "폭풍의 시 30", 
    "피어싱 20", 
    "페이크 30", 
    "트리플 스로우 20", "트리플 스로우 30", 
    "부메랑 스텝 30", 
    "스탠스 20"
]

# 마스터리북 데이터: (스킬명, 레벨, 직업카테고리, 세부직업, 드롭몬스터들)
# 퀘스트로만 획득 가능한 것은 빈 리스트
MASTERY_BOOK_DATA = [
    # === 공통 (전직업) ===
    ("메이플 용사", 10, "common", None, []),  # 4차 전직
    ("메이플 용사", 20, "common", None, ["혼테일"]),
    ("메이플 용사", 30, "common", None, []),  # 핑크빈
    
    # === 전사 공통 ===
    ("몬스터 마그넷", 10, "warrior", "warrior-common", []),  # 4차 전직
    ("몬스터 마그넷", 20, "warrior", "warrior-common", ["피아누스"]),  # 네스트 골렘 미출시
    ("몬스터 마그넷", 30, "warrior", "warrior-common", ["피아누스"]),
    
    ("스탠스", 10, "warrior", "warrior-common", []),  # 퀘스트
    ("스탠스", 20, "warrior", "warrior-common", ["다크코니언", "레비아탄", "파풀라투스"]),  # 후회의 수호대장 미출시
    ("스탠스", 30, "warrior", "warrior-common", ["자쿰"]),  # 후회의 수호병 미출시
    
    ("돌진", 10, "warrior", "warrior-common", []),  # 퀘스트
    ("돌진", 20, "warrior", "warrior-common", ["다크코니언", "피아누스"]),
    ("돌진", 30, "warrior", "warrior-common", ["피아누스"]),
    
    ("아킬레스", 10, "warrior", "warrior-common", []),  # 4차 전직
    ("아킬레스", 20, "warrior", "warrior-common", ["스켈로스"]),
    ("아킬레스", 30, "warrior", "warrior-common", ["마뇽"]),  # 릴리노흐 미출시
    
    # === 전사 (히어로) ===
    ("어드밴스드 콤보", 10, "warrior", "hero", ["자쿰"]),
    ("어드밴스드 콤보", 20, "warrior", "hero", []),  # 네스트 골렘 미출시
    ("어드밴스드 콤보", 30, "warrior", "hero", ["스켈로스"]),  # 길드대항전
    
    ("블로킹", 10, "warrior", "hero", []),  # 퀘스트
    ("블로킹", 20, "warrior", "hero", ["스켈레곤"]),
    ("블로킹", 30, "warrior", "hero", ["마뇽"]),
    
    ("브랜디쉬", 10, "warrior", "hero", []),  # 4차 전직
    ("브랜디쉬", 20, "warrior", "hero", ["다크 와이번"]),
    ("브랜디쉬", 30, "warrior", "hero", ["파풀라투스"]),
    
    ("인레이지", 10, "warrior", "hero", []),  # 퀘스트
    ("인레이지", 20, "warrior", "hero", ["자쿰"]),
    ("인레이지", 30, "warrior", "hero", ["혼테일"]),
    
    # === 전사 (다크나이트) ===
    ("버서크", 10, "warrior", "dark-knight", []),  # 퀘스트
    ("버서크", 20, "warrior", "dark-knight", ["자쿰"]),
    ("버서크", 30, "warrior", "dark-knight", ["혼테일"]),
    
    # === 전사 (팔라딘) ===
    ("생츄어리", 10, "warrior", "paladin", []),  # 퀘스트
    ("생츄어리", 20, "warrior", "paladin", ["자쿰"]),
    ("생츄어리", 30, "warrior", "paladin", ["혼테일"]),
    
    ("홀리 차지", 10, "warrior", "paladin", []),  # 퀘스트
    ("홀리 차지", 20, "warrior", "paladin", ["그리프"]),  # 네스트 골렘, 도도 미출시
    
    ("디바인 차지", 10, "warrior", "paladin", []),  # 퀘스트
    ("디바인 차지", 20, "warrior", "paladin", ["다크 와이번", "그리프"]),  # 도도 미출시
    
    ("블래스트", 10, "warrior", "paladin", []),  # 4차 전직
    ("블래스트", 20, "warrior", "paladin", ["스켈레곤"]),
    ("블래스트", 30, "warrior", "paladin", ["파풀라투스"]),  # 라이카 미출시
    
    ("어드밴스드 차지", 10, "warrior", "paladin", ["자쿰"]),
    
    # === 마법사 공통 ===
    ("빅뱅", 10, "mage", "mage-common", []),  # 4차 전직
    ("빅뱅", 20, "mage", "mage-common", ["다크 와이번", "피아누스"]),
    ("빅뱅", 30, "mage", "mage-common", ["피아누스"]),
    
    ("마나 리플렉션", 10, "mage", "mage-common", []),  # 4차 전직
    ("마나 리플렉션", 20, "mage", "mage-common", ["다크코니언", "피아누스"]),
    ("마나 리플렉션", 30, "mage", "mage-common", ["피아누스"]),  # 도도 미출시
    
    ("인피니티", 10, "mage", "mage-common", []),  # 퀘스트
    ("인피니티", 20, "mage", "mage-common", ["파풀라투스"]),
    ("인피니티", 30, "mage", "mage-common", ["자쿰"]),
    
    # === 마법사 (비숍) ===
    ("홀리실드", 10, "mage", "bishop", []),  # 4차 전직
    ("홀리실드", 20, "mage", "bishop", ["스켈로스"]),
    ("홀리실드", 30, "mage", "bishop", ["마뇽"]),
    
    ("엔젤레이", 10, "mage", "bishop", ["자쿰"]),
    ("엔젤레이", 20, "mage", "bishop", ["스켈레곤"]),  # 추억의 사제 미출시
    ("엔젤레이", 30, "mage", "bishop", ["파풀라투스"]),
    
    ("제네시스", 10, "mage", "bishop", []),  # 퀘스트
    ("제네시스", 20, "mage", "bishop", ["자쿰"]),
    ("제네시스", 30, "mage", "bishop", ["혼테일"]),
    
    # === 마법사 (썬,콜 아크메이지) ===
    ("아이스 데몬", 10, "mage", "arch-mage-il", []),  # 퀘스트
    ("아이스 데몬", 20, "mage", "arch-mage-il", ["콜드샤크", "그리프"]),
    ("아이스 데몬", 30, "mage", "arch-mage-il", ["파풀라투스"]),  # 라이카 미출시
    
    ("이프리트", 10, "mage", "arch-mage-il", []),  # 퀘스트
    ("이프리트", 20, "mage", "arch-mage-il", ["뉴트주니어"]),
    ("이프리트", 30, "mage", "arch-mage-il", []),  # 길드대항전
    
    ("체인 라이트닝", 10, "mage", "arch-mage-il", []),  # 4차 전직
    ("체인 라이트닝", 20, "mage", "arch-mage-il", ["그리프"]),  # 리셀스퀴드 미출시
    ("체인 라이트닝", 30, "mage", "arch-mage-il", ["레비아탄"]),  # 길드대항전
    
    ("블리자드", 10, "mage", "arch-mage-il", []),  # 퀘스트
    ("블리자드", 20, "mage", "arch-mage-il", ["자쿰"]),  # 망각의 수호병 미출시
    ("블리자드", 30, "mage", "arch-mage-il", ["혼테일"]),
    
    # === 마법사 (불.독 아크메이지) ===
    ("파이어 데몬", 10, "mage", "arch-mage-fp", []),  # 퀘스트
    ("파이어 데몬", 20, "mage", "arch-mage-fp", ["다크코니언", "뉴트주니어", "마뇽"]),
    ("파이어 데몬", 30, "mage", "arch-mage-fp", ["파풀라투스"]),  # 릴리노흐 미출시
    
    ("엘퀴네스", 10, "mage", "arch-mage-fp", []),  # 퀘스트
    ("엘퀴네스", 20, "mage", "arch-mage-fp", []),  # 네스트 골렘 미출시
    ("엘퀴네스", 30, "mage", "arch-mage-fp", []),  # 망각의 사제 미출시
    
    ("페럴라이즈", 10, "mage", "arch-mage-fp", []),  # 4차 전직
    ("페럴라이즈", 20, "mage", "arch-mage-fp", ["뉴트주니어", "마뇽"]),  # 길드대항전
    ("페럴라이즈", 30, "mage", "arch-mage-fp", ["레비아탄"]),
    
    ("메테오", 10, "mage", "arch-mage-fp", []),  # 퀘스트
    ("메테오", 20, "mage", "arch-mage-fp", ["자쿰"]),
    ("메테오", 30, "mage", "arch-mage-fp", ["혼테일"]),
    
    # === 궁수 공통 ===
    ("샤프아이즈", 10, "archer", "archer-common", []),  # 4차 전직
    ("샤프아이즈", 20, "archer", "archer-common", ["콜드샤크", "피아누스"]),
    ("샤프아이즈", 30, "archer", "archer-common", ["피아누스", "스켈로스"]),
    
    ("드래곤 펄스", 10, "archer", "archer-common", []),  # 퀘스트
    ("드래곤 펄스", 20, "archer", "archer-common", ["뉴트주니어", "피아누스"]),
    ("드래곤 펄스", 30, "archer", "archer-common", ["피아누스"]),  # 릴리노흐 미출시
    
    # === 궁수 (보우마스터) ===
    ("집중", 10, "archer", "bow-master", []),  # 퀘스트
    ("집중", 20, "archer", "bow-master", ["자쿰"]),
    ("집중", 30, "archer", "bow-master", ["혼테일"]),
    
    ("보우 엑스퍼트", 10, "archer", "bow-master", []),  # 4차 전직
    ("보우 엑스퍼트", 20, "archer", "bow-master", ["다크코니언", "파풀라투스"]),  # 추억의 수호병 미출시
    ("보우 엑스퍼트", 30, "archer", "bow-master", ["자쿰"]),
    
    ("폭풍의 시", 10, "archer", "bow-master", []),  # 퀘스트
    ("폭풍의 시", 20, "archer", "bow-master", []),  # 네스트 골렘, 길드대항전
    ("폭풍의 시", 30, "archer", "bow-master", ["레비아탄", "파풀라투스"]),  # 라이카, 길드대항전
    
    ("피닉스", 10, "archer", "bow-master", []),  # 퀘스트
    ("피닉스", 20, "archer", "bow-master", ["스켈레곤"]),
    ("피닉스", 30, "archer", "bow-master", ["마뇽"]),
    
    ("햄스트링", 10, "archer", "bow-master", []),  # 4차 전직
    ("햄스트링", 20, "archer", "bow-master", ["스켈로스"]),
    ("햄스트링", 30, "archer", "bow-master", ["그리프"]),  # 도도 미출시
    
    # === 궁수 (신궁) ===
    ("피어싱", 10, "archer", "marksman", []),  # 퀘스트
    ("피어싱", 20, "archer", "marksman", ["스켈레곤"]),
    ("피어싱", 30, "archer", "marksman", ["파풀라투스"]),
    
    ("프리져", 10, "archer", "marksman", []),  # 퀘스트
    ("프리져", 20, "archer", "marksman", ["다크코니언", "그리프"]),
    ("프리져", 30, "archer", "marksman", []),  # 추억의 수호대장 미출시
    
    ("블라인드", 10, "archer", "marksman", []),  # 4차 전직
    ("블라인드", 20, "archer", "marksman", ["스켈로스"]),
    ("블라인드", 30, "archer", "marksman", ["그리프"]),
    
    ("스나이핑", 10, "archer", "marksman", []),  # 퀘스트
    ("스나이핑", 20, "archer", "marksman", ["자쿰"]),
    ("스나이핑", 30, "archer", "marksman", ["혼테일"]),
    
    ("크로스보우 엑스퍼트", 10, "archer", "marksman", []),  # 4차 전직
    ("크로스보우 엑스퍼트", 20, "archer", "marksman", ["뉴트주니어", "파풀라투스"]),  # 추억의 신관 미출시
    ("크로스보우 엑스퍼트", 30, "archer", "marksman", ["자쿰"]),
    
    # === 도적 공통 ===
    ("페이크", 10, "rogue", "rogue-common", []),  # 4차 전직
    ("페이크", 20, "rogue", "rogue-common", ["다크 와이번", "피아누스"]),
    ("페이크", 30, "rogue", "rogue-common", ["피아누스", "레비아탄"]),  # 후회의 신관, 도도 미출시
    
    ("베놈", 10, "rogue", "rogue-common", []),  # 4차 전직
    ("베놈", 20, "rogue", "rogue-common", ["다크코니언", "파풀라투스"]),
    ("베놈", 30, "rogue", "rogue-common", ["자쿰"]),  # 후회의 사제 미출시
    
    ("쇼다운", 10, "rogue", "rogue-common", []),  # 퀘스트
    ("쇼다운", 20, "rogue", "rogue-common", ["마뇽"]),  # 네스트 골렘, 릴리노흐 미출시
    ("쇼다운", 30, "rogue", "rogue-common", []),  # 길드대항전
    
    ("닌자 앰부쉬", 10, "rogue", "rogue-common", []),  # 퀘스트
    ("닌자 앰부쉬", 20, "rogue", "rogue-common", ["바이킹", "피아누스"]),
    ("닌자 앰부쉬", 30, "rogue", "rogue-common", ["피아누스"]),
    
    # === 도적 (나이트로드) ===
    ("스피릿 자벨린", 10, "rogue", "night-lord", []),  # 4차 전직
    ("스피릿 자벨린", 20, "rogue", "night-lord", ["브레스튼"]),
    ("스피릿 자벨린", 30, "rogue", "night-lord", ["파풀라투스"]),  # 망각의 신관 미출시
    
    ("트리플 스로우", 10, "rogue", "night-lord", ["자쿰"]),
    ("트리플 스로우", 20, "rogue", "night-lord", ["자쿰"]),
    ("트리플 스로우", 30, "rogue", "night-lord", ["혼테일"]),
    
    ("닌자 스톰", 10, "rogue", "night-lord", []),  # 퀘스트
    ("닌자 스톰", 20, "rogue", "night-lord", ["스켈레곤"]),
    ("닌자 스톰", 30, "rogue", "night-lord", []),  # 망각의 수호대장, 길드대항전
    
    # === 도적 (섀도어) ===
    ("암살", 10, "rogue", "shadower", []),  # 퀘스트
    ("암살", 20, "rogue", "shadower", ["뉴트주니어", "그리프"]),
    ("암살", 30, "rogue", "shadower", []),  # 망각의 수호대장, 길드대항전
    
    ("연막탄", 10, "rogue", "shadower", []),  # 퀘스트
    ("연막탄", 20, "rogue", "shadower", ["자쿰"]),
    ("연막탄", 30, "rogue", "shadower", ["혼테일"]),
    
    ("부메랑 스텝", 10, "rogue", "shadower", []),  # 4차 전직
    ("부메랑 스텝", 20, "rogue", "shadower", ["스켈로스"]),  # 라이카 미출시
    ("부메랑 스텝", 30, "rogue", "shadower", ["파풀라투스"]),
    
    # === 에반 ===
    ("소울스톤", 10, "evan", None, ["자쿰"]),
    ("소울스톤", 20, "evan", None, []),  # 후회의 수호병, 릴리노흐 미출시
    
    ("일루전", 10, "evan", None, []),  # 4차 전직
    ("일루전", 20, "evan", None, ["파풀라투스"]),  # 레드 드래곤 터틀 미출시
    ("일루전", 30, "evan", None, []),  # 레드 와이번, 도도 미출시
    
    ("다크포그", 10, "evan", None, ["자쿰"]),
    ("다크포그", 20, "evan", None, []),  # 추억의 수호대장, 도도 미출시
    ("다크포그", 30, "evan", None, ["그린코니언"]),  # 라이카 미출시
    
    ("블레이즈", 10, "evan", None, []),  # 4차 전직
    ("블레이즈", 20, "evan", None, ["피아누스"]),  # 본 피쉬 미출시
    ("블레이즈", 30, "evan", None, ["혼테일"]),  # 후회의 수호대장 미출시
    
    ("플레임 휠", 10, "evan", None, ["자쿰"]),
    ("플레임 휠", 20, "evan", None, ["다크 와이번", "그리프"]),
    ("플레임 휠", 30, "evan", None, ["파풀라투스"]),  # 추억의 사제 미출시
    
    ("매직 마스터리", 10, "evan", None, ["자쿰"]),
    ("매직 마스터리", 20, "evan", None, ["마뇽", "스켈로스"]),
    ("매직 마스터리", 30, "evan", None, []),  # 추억의 신관, 릴리노흐 미출시
    
    ("오닉스의 축복", 10, "evan", None, []),  # 4차 전직
    ("오닉스의 축복", 20, "evan", None, []),  # 후회의 신관, 라이카 미출시
    ("오닉스의 축복", 30, "evan", None, ["혼테일"]),  # 망각의 수호병 미출시
    
    # === 아란 ===
    ("오버 스윙", 10, "aran", None, []),  # 4차 전직
    ("오버 스윙", 20, "aran", None, ["블루 드래곤터틀", "파풀라투스"]),
    ("오버 스윙", 30, "aran", None, []),  # 레드 와이번, 도도 미출시
    
    ("하이 마스터리", 10, "aran", None, []),  # 4차 전직
    ("하이 마스터리", 20, "aran", None, ["다크 와이번", "그리프"]),
    ("하이 마스터리", 30, "aran", None, ["파풀라투스"]),  # 추억의 사제 미출시
    
    ("프리즈 스탠딩", 10, "aran", None, []),  # 4차 전직
    ("프리즈 스탠딩", 20, "aran", None, ["스켈로스", "마뇽"]),
    ("프리즈 스탠딩", 30, "aran", None, []),  # 추억의 신관, 릴리노흐 미출시
    
    ("파이널 블로우", 10, "aran", None, ["자쿰"]),
    ("파이널 블로우", 20, "aran", None, ["피아누스"]),  # 본 피쉬 미출시
    ("파이널 블로우", 30, "aran", None, ["혼테일"]),  # 후회의 수호대장 미출시
    
    ("하이 디펜스", 10, "aran", None, ["자쿰"]),
    ("하이 디펜스", 20, "aran", None, []),  # 추억의 수호대장, 도도 미출시
    ("하이 디펜스", 30, "aran", None, ["그린코니언"]),  # 라이카 미출시
    
    ("콤보 템페스트", 10, "aran", None, ["자쿰"]),
    ("콤보 템페스트", 20, "aran", None, []),  # 후회의 수호병, 릴리노흐 미출시
    ("콤보 템페스트", 30, "aran", None, ["혼테일"]),  # 망각의 수호병 미출시
    
    ("콤보 배리어", 10, "aran", None, ["자쿰"]),
    ("콤보 배리어", 20, "aran", None, []),  # 후회의 신관, 라이카 미출시
    ("콤보 배리어", 30, "aran", None, ["혼테일"]),  # 망각의 수호대장 미출시
]


def load_monster_data():
    """몬스터 데이터 로드"""
    with open('src/data/monster_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def load_item_data():
    """아이템 데이터 로드"""
    with open('src/data/item_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def find_monster_by_name(monsters, name):
    """이름으로 몬스터 찾기 (출시된 몬스터만)"""
    for monster in monsters:
        if monster.get('name') == name and monster.get('isReleased', False):
            return monster
    return None


def generate_mastery_book_id(skill_name, skill_level):
    """마스터리북 ID 생성"""
    # 스킬 이름을 기반으로 고유 ID 생성
    import hashlib
    base = f"mb_{skill_name}_{skill_level}"
    hash_suffix = hashlib.md5(base.encode()).hexdigest()[:6]
    return f"mb_{hash_suffix}"


def is_popular_mastery_book(skill_name, skill_level):
    """인기 마스터리북 여부 확인"""
    book_name = f"{skill_name} {skill_level}"
    return book_name in POPULAR_MASTERY_BOOKS


def main():
    monsters = load_monster_data()
    existing_items = load_item_data()
    
    # 마스터리북 아이템 생성
    mastery_books = []
    monster_to_books = {}  # 몬스터ID -> 마스터리북ID 리스트
    
    for skill_name, skill_level, job_category, job_sub_category, drop_monsters in MASTERY_BOOK_DATA:
        book_id = generate_mastery_book_id(skill_name, skill_level)
        display_name = f"[마스터리북] {skill_name} {skill_level}"
        is_popular = is_popular_mastery_book(skill_name, skill_level)
        
        book = {
            "id": book_id,
            "name": display_name,
            "imageUrl": "https://maplestory.io/api/gms/200/item/2290001/icon?resize=2",  # 기본 마스터리북 아이콘
            "majorCategory": "consumable",
            "mediumCategory": "mastery-book",
            "isReleased": True,
            "skillName": skill_name,
            "skillLevel": skill_level,
            "jobCategory": job_category
        }
        
        if job_sub_category:
            book["jobSubCategory"] = job_sub_category
            
        if is_popular:
            book["isPopularMasteryBook"] = True
            
        mastery_books.append(book)
        
        # 몬스터-마스터리북 관계 설정
        for monster_name in drop_monsters:
            monster = find_monster_by_name(monsters, monster_name)
            if monster:
                monster_id = monster['id']
                if monster_id not in monster_to_books:
                    monster_to_books[monster_id] = []
                monster_to_books[monster_id].append(book_id)
            else:
                print(f"[WARN] 몬스터를 찾을 수 없음: {monster_name} (마스터리북: {display_name})")
    
    # 기존 아이템에 마스터리북 추가
    all_items = existing_items + mastery_books
    
    # 아이템 데이터 저장
    with open('src/data/item_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 마스터리북 {len(mastery_books)}개 추가됨")
    print(f"[OK] 총 아이템 수: {len(all_items)}개")
    
    # 몬스터 데이터 업데이트 (featuredDropItemIds에 인기 마스터리북 추가)
    updated_count = 0
    for monster in monsters:
        monster_id = monster['id']
        if monster_id in monster_to_books:
            # 기존 드랍 아이템 ID 가져오기
            if 'dropItemIds' not in monster:
                monster['dropItemIds'] = []
            if 'featuredDropItemIds' not in monster:
                monster['featuredDropItemIds'] = []
                
            for book_id in monster_to_books[monster_id]:
                if book_id not in monster['dropItemIds']:
                    monster['dropItemIds'].append(book_id)
                    
                # 인기 마스터리북인 경우 featuredDropItemIds에도 추가
                book = next((b for b in mastery_books if b['id'] == book_id), None)
                if book and book.get('isPopularMasteryBook') and book_id not in monster['featuredDropItemIds']:
                    monster['featuredDropItemIds'].append(book_id)
            
            updated_count += 1
    
    # 몬스터 데이터 저장
    with open('src/data/monster_data.json', 'w', encoding='utf-8') as f:
        json.dump(monsters, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 몬스터 {updated_count}개 업데이트됨")
    
    # 통계 출력
    popular_count = sum(1 for b in mastery_books if b.get('isPopularMasteryBook'))
    print(f"\n=== 통계 ===")
    print(f"총 마스터리북: {len(mastery_books)}개")
    print(f"인기 마스터리북: {popular_count}개")
    print(f"몬스터 드랍 테이블 업데이트: {updated_count}개")


if __name__ == "__main__":
    main()

