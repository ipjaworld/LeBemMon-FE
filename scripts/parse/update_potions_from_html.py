#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 파일에서 포션 아이템의 몬스터 드롭 정보를 파싱하여 monster_item_relations.json에 추가

사용법:
    python scripts/parse/update_potions_from_html.py --html-file src/request/white_potion.html --item-id 2000002
"""

import argparse
import json
import re
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


def extract_monster_ids_from_html(html_file: Path) -> List[str]:
    """HTML 파일에서 몬스터 ID 추출"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_text = f.read()
    
    # monster_detail/{id} 패턴으로 몬스터 ID 추출
    pattern = r'monster_detail/(\d+)'
    monster_ids = re.findall(pattern, html_text)
    
    # 중복 제거 및 정렬
    unique_ids = sorted(set(monster_ids), key=lambda x: sort_key_id(x))
    return unique_ids


def merge_monster_item_relations(
    item_id: str,
    monster_ids: List[str],
    relations: List[Dict],
) -> Tuple[List[Dict], int]:
    """monster_item_relations.json에 관계 추가"""
    # 기존 관계를 (monsterId, itemId) 쌍으로 관리
    relations_set = {(rel["monsterId"], rel["itemId"]) for rel in relations}
    
    added_count = 0
    for monster_id in monster_ids:
        if (monster_id, item_id) not in relations_set:
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
    parser = argparse.ArgumentParser(description="HTML 파일에서 포션 아이템 드롭 정보 업데이트")
    parser.add_argument(
        "--html-file",
        type=str,
        required=True,
        help="HTML 파일 경로",
    )
    parser.add_argument(
        "--item-id",
        type=str,
        required=True,
        help="아이템 ID",
    )
    
    args = parser.parse_args()
    
    html_file = Path(args.html_file)
    item_id = args.item_id
    
    if not html_file.exists():
        print(f"Error: HTML file not found: {html_file}")
        return 1
    
    # 데이터 파일 경로
    relations_file = DATA_DIR / "monster_item_relations.json"
    
    # 기존 데이터 로드
    print("Loading existing data...")
    relations = load_json(relations_file)
    
    # HTML 파일에서 몬스터 ID 추출
    print(f"Extracting monster IDs from {html_file}...")
    monster_ids = extract_monster_ids_from_html(html_file)
    print(f"Found {len(monster_ids)} monsters")
    
    # 관계 추가
    relations, added = merge_monster_item_relations(item_id, monster_ids, relations)
    
    # 결과 저장
    print("\n" + "=" * 60)
    print("Saving results...")
    save_json(relations_file, relations)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Item ID: {item_id}")
    print(f"Total monsters found: {len(monster_ids)}")
    print(f"Monster-item relations added: {added}")
    print(f"Output file: {relations_file}")
    
    return 0


if __name__ == "__main__":
    exit(main())
