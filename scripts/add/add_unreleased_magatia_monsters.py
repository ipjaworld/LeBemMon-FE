#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
마가티아 지역의 미출시 몬스터들을 HTML에서 파싱하여 monster_data.json에 추가합니다.
이 몬스터들은 DB에 존재하지만 아직 출시되지 않은 상태입니다 (isReleased: false).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "src" / "data"
SCRAPED_DIR = ROOT_DIR / "src" / "request" / "scraped_monsters" / "magatia"

# 미출시 몬스터 ID 리스트
UNRELEASED_MONSTER_IDS = ["4110301", "5110300", "5110301", "5110302", "7110301"]


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


def parse_monster_html(html_path: Path, monster_id: str) -> Optional[dict]:
    """HTML 파일에서 몬스터 정보를 파싱합니다."""
    if not html_path.exists():
        print(f"  WARNING: HTML file not found: {html_path}")
        return None

    html_text = html_path.read_text(encoding="utf-8")

    # 이름 추출: <h2>태그에서
    name_match = re.search(r'<h2>([^<]+)</h2>', html_text)
    if not name_match:
        print(f"  WARNING: Could not parse name from {html_path}")
        return None
    name = name_match.group(1).strip()

    # 레벨 추출: Lv : 45
    level_match = re.search(r'Lv\s*:\s*(\d+)', html_text)
    level = int(level_match.group(1)) if level_match else None

    # HP 추출: HP : 2550 또는 HP : 15.5K
    hp_match = re.search(r'HP\s*:\s*([\d.]+)\s*K?', html_text)
    if hp_match:
        hp_str = hp_match.group(1)
        try:
            hp_float = float(hp_str)
            # K 단위가 있으면 1000 곱하기 (예: 15.5K -> 15500)
            if 'K' in html_text[hp_match.start():hp_match.end()+10]:  # K가 근처에 있는지 확인
                hp = int(hp_float * 1000)
            else:
                hp = int(hp_float)
        except ValueError:
            hp = None
    else:
        hp = None

    # EXP 추출: EXP : 110
    exp_match = re.search(r'EXP\s*:\s*(\d+)', html_text)
    exp = int(exp_match.group(1)) if exp_match else None

    # 속성 추출: 속성관계 : ... (있는 경우)
    attributes = None
    # 속성관계 패턴이 복잡하므로 일단 None으로 두고, 필요시 나중에 추가

    # 이미지 URL 생성
    image_url = f"https://maplestory.io/api/gms/62/mob/{monster_id}/icon?resize=2"

    monster_data = {
        "id": monster_id,
        "name": name,
        "imageUrl": image_url,
        "isReleased": False,  # 미출시 상태
    }

    if level is not None:
        monster_data["level"] = level
    if hp is not None:
        monster_data["hp"] = hp
    if exp is not None:
        monster_data["exp"] = exp
    if attributes is not None:
        monster_data["attributes"] = attributes

    return monster_data


def main():
    monster_file = DATA_DIR / "monster_data.json"
    monsters = load_json(monster_file)

    monsters_by_id = {m["id"]: m for m in monsters}
    added_count = 0
    updated_count = 0

    for monster_id in UNRELEASED_MONSTER_IDS:
        html_path = SCRAPED_DIR / f"monster_{monster_id}.html"
        print(f"  Parsing {monster_id} from {html_path.name}...")
        parsed_data = parse_monster_html(html_path, monster_id)

        if not parsed_data:
            print(f"    ERROR: Failed to parse {monster_id}")
            continue

        if monster_id in monsters_by_id:
            # 기존 데이터 업데이트 (HP 등이 잘못 파싱된 경우 대비)
            existing = monsters_by_id[monster_id]
            # HP가 명백히 잘못된 경우 (예: 15인데 레벨이 73인 경우) 업데이트
            if parsed_data.get("hp") and existing.get("hp"):
                if parsed_data["hp"] > existing["hp"] * 10:  # 새로 파싱한 HP가 훨씬 큰 경우
                    existing["hp"] = parsed_data["hp"]
                    updated_count += 1
                    print(f"    Updated HP: {existing['name']} (HP {existing['hp']})")
            elif parsed_data.get("hp") and not existing.get("hp"):
                existing["hp"] = parsed_data["hp"]
                updated_count += 1
                print(f"    Added HP: {existing['name']} (HP {existing['hp']})")
            # 기타 필드 업데이트 (없는 경우에만)
            for key in ["level", "exp", "name"]:
                if key in parsed_data and key not in existing:
                    existing[key] = parsed_data[key]
            # isReleased는 항상 False로 유지
            existing["isReleased"] = False
            print(f"    Verified: {existing['name']} (Lv {existing.get('level', '?')}, HP {existing.get('hp', '?')}, EXP {existing.get('exp', '?')})")
        else:
            monsters.append(parsed_data)
            monsters_by_id[monster_id] = parsed_data
            added_count += 1
            print(f"    Added: {parsed_data['name']} (Lv {parsed_data.get('level', '?')}, HP {parsed_data.get('hp', '?')}, EXP {parsed_data.get('exp', '?')})")

    # ID 정렬
    monsters.sort(key=lambda m: sort_key_id(m["id"]))

    save_json(monster_file, monsters)

    print("\n" + "=" * 60)
    print("Summary")
    print(f"  - Monsters added: {added_count}")
    print(f"  - Monsters updated: {updated_count}")
    print(f"  - Total monsters: {len(monsters)}")
    print(f"  - monster_data.json: {monster_file}")


if __name__ == "__main__":
    main()
