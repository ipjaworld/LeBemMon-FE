#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
빅토리아 아일랜드(foundAt=10) 몬스터 목록을 기반으로:
- monster_detail/{id} 페이지에서
  - SPAWN(map_detail/{mapId}) -> src/data/map_data.json의 monsterIds 갱신/추가
  - GET(item_detail/{itemId} + drop-rate-box) -> src/data/monster_item_relations.json 갱신(dropRate 포함)
  - (선택) monster_data.json의 regionIds(맵 regionId 기반) 갱신

참고 사이트:
- https://xn--o80b01o9mlw3kdzc.com/monsternote?foundAt=10
- https://xn--o80b01o9mlw3kdzc.com/monster_detail/{monsterId}
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
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "src" / "data"
SCRAPED_DIR_DEFAULT = ROOT_DIR / "src" / "request" / "scraped_monsters" / "victoria"


LIST_URL_DEFAULT = "https://xn--o80b01o9mlw3kdzc.com/monsternote?foundAt=10"
DETAIL_URL_TEMPLATE = "https://xn--o80b01o9mlw3kdzc.com/monster_detail/{monster_id}"


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    return urlopen(req, context=ssl.create_default_context(), timeout=timeout).read()


def choose_decode(raw: bytes) -> str:
    """
    사이트가 UTF-8로 선언되어 있어도, 실제 바이트가 CP949 계열로 오는 경우가 있어
    (특히 윈도 환경) 한글 글자 수가 더 많은 디코딩 결과를 채택합니다.
    """
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


def guess_region_id_from_map_id(map_id: str) -> str:
    """
    최소한의 휴리스틱: 빅토리아 섬 범위에서 mapId 접두어로 town(region) 매핑.
    정확도는 100%가 아니므로, 모르는 경우는 'victoria'로 두어 UI가 깨지지 않게 합니다.
    """
    # 9자리 미만(예: 메이플 아일랜드)은 town-prefix 휴리스틱을 적용하면 오판이 잦아
    # 우선 상위 지역(victoria)로만 귀속시켜 UI 표시가 망가지지 않게 합니다.
    if len(map_id) < 9:
        return "victoria"

    if map_id.startswith("100"):
        return "victoria-henesys"
    if map_id.startswith("101"):
        return "victoria-ellinia"
    if map_id.startswith("102"):
        return "victoria-perion"
    if map_id.startswith("103"):
        return "victoria-kerning"
    if map_id.startswith("104"):
        return "victoria-lith"
    if map_id.startswith("105"):
        return "victoria-sleepywood"
    if map_id.startswith("110"):
        return "victoria-florina"
    return "victoria"


def guess_map_type(map_id: str) -> str:
    # 9자리 맵 중 xxx000000 형태는 보통 마을/허브인 경우가 많음
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
    # SPAWN: map_detail/{id} + h3 text (after img)
    spawn_maps: List[Tuple[str, str]] = []
    spawn_pattern = re.compile(
        r'href="[^"]*?/map_detail/(\d+)"[^>]*>[\s\S]*?<h3[^>]*>([\s\S]*?)</h3>',
        re.IGNORECASE,
    )
    for map_id, h3_inner in spawn_pattern.findall(html_text):
        name = strip_tags(h3_inner)
        if not name:
            name = f"map-{map_id}"
        spawn_maps.append((map_id, name))

    # GET: item_detail/{id} + drop-rate-box
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

    # dedup while keeping order
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
        key = (iid,)
        if key in seen_drop:
            continue
        seen_drop.add(key)
        unique_drops.append((iid, dr))

    return ParsedMonsterDetail(monster_id=monster_id, spawn_maps=unique_spawn, drops=unique_drops)


def extract_victoria_monster_ids(list_html: str) -> List[str]:
    ids = re.findall(r"monster_detail/(\d+)", list_html)
    unique = sorted(set(ids), key=lambda x: sort_key_id(x))
    return unique


def merge_monster_item_relations(
    existing: List[dict],
    monster_id: str,
    drops: List[Tuple[str, Optional[float]]],
) -> Tuple[List[dict], int, int]:
    """
    key: (monsterId, itemId)
    - 존재하면 dropRate 갱신(새 값이 있으면 덮어쓰기)
    - 없으면 추가
    """
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
    """
    map_data.json 병합:
    - map이 존재하면 monsterIds에 monster_id 추가
    - map이 없으면 minimal map 객체 생성 후 추가
    """
    maps_by_id: Dict[str, dict] = {m["id"]: m for m in existing_maps}
    added_maps = 0
    updated_maps = 0

    for map_id, map_name in spawn_maps:
        if map_id in maps_by_id:
            m = maps_by_id[map_id]
            # 이전 버전 휴리스틱으로 9자리 미만 맵이 victoria-* town으로 잘못 분류된 경우 보정
            if len(map_id) < 9 and isinstance(m.get("regionId"), str) and m["regionId"].startswith("victoria-"):
                m["regionId"] = "victoria"
                updated_maps += 1

            monster_ids = m.get("monsterIds") or []
            if monster_id not in monster_ids:
                monster_ids.append(monster_id)
                m["monsterIds"] = sorted(set(monster_ids), key=lambda x: sort_key_id(x))
                updated_maps += 1
        else:
            new_map = {
                "id": map_id,
                "name": map_name,
                "regionId": guess_region_id_from_map_id(map_id),
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
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--skip-save-html", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching list page: {args.list_url}")
    list_raw = fetch_bytes(args.list_url)
    list_html = choose_decode(list_raw)
    monster_ids = extract_victoria_monster_ids(list_html)

    if args.max_monsters is not None:
        monster_ids = monster_ids[: args.max_monsters]

    print(f"Found {len(monster_ids)} monster IDs")
    if monster_ids:
        print("Sample:", monster_ids[:10])

    # load existing data
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

        # save raw HTML for reproducibility
        if not args.skip_save_html:
            out = output_dir / f"monster_{mid}.html"
            out.write_bytes(raw)
            print(f"  Saved HTML: {out}")

        html_text = choose_decode(raw)
        parsed = parse_monster_detail_html(html_text, monster_id=mid)

        # merge relations
        relations, added_rel, updated_rel = merge_monster_item_relations(relations, mid, parsed.drops)
        added_rel_total += added_rel
        updated_rel_total += updated_rel
        print(f"  Drops: {len(parsed.drops)} (added rel {added_rel}, updated rel {updated_rel})")

        # merge maps
        maps, added_maps, updated_maps = merge_maps(maps, mid, parsed.spawn_maps)
        added_maps_total += added_maps
        updated_maps_total += updated_maps
        print(f"  Spawn maps: {len(parsed.spawn_maps)} (added maps {added_maps}, updated maps {updated_maps})")

        # update monster regionIds (optional but useful)
        map_by_id = {m['id']: m for m in maps}
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

    # save outputs
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

