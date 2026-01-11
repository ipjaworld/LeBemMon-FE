#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
크림슨 우드 지역 몬스터 드롭테이블 추가 스크립트

몬스터 이름과 아이템 이름으로 매칭하여 monster_item_relations.json에 관계 추가
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "src" / "data"


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def sort_key_id(id_value: str):
    try:
        return (0, int(id_value))
    except Exception:
        return (1, id_value)


def find_monster_id_by_name(monster_name: str, monster_data: List[Dict]) -> Optional[str]:
    """monster_data.json에서 몬스터 이름으로 ID 찾기"""
    for monster in monster_data:
        if monster.get("name") == monster_name:
            return monster["id"]
    return None


def find_item_id_by_name(item_name: str, item_data: List[Dict]) -> Optional[str]:
    """item_data.json에서 아이템 이름으로 ID 찾기 (부분 일치 포함)"""
    # 정확한 일치 먼저 시도
    for item in item_data:
        if item.get("name") == item_name:
            return item["id"]
    
    # 공백 제거 후 비교
    item_name_no_space = item_name.replace(" ", "")
    for item in item_data:
        name = item.get("name", "")
        name_no_space = name.replace(" ", "")
        if item_name_no_space == name_no_space:
            return item["id"]
    
    # 부분 일치 시도 (아이템 이름에 검색어가 포함되어 있는 경우)
    for item in item_data:
        name = item.get("name", "")
        # 공백 제거 후 부분 일치
        if item_name_no_space in name.replace(" ", "") or name.replace(" ", "") in item_name_no_space:
            return item["id"]
        # 원본으로도 부분 일치
        if item_name in name or name in item_name:
            return item["id"]
    
    return None


def merge_monster_item_relations(
    monster_id: str,
    item_ids: List[str],
    relations: List[Dict],
) -> Tuple[List[Dict], int]:
    """monster_item_relations.json에 관계 추가"""
    # 기존 관계를 (monsterId, itemId) 쌍으로 관리
    relations_set = {(rel["monsterId"], rel["itemId"]) for rel in relations}
    
    added_count = 0
    for item_id in item_ids:
        if item_id and (monster_id, item_id) not in relations_set:
            relations.append({
                "monsterId": monster_id,
                "itemId": item_id,
                # dropRate는 제공되지 않았으므로 추가하지 않음
            })
            relations_set.add((monster_id, item_id))
            added_count += 1
    
    # 정렬: (monsterId, itemId) 순서
    relations.sort(key=lambda x: (sort_key_id(x["monsterId"]), sort_key_id(x["itemId"])))
    
    return relations, added_count


def main():
    # 크림슨 우드 지역 몬스터 드롭테이블 데이터
    # 몬스터 이름은 monster_data.json에 있는 정확한 이름으로 매칭
    crimsonwood_drops = {
        "크림슨 가디언": [  # "크림슨가디언" -> "크림슨 가디언"
            "어드밴스드콤보 20",
            "브랜디쉬 20",
            "파워엘릭서",
        ],
        "나이트섀도우": [  # "나이트쉐도우" -> "나이트섀도우"
            "망토 힘 주문서 60%",
            "퍼플 쉐도우 부츠",
            "골든해머",
        ],
        "티폰": [
            "바키트",
            "레드아르시나",
            "블러드대거",
            "핼버드",
        ],
        "엘더레이스": [
            "돌진 20",
            "마나리플렉션 20",
        ],
        "파이어브랜드": [
            "마기코라스",
            "하트귀고리",
            "낙엽 귀고리",  # "낙엽귀걸이" -> "낙엽 귀고리"
            "수박",
        ],
        "스톰브레이커": [
            "전신갑옷 지력 주문서 60%",
            "창 공격력 주문서 60%",
            "그륜힐",
            "마나엘릭서",
            "엘릭서",
            "파워엘릭서",
            "황룡도",
            "빨간색 수호의 망토",
            "골드드롭 이어링",
            "레드 키튼서클렛",
        ],
        "윈드레이더": [
            "장갑 민첩 주문서 10%",  # "장갑 민첩성 주문서 10%" -> "장갑 민첩 주문서 10%"
            "단검 공격력 주문서 60%",
            "메탈실버 이어링",
            "블루 루티드슈즈",
        ],
        "레프러콘": [
            "에스터실드",
            "뇌전수리검",
            "레드 골드윙캡",
            "그린 피레타햇",
            "초록 두건",
            "딸기 귀고리",
            "블러드 플라티나",
            "다크 잉그리트",
            "다크 크리시아",
            "핑크 루티드 바지",
            "레드문 슈즈",
            "다크 노엘",
            "레이든스태프",
            "크롬",
        ],
        "아기 티폰": [  # "아기티폰" -> "아기 티폰" (확인 필요)
            "님블리스트",
            "파란색 삿갓",
            "빨간색 별 두건",
            "토비표창",
        ],
    }
    
    # 데이터 파일 경로
    monster_data_file = DATA_DIR / "monster_data.json"
    item_data_file = DATA_DIR / "item_data.json"
    relations_file = DATA_DIR / "monster_item_relations.json"
    
    # 기존 데이터 로드
    print("Loading existing data...")
    monster_data = load_json(monster_data_file)
    item_data = load_json(item_data_file)
    relations = load_json(relations_file)
    
    # 통계
    total_relations_added = 0
    monsters_not_found = []
    items_not_found = {}
    
    # 각 몬스터 처리
    for monster_name, item_names in crimsonwood_drops.items():
        print(f"\nProcessing {monster_name}...")
        
        # 몬스터 ID 찾기
        monster_id = find_monster_id_by_name(monster_name, monster_data)
        if not monster_id:
            print(f"  [ERROR] Monster '{monster_name}' not found in monster_data.json")
            monsters_not_found.append(monster_name)
            continue
        
        print(f"  Found monster ID: {monster_id}")
        
        # 각 아이템 ID 찾기
        item_ids = []
        for item_name in item_names:
            item_id = find_item_id_by_name(item_name, item_data)
            if item_id:
                item_ids.append(item_id)
                print(f"    [OK] {item_name} -> {item_id}")
            else:
                print(f"    [NOT FOUND] {item_name}")
                if monster_name not in items_not_found:
                    items_not_found[monster_name] = []
                items_not_found[monster_name].append(item_name)
        
        # 관계 추가
        if item_ids:
            relations, added = merge_monster_item_relations(monster_id, item_ids, relations)
            total_relations_added += added
            print(f"  [OK] Added {added} monster-item relations")
        else:
            print(f"  [WARNING] No items found for {monster_name}")
    
    # 결과 저장
    print("\n" + "=" * 60)
    print("Saving results...")
    save_json(relations_file, relations)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total monster-item relations added: {total_relations_added}")
    print(f"Monsters not found: {len(monsters_not_found)}")
    if monsters_not_found:
        print(f"  - {', '.join(monsters_not_found)}")
    print(f"Items not found: {sum(len(items) for items in items_not_found.values())}")
    if items_not_found:
        for monster_name, items in items_not_found.items():
            print(f"  - {monster_name}: {', '.join(items)}")
    
    print(f"\nOutput file: {relations_file}")


if __name__ == "__main__":
    main()
