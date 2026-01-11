#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메이플 이어링(1단계, 2단계, 3단계)은 몬스터에게 드롭되지 않는 아이템이므로
monster_item_relations.json에서 모든 관계를 제거합니다.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
RELATIONS_FILE = ROOT_DIR / "src" / "data" / "monster_item_relations.json"

# 메이플 이어링 아이템 ID 목록
MAPLE_EARRING_IDS = ["1032040", "1032041", "1032042"]


def main():
    print(f"Reading {RELATIONS_FILE}...")
    with open(RELATIONS_FILE, "r", encoding="utf-8") as f:
        relations = json.load(f)

    original_count = len(relations)
    print(f"Original relations count: {original_count}")

    # 메이플 이어링 관계 필터링
    filtered_relations = [
        rel
        for rel in relations
        if rel.get("itemId") not in MAPLE_EARRING_IDS
    ]

    removed_count = original_count - len(filtered_relations)
    print(f"Removed relations: {removed_count}")
    print(f"Remaining relations count: {len(filtered_relations)}")

    # 제거된 관계 상세 정보 출력
    if removed_count > 0:
        print("\nRemoved relations:")
        for rel in relations:
            if rel.get("itemId") in MAPLE_EARRING_IDS:
                print(f"  - Monster {rel.get('monsterId')} -> Item {rel.get('itemId')}")

    # JSON 저장 (정렬 유지)
    print(f"\nSaving to {RELATIONS_FILE}...")
    with open(RELATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(filtered_relations, f, ensure_ascii=False, indent=2)

    print("Done!")


if __name__ == "__main__":
    main()
