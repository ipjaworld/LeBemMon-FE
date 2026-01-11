#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
크림슨우드(foundAt=6100, regionId=masteria-crimsonwood) 몬스터 목록을 기반으로:
- monster_detail/{id} 페이지에서
  - STATS 섹션 -> src/data/monster_data.json의 stats 필드 업데이트
  - SPAWN(map_detail/{mapId}) -> src/data/map_data.json의 monsterIds 갱신/추가
  - GET(item_detail/{itemId} + drop-rate-box) -> src/data/monster_item_relations.json 갱신(dropRate 포함)
  - monster_data.json의 regionIds(맵 regionId 기반) 갱신

참고:
- 목록: https://xn--o80b01o9mlw3kdzc.com/monsternote?foundAt=6100
- 상세 예시: https://xn--o80b01o9mlw3kdzc.com/monster_detail/9400573
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
SCRAPED_DIR_DEFAULT = ROOT_DIR / "src" / "request" / "scraped_monsters" / "crimsonwood"

LIST_URL_DEFAULT = "https://xn--o80b01o9mlw3kdzc.com/monsternote?foundAt=6100"
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


def parse_k_value(text: str) -> Optional[float]:
    """K 접미사가 있는 값 파싱 (예: 14.5K -> 14500)"""
    text = text.strip()
    if text.endswith("K") or text.endswith("k"):
        try:
            return float(text[:-1]) * 1000
        except Exception:
            return None
    try:
        return float(text)
    except Exception:
        return None


def parse_plus_value(text: str) -> str | int:
    """+ 접미사가 있는 값 파싱 (예: 1450+ -> "1450+" 또는 1450)"""
    text = text.strip()
    if text.endswith("+") or text.endswith("+"):
        return text  # 문자열로 반환
    try:
        return int(text)
    except Exception:
        try:
            return float(text)
        except Exception:
            return text  # 파싱 실패 시 문자열 반환


def parse_stats_section(html_text: str) -> Optional[Dict]:
    """
    STATS 섹션 파싱
    
    HTML 구조:
    <h2>STATS</h2>
    <span class="hp-box">HP : 100</span>
    <span class="mp-box">MP : 100</span>
    <span class="exp-box">EXP : 10</span>
    <span class="acc">넉백 가능 데미지 : 500+</span>
    ...
    """
    # <h2>STATS</h2> 섹션 찾기
    stats_match = re.search(
        r'<h2[^>]*>STATS</h2>(.*?)(?=<h2|<div[^>]*class="section"|<h1|</body>|\Z)',
        html_text,
        re.DOTALL | re.IGNORECASE
    )
    if not stats_match:
        return None
    
    stats_text = stats_match.group(1)
    stats = {}
    
    # HTML 태그 제거하여 텍스트만 추출
    clean_text = strip_tags(stats_text)
    
    # HP : 14.5K 또는 HP : 14500 형식
    hp_match = re.search(r"HP\s*:\s*([0-9.]+(?:K|k)?)", clean_text, re.IGNORECASE)
    if hp_match:
        hp_value = parse_k_value(hp_match.group(1))
        if hp_value is not None:
            stats["hp"] = int(hp_value)
    
    # MP : 0.15K 또는 MP : 150 형식
    mp_match = re.search(r"MP\s*:\s*([0-9.]+(?:K|k)?)", clean_text, re.IGNORECASE)
    if mp_match:
        mp_value = parse_k_value(mp_match.group(1))
        if mp_value is not None:
            stats["mp"] = int(mp_value)
    
    # EXP : 456 형식
    exp_match = re.search(r"EXP\s*:\s*([0-9.]+(?:K|k)?)", clean_text, re.IGNORECASE)
    if exp_match:
        exp_value = parse_k_value(exp_match.group(1))
        if exp_value is not None:
            stats["exp"] = int(exp_value)
    
    # 넉백 가능 데미지 : 1450+ 형식
    knockback_match = re.search(r"넉백 가능 데미지\s*:\s*([0-9.]+(?:\+)?)", clean_text)
    if knockback_match:
        knockback_value = parse_plus_value(knockback_match.group(1))
        stats["knockbackDamage"] = knockback_value
    
    # 물리 데미지 : 245 형식
    phys_dmg_match = re.search(r"물리 데미지\s*:\s*([0-9.]+)", clean_text)
    if phys_dmg_match:
        try:
            stats["physicalDamage"] = int(float(phys_dmg_match.group(1)))
        except Exception:
            pass
    
    # 마법 데미지 : 0 형식
    mag_dmg_match = re.search(r"마법 데미지\s*:\s*([0-9.]+)", clean_text)
    if mag_dmg_match:
        try:
            stats["magicDamage"] = int(float(mag_dmg_match.group(1)))
        except Exception:
            pass
    
    # 물리 방어력 : 235 형식
    phys_def_match = re.search(r"물리 방어력\s*:\s*([0-9.]+)", clean_text)
    if phys_def_match:
        try:
            stats["physicalDefense"] = int(float(phys_def_match.group(1)))
        except Exception:
            pass
    
    # 마법 방어력 : 245 형식
    mag_def_match = re.search(r"마법 방어력\s*:\s*([0-9.]+)", clean_text)
    if mag_def_match:
        try:
            stats["magicDefense"] = int(float(mag_def_match.group(1)))
        except Exception:
            pass
    
    # 속도 : -20 형식
    speed_match = re.search(r"속도\s*:\s*(-?[0-9.]+)", clean_text)
    if speed_match:
        try:
            stats["speed"] = int(float(speed_match.group(1)))
        except Exception:
            pass
    
    # 레벨 에서의 필요 명중 : 91.65 형식 (소수점 가능)
    acc_match = re.search(r"(\d+)레벨\s*에서의\s*필요\s*명중\s*:\s*([0-9.]+)", clean_text)
    if acc_match:
        try:
            stats["requiredAccuracy"] = float(acc_match.group(2))
        except Exception:
            pass
    
    # 메소 : 525.0 형식
    mesos_match = re.search(r"메소\s*:\s*([0-9.]+)", clean_text)
    if mesos_match:
        try:
            stats["mesos"] = float(mesos_match.group(1))
        except Exception:
            pass
    
    return stats if stats else None


def guess_crimsonwood_region_id_from_map_id(map_id: str) -> str:
    """
    크림슨우드 권역은 대개 61xxxxxxx 형태(예: 610010000)로 관찰될 수 있습니다.
    크림슨우드 도감(foundAt=6100) 컨텍스트에서는 'masteria-crimsonwood'로 귀속시킵니다.
    """
    if map_id.startswith("61"):
        return "masteria-crimsonwood"
    # 일부 특수/이벤트 맵이 섞여도, 크림슨우드 도감(foundAt=6100) 컨텍스트에서는 일단 masteria-crimsonwood로 둠
    return "masteria-crimsonwood"


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
    stats: Optional[Dict]  # STATS 섹션에서 파싱한 정보
    spawn_maps: List[Tuple[str, str]]  # (mapId, mapName)
    drops: List[Tuple[str, Optional[float]]]  # (itemId, dropRate)


def parse_monster_detail_html(html_text: str, monster_id: str) -> ParsedMonsterDetail:
    # STATS 섹션 파싱
    stats = parse_stats_section(html_text)
    
    # SPAWN 맵 파싱
    spawn_maps: List[Tuple[str, str]] = []
    spawn_pattern = re.compile(
        r'href="[^"]*?/map_detail/(\d+)"[^>]*>[\s\S]*?<h3[^>]*>([\s\S]*?)</h3>',
        re.IGNORECASE,
    )
    for map_id, h3_inner in spawn_pattern.findall(html_text):
        name = strip_tags(h3_inner) or f"map-{map_id}"
        spawn_maps.append((map_id, name))

    # GET 드롭 아이템 파싱
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

    return ParsedMonsterDetail(
        monster_id=monster_id,
        stats=stats,
        spawn_maps=unique_spawn,
        drops=unique_drops
    )


def extract_monster_ids(list_html: str) -> List[str]:
    ids = re.findall(r"monster_detail/(\d+)", list_html)
    return sorted(set(ids), key=lambda x: sort_key_id(x))


def merge_monster_stats(
    existing_monsters: List[dict],
    monster_id: str,
    stats: Optional[Dict],
) -> Tuple[List[dict], int]:
    """monster_data.json의 stats 필드 업데이트"""
    monsters_by_id: Dict[str, dict] = {m["id"]: m for m in existing_monsters}
    if monster_id not in monsters_by_id:
        return existing_monsters, 0
    
    if not stats:
        return existing_monsters, 0
    
    monster = monsters_by_id[monster_id]
    if "stats" not in monster:
        monster["stats"] = {}
    
    old_stats = monster["stats"].copy()
    updated = False
    
    # stats 객체 업데이트 (STATS 섹션에서 파싱한 정보)
    # hp, exp는 최상위 레벨 필드이므로 제외
    for key, value in stats.items():
        if key in ("hp", "exp"):
            # hp, exp는 최상위 레벨 필드이므로 비교 후 업데이트
            if key == "hp" and value != monster.get("hp"):
                monster["hp"] = value
                updated = True
            elif key == "exp" and value != monster.get("exp"):
                monster["exp"] = value
                updated = True
        else:
            # 나머지는 stats 객체에 추가
            if key not in old_stats or old_stats[key] != value:
                monster["stats"][key] = value
                updated = True
    
    if updated:
        merged = list(monsters_by_id.values())
        merged.sort(key=lambda x: sort_key_id(x["id"]))
        return merged, 1
    
    return existing_monsters, 0


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
                "regionId": guess_crimsonwood_region_id_from_map_id(map_id),
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
) -> Tuple[List[dict], int, bool]:
    """
    monster_data.json의 regionIds 업데이트.
    Returns: (updated_monsters, updated_count, found_by_id)
    found_by_id가 False이면 ID로 찾지 못한 경우 (이름 매칭 필요할 수 있음)
    """
    monsters_by_id: Dict[str, dict] = {m["id"]: m for m in existing_monsters}
    if monster_id not in monsters_by_id:
        return existing_monsters, 0, False

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
        return merged, 1, True

    return existing_monsters, 0, True


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
    updated_monsters_stats_total = 0
    updated_monsters_region_total = 0
    missing_monster_ids = []

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

        # STATS 업데이트
        monsters, updated_stats = merge_monster_stats(monsters, mid, parsed.stats)
        updated_monsters_stats_total += updated_stats
        if parsed.stats:
            print(f"  Stats: {parsed.stats}")
            if updated_stats:
                print("  [OK] Updated monster stats")

        # 드롭 아이템 관계 업데이트
        relations, added_rel, updated_rel = merge_monster_item_relations(relations, mid, parsed.drops)
        added_rel_total += added_rel
        updated_rel_total += updated_rel
        print(f"  Drops: {len(parsed.drops)} (added rel {added_rel}, updated rel {updated_rel})")

        # 스폰 맵 업데이트
        maps, added_maps, updated_maps = merge_maps(maps, mid, parsed.spawn_maps)
        added_maps_total += added_maps
        updated_maps_total += updated_maps
        print(f"  Spawn maps: {len(parsed.spawn_maps)} (added maps {added_maps}, updated maps {updated_maps})")

        # regionIds 업데이트
        map_by_id = {m["id"]: m for m in maps}
        monsters, updated_region, found_by_id = merge_monster_region_ids(
            monsters,
            mid,
            [m[0] for m in parsed.spawn_maps],
            map_by_id,
        )
        updated_monsters_region_total += updated_region
        if updated_region:
            print("  [OK] Updated monster.regionIds")
        if not found_by_id:
            missing_monster_ids.append(mid)
            print(f"  WARNING: Monster ID {mid} not found in monster_data.json (may need name matching)")

        time.sleep(args.delay)

    save_json(map_file, maps)
    save_json(rel_file, relations)
    save_json(monster_file, monsters)

    print("\n" + "=" * 60)
    print("Summary")
    print(f"  - Monsters processed: {len(monster_ids)}")
    print(f"  - Stats updated: {updated_monsters_stats_total}")
    print(f"  - Relations: +{added_rel_total} / ~{updated_rel_total} (total {len(relations)})")
    print(f"  - Maps: +{added_maps_total} / ~{updated_maps_total} (total {len(maps)})")
    print(f"  - Monsters updated(regionIds): {updated_monsters_region_total}")
    if missing_monster_ids:
        print(f"  - Missing monster IDs (need name matching): {missing_monster_ids}")
    print(f"  - HTML dir: {output_dir}")
    print(f"  - map_data.json: {map_file}")
    print(f"  - monster_item_relations.json: {rel_file}")
    print(f"  - monster_data.json: {monster_file}")


if __name__ == "__main__":
    main()
