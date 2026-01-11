#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mapledb.kr에서 몬스터 데이터를 크롤링하여 업데이트합니다.
특히 상세 페이지가 없는 몬스터들(예: 흰 닭)의 stats 정보를 추가합니다.

사용 예시:
    python scripts/parse/update_monsters_from_mapledb.py --monster-id 9420005
    python scripts/parse/update_monsters_from_mapledb.py --monster-ids 9420005,9420006
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import ssl
import time
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "src" / "data"
SCRAPED_DIR_DEFAULT = ROOT_DIR / "src" / "request" / "scraped_monsters" / "mapledb"


BASE_URL = "https://mapledb.kr/search.php"
DETAIL_URL_TEMPLATE = f"{BASE_URL}?q={{monster_id}}&t=mob"


def fetch_html(url: str, timeout: int = 30) -> str:
    """HTML 가져오기"""
    req = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    )
    ctx = ssl.create_default_context()
    with urlopen(req, context=ctx, timeout=timeout) as resp:
        raw = resp.read()
        # UTF-8로 디코딩 시도
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("cp949", "ignore")


def parse_monster_detail_html(html_text: str, monster_id: str) -> Optional[Dict]:
    """
    mapledb.kr HTML에서 몬스터 정보 파싱
    
    반환 형식:
    {
        "level": int,
        "exp": int,
        "hp": int,
        "mp": int (선택적),
        "stats": {
            "physicalDefense": int,
            "magicDefense": int,
            "requiredAccuracy": int,
            "evasion": int (선택적)
        }
    }
    """
    result = {}
    
    # 기본 정보 파싱: LEVEL, EXP, HP, MP
    level_match = re.search(r'<h4>LEVEL</h4>\s*<span>(\d+)</span>', html_text)
    if level_match:
        result["level"] = int(level_match.group(1))
    
    exp_match = re.search(r'<h4>EXP</h4>\s*<span>(\d+)</span>', html_text)
    if exp_match:
        result["exp"] = int(exp_match.group(1))
    
    hp_match = re.search(r'<h4>HP</h4>\s*<span>(\d+)</span>', html_text)
    if hp_match:
        result["hp"] = int(hp_match.group(1))
    
    mp_match = re.search(r'<h4>MP</h4>\s*<span>(\d+)</span>', html_text)
    if mp_match:
        result["mp"] = int(mp_match.group(1))
    
    # 세부 정보 파싱: 물리 방어력, 마법 방어력, 필요 명중률, 회피율
    stats = {}
    
    phys_def_match = re.search(r'<h4>물리 방어력</h4>\s*<span>(\d+)</span>', html_text)
    if phys_def_match:
        stats["physicalDefense"] = int(phys_def_match.group(1))
    
    mag_def_match = re.search(r'<h4>마법 방어력</h4>\s*<span>(\d+)</span>', html_text)
    if mag_def_match:
        stats["magicDefense"] = int(mag_def_match.group(1))
    
    acc_match = re.search(r'<h4>필요 명중률</h4>\s*<span>(\d+)</span>', html_text)
    if acc_match:
        stats["requiredAccuracy"] = int(acc_match.group(1))
    
    eva_match = re.search(r'<h4>회피율</h4>\s*<span>(\d+)</span>', html_text)
    if eva_match:
        stats["evasion"] = int(eva_match.group(1))
    
    if stats:
        result["stats"] = stats
    
    return result if result else None


def load_json(path: Path, default):
    """JSON 파일 로드"""
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    """JSON 파일 저장"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def sort_key_id(id_value: str):
    """ID 정렬 키"""
    try:
        return (0, int(id_value))
    except Exception:
        return (1, id_value)


def update_monster_data(
    monsters: List[Dict],
    monster_id: str,
    parsed_data: Dict,
) -> bool:
    """monster_data.json 업데이트"""
    updated = False
    
    for monster in monsters:
        if monster.get("id") == monster_id:
            # 기본 정보 업데이트 (필요시)
            if "level" in parsed_data and parsed_data["level"] != monster.get("level"):
                print(f"  Updating level: {monster.get('level')} -> {parsed_data['level']}")
                monster["level"] = parsed_data["level"]
                updated = True
            
            if "exp" in parsed_data and parsed_data["exp"] != monster.get("exp"):
                print(f"  Updating exp: {monster.get('exp')} -> {parsed_data['exp']}")
                monster["exp"] = parsed_data["exp"]
                updated = True
            
            if "hp" in parsed_data and parsed_data["hp"] != monster.get("hp"):
                print(f"  Updating hp: {monster.get('hp')} -> {parsed_data['hp']}")
                monster["hp"] = parsed_data["hp"]
                updated = True
            
            # stats 추가/업데이트
            converted_stats = {}
            
            # MP는 stats에 포함
            if "mp" in parsed_data:
                converted_stats["mp"] = parsed_data["mp"]
            
            # stats 파싱 데이터 추가
            if "stats" in parsed_data:
                stats = parsed_data["stats"]
                
                if "physicalDefense" in stats:
                    converted_stats["physicalDefense"] = stats["physicalDefense"]
                
                if "magicDefense" in stats:
                    converted_stats["magicDefense"] = stats["magicDefense"]
                
                if "requiredAccuracy" in stats:
                    converted_stats["requiredAccuracy"] = stats["requiredAccuracy"]
                
                # evasion은 타입 정의에 없으므로 제외
            
            if converted_stats:
                if "stats" not in monster:
                    monster["stats"] = {}
                
                old_stats = monster.get("stats", {})
                for key, value in converted_stats.items():
                    if key not in old_stats or old_stats[key] != value:
                        old_val = old_stats.get(key, "없음")
                        print(f"  Updating stats.{key}: {old_val} -> {value}")
                        monster["stats"][key] = value
                        updated = True
            
            break
    
    return updated


def main():
    parser = argparse.ArgumentParser(description="mapledb.kr에서 몬스터 데이터 크롤링")
    parser.add_argument("--monster-id", type=str, help="단일 몬스터 ID")
    parser.add_argument("--monster-ids", type=str, help="쉼표로 구분된 몬스터 ID 목록")
    parser.add_argument("--delay", type=float, default=2.0, help="각 요청 사이 대기 시간 (초)")
    parser.add_argument("--output-dir", type=Path, default=SCRAPED_DIR_DEFAULT, help="HTML 저장 디렉토리")
    parser.add_argument("--skip-save-html", action="store_true", help="HTML 저장 건너뛰기")
    
    args = parser.parse_args()
    
    # 몬스터 ID 목록 구성
    monster_ids = []
    if args.monster_id:
        monster_ids = [args.monster_id]
    elif args.monster_ids:
        monster_ids = [mid.strip() for mid in args.monster_ids.split(",")]
    else:
        parser.error("--monster-id 또는 --monster-ids를 지정해야 합니다")
    
    # 데이터 파일 로드
    monster_data_file = DATA_DIR / "monster_data.json"
    monsters = load_json(monster_data_file, [])
    
    print(f"Processing {len(monster_ids)} monster(s)...")
    
    updated_count = 0
    not_found_count = 0
    error_count = 0
    
    for i, monster_id in enumerate(monster_ids, 1):
        print(f"\n[{i}/{len(monster_ids)}] Processing monster {monster_id}...")
        
        # 몬스터가 데이터에 있는지 확인
        found = any(m.get("id") == monster_id for m in monsters)
        if not found:
            print(f"  Warning: Monster {monster_id} not found in monster_data.json")
            not_found_count += 1
            continue
        
        # HTML 가져오기
        url = DETAIL_URL_TEMPLATE.format(monster_id=monster_id)
        try:
            html = fetch_html(url)
            
            # HTML 저장
            if not args.skip_save_html:
                html_file = args.output_dir / f"monster_{monster_id}.html"
                html_file.parent.mkdir(parents=True, exist_ok=True)
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"  Saved HTML to {html_file}")
            
            # HTML 파싱
            parsed_data = parse_monster_detail_html(html, monster_id)
            if not parsed_data:
                print(f"  Warning: Failed to parse monster data from HTML")
                error_count += 1
                continue
            
            print(f"  Parsed data: {parsed_data}")
            
            # 데이터 업데이트
            updated = update_monster_data(monsters, monster_id, parsed_data)
            if updated:
                updated_count += 1
                print(f"  [OK] Updated monster {monster_id}")
            else:
                print(f"  [-] No changes needed for monster {monster_id}")
            
            # 대기
            if i < len(monster_ids):
                time.sleep(args.delay)
        
        except Exception as e:
            print(f"  Error processing {monster_id}: {e}")
            error_count += 1
            continue
    
    # 데이터 저장
    if updated_count > 0:
        print(f"\nSaving updated data to {monster_data_file}...")
        save_json(monster_data_file, monsters)
        print(f"[OK] Saved {updated_count} updated monster(s)")
    
    # 결과 요약
    print(f"\n=== Summary ===")
    print(f"Total processed: {len(monster_ids)}")
    print(f"Updated: {updated_count}")
    print(f"Not found: {not_found_count}")
    print(f"Errors: {error_count}")


if __name__ == "__main__":
    main()
