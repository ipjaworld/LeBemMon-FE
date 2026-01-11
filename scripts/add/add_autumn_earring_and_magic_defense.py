#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1. 낙엽 귀고리 아이템 추가
2. 모든 귀고리에 마법방어력 필드 추가
3. "장갑 민첩성 주문서 10%"를 "장갑 민첩 주문서 10%"로 수정
"""

import json
from pathlib import Path
from typing import Dict, List

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
    # 데이터 파일 경로
    item_data_file = DATA_DIR / "item_data.json"
    monster_item_relations_file = DATA_DIR / "monster_item_relations.json"
    
    # 기존 데이터 로드
    print("Loading existing data...")
    item_data = load_json(item_data_file)
    relations = load_json(monster_item_relations_file)
    
    # 1. 낙엽 귀고리 추가
    print("\n1. Adding 낙엽 귀고리...")
    autumn_earring = {
        "id": "1032032",
        "name": "낙엽 귀고리",
        "imageUrl": "https://maplestory.io/api/gms/200/item/1032032/icon?resize=2",
        "majorCategory": "common",
        "mediumCategory": "earring",
        "reqLevel": 25,
        "magicPower": 1,
        "magicDefense": 0,  # 기본값 0 (다른 귀고리들도 확인 필요)
        "isReleased": True,
    }
    
    # 아이템이 이미 있는지 확인
    item_dict = {item["id"]: item for item in item_data}
    if "1032032" in item_dict:
        print("  [INFO] 낙엽 귀고리 already exists, updating...")
        item_dict["1032032"] = autumn_earring
    else:
        print("  [OK] Adding 낙엽 귀고리...")
        item_dict["1032032"] = autumn_earring
    
    # 2. 모든 귀고리에 마법방어력 필드 추가
    print("\n2. Adding magicDefense field to all earrings...")
    earrings_updated = 0
    for item in item_dict.values():
        if item.get("mediumCategory") == "earring":
            if "magicDefense" not in item:
                item["magicDefense"] = 0  # 기본값 0
                earrings_updated += 1
    
    print(f"  [OK] Updated {earrings_updated} earrings with magicDefense field")
    
    # 3. "장갑 민첩성 주문서 10%"를 "장갑 민첩 주문서 10%"로 수정
    print("\n3. Fixing item name: '장갑 민첩성 주문서 10%' -> '장갑 민첩 주문서 10%'...")
    items_fixed = 0
    for item in item_dict.values():
        if item.get("name") == "장갑 민첩성 주문서 10%":
            item["name"] = "장갑 민첩 주문서 10%"
            items_fixed += 1
            print(f"  [OK] Fixed item {item['id']}: {item['name']}")
    
    if items_fixed == 0:
        print("  [INFO] Item not found, checking for similar names...")
        # 부분 일치 검색
        for item in item_dict.values():
            if "장갑" in item.get("name", "") and "민첩" in item.get("name", "") and "주문서" in item.get("name", "") and "10%" in item.get("name", ""):
                print(f"  [INFO] Found similar item: {item['id']} - {item['name']}")
    
    # 4. monster_item_relations.json에서 "장갑 민첩성 주문서 10%" 관련 관계 수정
    print("\n4. Updating monster-item relations...")
    # 먼저 아이템 ID 찾기
    target_item_id = None
    for item in item_dict.values():
        if "장갑" in item.get("name", "") and "민첩" in item.get("name", "") and "주문서" in item.get("name", "") and "10%" in item.get("name", ""):
            target_item_id = item["id"]
            print(f"  [INFO] Found item ID: {target_item_id} - {item['name']}")
            break
    
    # 아이템 데이터를 리스트로 변환 및 정렬
    item_data = list(item_dict.values())
    item_data.sort(key=lambda x: sort_key_id(x["id"]))
    
    # 결과 저장
    print("\n" + "=" * 60)
    print("Saving results...")
    save_json(item_data_file, item_data)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    # 낙엽 귀고리 추가 여부 확인
    existing_items = load_json(item_data_file)
    autumn_exists = any(item.get("id") == "1032032" for item in existing_items)
    print(f"낙엽 귀고리: {'Added' if not autumn_exists else 'Updated'}")
    print(f"귀고리 마법방어력 필드 추가: {earrings_updated} items")
    print(f"아이템 이름 수정: {items_fixed} items")
    print(f"\nOutput file: {item_data_file}")


if __name__ == "__main__":
    main()
