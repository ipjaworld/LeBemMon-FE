#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
중복 아이템 "귀 장식 지력 주문서 10%" (2040302)를 제거하고,
monster_item_relations.json에서 해당 아이템 ID를 "귀장식 지력 주문서 10%" (2040046)로 교체합니다.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "src" / "data"
ITEM_DATA_FILE = DATA_DIR / "item_data.json"
RELATIONS_FILE = DATA_DIR / "monster_item_relations.json"

# 삭제할 아이템 ID (중복)
OLD_ITEM_ID = "2040302"
# 유지할 아이템 ID (정상)
NEW_ITEM_ID = "2040046"


def main():
    print("=" * 60)
    print("중복 아이템 제거 작업")
    print(f"삭제 대상: {OLD_ITEM_ID} (귀 장식 지력 주문서 10%)")
    print(f"교체 대상: {NEW_ITEM_ID} (귀장식 지력 주문서 10%)")
    print("=" * 60)
    
    # 1. item_data.json에서 중복 아이템 제거
    print(f"\n[1/2] Reading {ITEM_DATA_FILE}...")
    with open(ITEM_DATA_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)
    
    original_item_count = len(items)
    items_before = [item for item in items if item.get("id") == OLD_ITEM_ID]
    items_after = [item for item in items if item.get("id") != OLD_ITEM_ID]
    
    removed_item_count = original_item_count - len(items_after)
    print(f"  Original items: {original_item_count}")
    print(f"  Removed items: {removed_item_count}")
    
    if items_before:
        print(f"  Removed item: {items_before[0].get('name')} (ID: {OLD_ITEM_ID})")
    
    # 아이템 저장
    with open(ITEM_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items_after, f, ensure_ascii=False, indent=2)
    print(f"  [OK] Saved {ITEM_DATA_FILE}")
    
    # 2. monster_item_relations.json에서 아이템 ID 교체
    print(f"\n[2/2] Reading {RELATIONS_FILE}...")
    with open(RELATIONS_FILE, "r", encoding="utf-8") as f:
        relations = json.load(f)
    
    original_rel_count = len(relations)
    replaced_count = 0
    removed_duplicates = 0
    
    # OLD_ITEM_ID를 사용하는 관계 찾기
    old_relations = [r for r in relations if r.get("itemId") == OLD_ITEM_ID]
    print(f"  Found {len(old_relations)} relations with {OLD_ITEM_ID}")
    
    # 교체된 관계와 중복 제거
    new_relations = []
    seen_keys = set()
    
    for relation in relations:
        item_id = relation.get("itemId")
        monster_id = relation.get("monsterId")
        
        # OLD_ITEM_ID를 NEW_ITEM_ID로 교체
        if item_id == OLD_ITEM_ID:
            item_id = NEW_ITEM_ID
            replaced_count += 1
        
        # 중복 제거 (같은 monsterId-itemId 쌍은 한 번만 추가)
        key = (monster_id, item_id)
        if key in seen_keys:
            removed_duplicates += 1
            continue
        
        seen_keys.add(key)
        new_relation = relation.copy()
        new_relation["itemId"] = item_id
        new_relations.append(new_relation)
    
    # 정렬 (monsterId, itemId 순)
    new_relations.sort(key=lambda r: (
        (0, int(r["monsterId"])) if r["monsterId"].isdigit() else (1, r["monsterId"]),
        (0, int(r["itemId"])) if r["itemId"].isdigit() else (1, r["itemId"])
    ))
    
    print(f"  Original relations: {original_rel_count}")
    print(f"  Replaced relations: {replaced_count}")
    print(f"  Removed duplicates: {removed_duplicates}")
    print(f"  Final relations: {len(new_relations)}")
    
    # 관계 저장
    with open(RELATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(new_relations, f, ensure_ascii=False, indent=2)
    print(f"  [OK] Saved {RELATIONS_FILE}")
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("작업 완료 요약")
    print(f"  - 삭제된 아이템: {removed_item_count}개")
    print(f"  - 교체된 관계: {replaced_count}개")
    print(f"  - 제거된 중복 관계: {removed_duplicates}개")
    print("=" * 60)


if __name__ == "__main__":
    main()
