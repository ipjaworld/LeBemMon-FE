#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2040045 (장갑 공격력 주문서 60%)를 2040804 (장갑 공격력 주문서 60%)로 통일합니다.
2040045 아이템을 삭제하고 모든 참조를 2040804로 변경합니다.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "src" / "data"

OLD_ITEM_ID = "2040045"
NEW_ITEM_ID = "2040804"


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
    item_file = DATA_DIR / "item_data.json"
    
    relations = load_json(relations_file)
    monsters = load_json(monster_file)
    items = load_json(item_file)
    
    # 1. item_data.json에서 2040045 아이템 삭제
    items_before = len(items)
    items = [item for item in items if item.get("id") != OLD_ITEM_ID]
    items_after = len(items)
    deleted_items = items_before - items_after
    
    # 정렬
    items.sort(key=lambda i: sort_key_id(i.get("id", "")))
    
    # 2. monster_item_relations.json에서 2040045 -> 2040804 변경
    updated_relations = 0
    for rel in relations:
        if rel.get("itemId") == OLD_ITEM_ID:
            rel["itemId"] = NEW_ITEM_ID
            updated_relations += 1
    
    # 중복 제거 (같은 monsterId, itemId 쌍)
    seen = set()
    unique_relations = []
    for rel in relations:
        key = (rel["monsterId"], rel["itemId"])
        if key not in seen:
            seen.add(key)
            unique_relations.append(rel)
        else:
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
    
    # 3. monster_data.json에서 featuredDropItemIds와 dropItemIds의 2040045 -> 2040804 변경
    updated_monsters = 0
    for monster in monsters:
        featured = monster.get("featuredDropItemIds")
        if featured and OLD_ITEM_ID in featured:
            featured = [item_id if item_id != OLD_ITEM_ID else NEW_ITEM_ID for item_id in featured]
            # 중복 제거 후 정렬
            featured = sorted(list(set(featured)), key=lambda x: sort_key_id(x))
            monster["featuredDropItemIds"] = featured
            updated_monsters += 1
        
        drop_item_ids = monster.get("dropItemIds")
        if drop_item_ids and OLD_ITEM_ID in drop_item_ids:
            drop_item_ids = [item_id if item_id != OLD_ITEM_ID else NEW_ITEM_ID for item_id in drop_item_ids]
            # 중복 제거 후 정렬
            drop_item_ids = sorted(list(set(drop_item_ids)), key=lambda x: sort_key_id(x))
            monster["dropItemIds"] = drop_item_ids
            updated_monsters += 1
    
    # 저장
    save_json(relations_file, unique_relations)
    save_json(monster_file, monsters)
    save_json(item_file, items)
    
    print(f"Summary:")
    print(f"  - Items deleted: {deleted_items}")
    print(f"  - Relations updated: {updated_relations}")
    print(f"  - Relations after dedup: {len(unique_relations)}")
    print(f"  - Monsters updated: {updated_monsters}")
    print(f"  - item_data.json: {item_file}")
    print(f"  - monster_item_relations.json: {relations_file}")
    print(f"  - monster_data.json: {monster_file}")


if __name__ == "__main__":
    main()
