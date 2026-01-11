#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
특정 아이템을 드롭하는 몬스터의 featuredDropItemIds 필드에 추가합니다.

주요 드랍 아이템:
- 투구민첩주문서
- 일비표창
- 뇌전수리검
- 장갑 공격력 주문서
- 귀장식 지력 주문서
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Set

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


def find_featured_item_ids(items: List[dict]) -> Dict[str, str]:
    """
    주요 드랍 아이템 이름 패턴을 가진 아이템들을 찾아서 ID 매핑 반환
    Returns: {item_id: item_name}
    """
    featured_patterns = [
        r"투구.*민첩.*주문서",
        r"일비.*표창",
        r"뇌전.*수리검",
        r"장갑.*공격력.*주문서",
        r"귀장식.*지력.*주문서",
        r"귀.*장식.*지력.*주문서",
    ]
    
    featured_items: Dict[str, str] = {}
    
    for item in items:
        name = item.get("name", "")
        item_id = item.get("id", "")
        
        for pattern in featured_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                featured_items[item_id] = name
                break
    
    return featured_items


def main():
    item_file = DATA_DIR / "item_data.json"
    monster_file = DATA_DIR / "monster_data.json"
    relations_file = DATA_DIR / "monster_item_relations.json"
    
    items = load_json(item_file)
    monsters = load_json(monster_file)
    relations = load_json(relations_file)
    
    # 주요 드랍 아이템 ID 찾기
    featured_item_ids_map = find_featured_item_ids(items)
    featured_item_ids_set = set(featured_item_ids_map.keys())
    
    print(f"Found {len(featured_item_ids_set)} featured items:")
    for item_id, name in sorted(featured_item_ids_map.items()):
        print(f"  {item_id}: {name}")
    
    # 몬스터별 드롭 아이템 ID 집합 생성 (relations에서)
    monster_drops: Dict[str, Set[str]] = {}
    for rel in relations:
        monster_id = rel.get("monsterId")
        item_id = rel.get("itemId")
        if monster_id and item_id:
            if monster_id not in monster_drops:
                monster_drops[monster_id] = set()
            monster_drops[monster_id].add(item_id)
    
    # 몬스터 데이터 업데이트
    monsters_by_id = {m["id"]: m for m in monsters}
    updated_count = 0
    
    for monster_id, monster in monsters_by_id.items():
        drops = monster_drops.get(monster_id, set())
        
        # 주요 드랍 아이템이 있는지 확인
        featured_drops = drops & featured_item_ids_set
        
        if featured_drops:
            # featuredDropItemIds 필드 추가/업데이트
            current_featured = set(monster.get("featuredDropItemIds") or [])
            new_featured = sorted(list(current_featured | featured_drops), key=lambda x: sort_key_id(x))
            
            if new_featured != (monster.get("featuredDropItemIds") or []):
                monster["featuredDropItemIds"] = new_featured
                updated_count += 1
                print(f"  Updated {monster.get('name', monster_id)}: {new_featured}")
    
    # 정렬 유지
    monsters = list(monsters_by_id.values())
    monsters.sort(key=lambda m: sort_key_id(m["id"]))
    
    save_json(monster_file, monsters)
    
    print(f"\nSummary:")
    print(f"  - Featured items: {len(featured_item_ids_set)}")
    print(f"  - Monsters updated: {updated_count}")
    print(f"  - Total monsters: {len(monsters)}")


if __name__ == "__main__":
    main()
