#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
지구방위본부(foundAt=2210) 몬스터 목록을 기반으로:
- monster_detail/{id} 페이지에서
  - SPAWN(map_detail/{mapId}) -> src/data/map_data.json의 monsterIds 갱신/추가
  - GET(item_detail/{itemId} + drop-rate-box) -> src/data/monster_item_relations.json 갱신(dropRate 포함)
  - (선택) monster_data.json의 regionIds(맵 regionId 기반) 갱신

참고:
- 목록: https://xn--o80b01o9mlw3kdzc.com/monsternote?foundAt=2210
- 상세 예시: https://xn--o80b01o9mlw3kdzc.com/monster_detail/2230103
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import ssl
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "src" / "data"
SCRAPED_DIR_DEFAULT = ROOT_DIR / "src" / "request" / "scraped_monsters" / "earth-defense-hq"

LIST_URL_DEFAULT = "https://xn--o80b01o9mlw3kdzc.com/monsternote?foundAt=2210"
DETAIL_URL_TEMPLATE = "https://xn--o80b01o9mlw3kdzc.com/monster_detail/{monster_id}"


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    req = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    )
    return urlopen(req, context=ssl.create_default_context(), timeout=timeout).read()


def choose_decode(raw: bytes) -> str:
    candidates = []
    for enc in ("utf-8", "cp949"):
        s = raw.decode(enc, "ignore")
        hangul = sum(1 for ch in s if "\uac00" <= ch <= "\ud7a3")
        candidates.append((hangul, enc, s))
    candidates.sort(reverse=True)
    return candidates[0][2]


def load_json(path: Path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def sort_key_id(id_value: str):
    try:
        return (0, int(id_value))
    except Exception:
        return (1, id_value)


def guess_earth_defense_hq_region_id_from_map_id(map_id: str) -> str:
    """
    지구방위본부 권역은 대개 223xxxxxxx 형태(예: 223010000)로 관찰됨.
    지구방위본부 도감(foundAt=2210) 컨텍스트에서는 'ludus-lake-earth-defense-hq'로 귀속시킵니다.
    (참고: 지구방위본부엔 루디브리엄쪽의 에오스탑 몬스터와 지구방위본부의 몬스터가 섞여있을 수 있음)
    """
    if map_id.startswith("223"):
        return "ludus-lake-earth-defense-hq"
    # 일부 특수/이벤트 맵이 섞여도, 지구방위본부 도감(foundAt=2210) 컨텍스트에서는 일단 ludus-lake-earth-defense-hq로 둠
    return "ludus-lake-earth-defense-hq"


def guess_map_type(map_id: str) -> str:
    if len(map_id) >= 9 and map_id.endswith("000000"):
        return "town"
    return "field"


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = html_lib.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


@dataclass
class ParsedMonsterDetail:
    monster_id: str
    spawn_maps: List[Tuple[str, str]]  # (mapId, mapName)
    drops: List[Tuple[str, Optional[float]]]  # (itemId, dropRate)


def parse_monster_detail_html(html_text: str, monster_id: str) -> ParsedMonsterDetail:
    spawn_maps: List[Tuple[str, str]] = []
    spawn_pattern = re.compile(
        r'href="[^"]*?/map_detail/(\d+)"[^>]*>[\s\S]*?<h3[^>]*>([\s\S]*?)</h3>',
        re.IGNORECASE,
    )
    for map_id, h3_inner in spawn_pattern.findall(html_text):
        name = strip_tags(h3_inner) or f"map-{map_id}"
        spawn_maps.append((map_id, name))

    drops: List[Tuple[str, Optional[float]]] = []
    drop_pattern = re.compile(
        r'href="[^"]*?/item_detail/(\d+)"[^>]*>[\s\S]*?<div class="drop-rate-box">\s*([^<]+?)\s*</div>',
        re.IGNORECASE,
    )
    for item_id, rate_text in drop_pattern.findall(html_text):
        rate_text = rate_text.strip()
        rate: Optional[float]
        try:
            rate = float(rate_text)
        except Exception:
            rate = None
        drops.append((item_id, rate))

    # dedup keep order
    seen_map = set()
    unique_spawn = []
    for mid, mname in spawn_maps:
        if mid in seen_map:
            continue
        seen_map.add(mid)
        unique_spawn.append((mid, mname))

    seen_drop = set()
    unique_drops = []
    for iid, dr in drops:
        if iid in seen_drop:
            continue
        seen_drop.add(iid)
        unique_drops.append((iid, dr))

    return ParsedMonsterDetail(monster_id=monster_id, spawn_maps=unique_spawn, drops=unique_drops)


def extract_monster_ids(list_html: str) -> List[str]:
    ids = re.findall(r"monster_detail/(\d+)", list_html)
    return sorted(set(ids), key=lambda x: sort_key_id(x))


def merge_monster_item_relations(
    existing: List[dict],
    monster_id: str,
    drops: List[Tuple[str, Optional[float]]],
) -> Tuple[List[dict], int, int]:
    by_key: Dict[Tuple[str, str], dict] = {(r["monsterId"], r["itemId"]): r for r in existing}
    added = 0
    updated = 0

    for item_id, rate in drops:
        key = (monster_id, item_id)
        if key in by_key:
            if rate is not None:
                prev = by_key[key].get("dropRate")
                if prev != rate:
                    by_key[key]["dropRate"] = rate
                    updated += 1
        else:
            rel = {"monsterId": monster_id, "itemId": item_id}
            if rate is not None:
                rel["dropRate"] = rate
            by_key[key] = rel
            added += 1

    merged = list(by_key.values())
    merged.sort(key=lambda r: (sort_key_id(r["monsterId"]), sort_key_id(r["itemId"])))
    return merged, added, updated


def merge_maps(
    existing_maps: List[dict],
    monster_id: str,
    spawn_maps: List[Tuple[str, str]],
) -> Tuple[List[dict], int, int]:
    maps_by_id: Dict[str, dict] = {m["id"]: m for m in existing_maps}
    added_maps = 0
    updated_maps = 0

    for map_id, map_name in spawn_maps:
        if map_id in maps_by_id:
            m = maps_by_id[map_id]
            monster_ids = m.get("monsterIds") or []
            if monster_id not in monster_ids:
                monster_ids.append(monster_id)
                m["monsterIds"] = sorted(set(monster_ids), key=lambda x: sort_key_id(x))
                updated_maps += 1
        else:
            new_map = {
                "id": map_id,
                "name": map_name,
                "regionId": guess_earth_defense_hq_region_id_from_map_id(map_id),
                "mapType": guess_map_type(map_id),
                "monsterIds": [monster_id],
                "isReleased": True,
                "imageUrls": {
                    "render": f"https://maplestory.io/api/gms/92/map/{map_id}/render",
                    "minimap": f"https://maplestory.io/api/gms/92/map/{map_id}/minimap",
                    "icon": f"https://maplestory.io/api/gms/92/map/{map_id}/icon",
                },
            }
            maps_by_id[map_id] = new_map
            added_maps += 1

    merged = list(maps_by_id.values())
    merged.sort(key=lambda m: sort_key_id(m["id"]))
    return merged, added_maps, updated_maps


def merge_monster_region_ids(
    existing_monsters: List[dict],
    monster_id: str,
    spawn_map_ids: List[str],
    map_by_id: Dict[str, dict],
) -> Tuple[List[dict], int]:
    monsters_by_id: Dict[str, dict] = {m["id"]: m for m in existing_monsters}
    if monster_id not in monsters_by_id:
        return existing_monsters, 0

    region_ids = set(monsters_by_id[monster_id].get("regionIds") or [])
    for mid in spawn_map_ids:
        m = map_by_id.get(mid)
        if not m:
            continue
        rid = m.get("regionId")
        if rid:
            region_ids.add(rid)

    merged_region_ids = sorted(region_ids)
    prev = monsters_by_id[monster_id].get("regionIds") or []
    if prev != merged_region_ids:
        monsters_by_id[monster_id]["regionIds"] = merged_region_ids
        merged = list(monsters_by_id.values())
        merged.sort(key=lambda x: sort_key_id(x["id"]))
        return merged, 1

    return existing_monsters, 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-url", default=LIST_URL_DEFAULT)
    parser.add_argument("--output-dir", default=str(SCRAPED_DIR_DEFAULT))
    parser.add_argument("--max-monsters", type=int, default=None)
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--skip-save-html", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching list page: {args.list_url}")
    list_raw = fetch_bytes(args.list_url)
    list_html = choose_decode(list_raw)
    monster_ids = extract_monster_ids(list_html)

    if args.max_monsters is not None:
        monster_ids = monster_ids[: args.max_monsters]

    print(f"Found {len(monster_ids)} monster IDs")
    if monster_ids:
        print("Sample:", monster_ids[:10])

    map_file = DATA_DIR / "map_data.json"
    rel_file = DATA_DIR / "monster_item_relations.json"
    monster_file = DATA_DIR / "monster_data.json"

    maps = load_json(map_file, [])
    relations = load_json(rel_file, [])
    monsters = load_json(monster_file, [])

    added_rel_total = 0
    updated_rel_total = 0
    added_maps_total = 0
    updated_maps_total = 0
    updated_monsters_total = 0

    for i, mid in enumerate(monster_ids, 1):
        url = DETAIL_URL_TEMPLATE.format(monster_id=mid)
        print(f"\n[{i}/{len(monster_ids)}] Fetching {mid}: {url}")
        raw = fetch_bytes(url)

        if not args.skip_save_html:
            out = output_dir / f"monster_{mid}.html"
            out.write_bytes(raw)
            print(f"  Saved HTML: {out}")

        html_text = choose_decode(raw)
        parsed = parse_monster_detail_html(html_text, monster_id=mid)

        relations, added_rel, updated_rel = merge_monster_item_relations(relations, mid, parsed.drops)
        added_rel_total += added_rel
        updated_rel_total += updated_rel
        print(f"  Drops: {len(parsed.drops)} (added rel {added_rel}, updated rel {updated_rel})")

        maps, added_maps, updated_maps = merge_maps(maps, mid, parsed.spawn_maps)
        added_maps_total += added_maps
        updated_maps_total += updated_maps
        print(f"  Spawn maps: {len(parsed.spawn_maps)} (added maps {added_maps}, updated maps {updated_maps})")

        map_by_id = {m["id"]: m for m in maps}
        monsters, updated_monsters = merge_monster_region_ids(
            monsters,
            mid,
            [m[0] for m in parsed.spawn_maps],
            map_by_id,
        )
        updated_monsters_total += updated_monsters
        if updated_monsters:
            print("  Updated monster.regionIds")

        time.sleep(args.delay)

    save_json(map_file, maps)
    save_json(rel_file, relations)
    save_json(monster_file, monsters)

    print("\n" + "=" * 60)
    print("Summary")
    print(f"  - Monsters processed: {len(monster_ids)}")
    print(f"  - Relations: +{added_rel_total} / ~{updated_rel_total} (total {len(relations)})")
    print(f"  - Maps: +{added_maps_total} / ~{updated_maps_total} (total {len(maps)})")
    print(f"  - Monsters updated(regionIds): {updated_monsters_total}")
    print(f"  - HTML dir: {output_dir}")
    print(f"  - map_data.json: {map_file}")
    print(f"  - monster_item_relations.json: {rel_file}")


if __name__ == "__main__":
    main()
