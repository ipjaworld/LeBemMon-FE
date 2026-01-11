#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2070000 (뇌전 수리검)으로 정의된 관계를 2070005 (뇌전 수리검)로 변경합니다.
"""

from __future__ import annotations

import json
from pathlib import Path

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


def main():
    relations_file = DATA_DIR / "monster_item_relations.json"
    monster_file = DATA_DIR / "monster_data.json"
    
    relations = load_json(relations_file)
    monsters = load_json(monster_file)
    
    # monster_item_relations.json에서 2070000 -> 2070005 변경
    updated_relations = 0
    for rel in relations:
        if rel.get("itemId") == "2070000":
            rel["itemId"] = "2070005"
            updated_relations += 1
    
    # 중복 제거 (같은 monsterId, itemId 쌍)
    seen = set()
    unique_relations = []
    for rel in relations:
        key = (rel["monsterId"], rel["itemId"])
        if key not in seen:
            seen.add(key)
            unique_relations.append(rel)
        elif key in seen:
            # 중복인 경우 dropRate가 더 큰 것을 유지
            for i, existing_rel in enumerate(unique_relations):
                if (existing_rel["monsterId"], existing_rel["itemId"]) == key:
                    existing_rate = existing_rel.get("dropRate")
                    new_rate = rel.get("dropRate")
                    if new_rate is not None and (existing_rate is None or new_rate > existing_rate):
                        unique_relations[i] = rel
                    break
    
    # 정렬
    unique_relations.sort(key=lambda r: (sort_key_id(r["monsterId"]), sort_key_id(r["itemId"])))
    
    # monster_data.json에서 featuredDropItemIds의 2070000 -> 2070005 변경
    updated_monsters = 0
    for monster in monsters:
        featured = monster.get("featuredDropItemIds")
        if featured and "2070000" in featured:
            featured = [item_id if item_id != "2070000" else "2070005" for item_id in featured]
            # 중복 제거 후 정렬
            featured = sorted(list(set(featured)), key=lambda x: sort_key_id(x))
            monster["featuredDropItemIds"] = featured
            updated_monsters += 1
        
        drop_item_ids = monster.get("dropItemIds")
        if drop_item_ids and "2070000" in drop_item_ids:
            drop_item_ids = [item_id if item_id != "2070000" else "2070005" for item_id in drop_item_ids]
            # 중복 제거 후 정렬
            drop_item_ids = sorted(list(set(drop_item_ids)), key=lambda x: sort_key_id(x))
            monster["dropItemIds"] = drop_item_ids
            updated_monsters += 1
    
    # 저장
    save_json(relations_file, unique_relations)
    save_json(monster_file, monsters)
    
    print(f"Summary:")
    print(f"  - Relations updated: {updated_relations}")
    print(f"  - Relations after dedup: {len(unique_relations)}")
    print(f"  - Monsters updated: {updated_monsters}")
    print(f"  - monster_item_relations.json: {relations_file}")
    print(f"  - monster_data.json: {monster_file}")


if __name__ == "__main__":
    main()
