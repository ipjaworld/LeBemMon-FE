#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
아이템 상세 페이지 HTML에서 몬스터/NPC 드롭/판매 정보를 추출하는 스크립트
"""
import re
import json
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# 프로젝트 루트 디렉토리
ROOT_DIR = Path(__file__).parent.parent.parent


def extract_monster_relations_from_html(html_text, item_id):
    """HTML에서 몬스터 드롭 정보 추출"""
    relations = []
    
    # BY 섹션 찾기 (몬스터 드롭)
    # 패턴: <a href=".../monster_detail/{monster_id}"> ... <h3>{monster_name}</h3> ...
    monster_pattern = r'<a[^>]*href="[^"]*monster_detail/(\d+)"[^>]*>.*?<h3[^>]*>([^<]+)</h3>'
    monster_matches = re.findall(monster_pattern, html_text, re.DOTALL)
    
    for monster_id, monster_name in monster_matches:
        monster_name = monster_name.strip()
        relations.append({
            "monsterId": monster_id,
            "itemId": item_id
        })
    
    return relations


def extract_npc_relations_from_html(html_text, item_id):
    """HTML에서 NPC 판매 정보 추출 (향후 확장용)"""
    relations = []
    
    # NPC 섹션 찾기
    # 패턴: <h2>NPC</h2> ... <h3>{npc_name}</h3> ...
    # 현재는 NPC 관계를 저장하는 구조가 없으므로 주석 처리
    
    return relations


def merge_relations(new_relations, existing_file_path):
    """기존 monster_item_relations.json과 병합"""
    # 기존 데이터 로드
    if existing_file_path.exists():
        with open(existing_file_path, 'r', encoding='utf-8') as f:
            existing_relations = json.load(f)
    else:
        existing_relations = []
    
    # 관계를 키로 하는 집합 생성 (중복 제거)
    existing_set = set((rel['monsterId'], rel['itemId']) for rel in existing_relations)
    
    # 새로운 관계 추가
    added_count = 0
    for rel in new_relations:
        key = (rel['monsterId'], rel['itemId'])
        if key not in existing_set:
            existing_set.add(key)
            existing_relations.append(rel)
            added_count += 1
    
    return existing_relations, added_count


def parse_html_file(html_file_path, item_id=None):
    """HTML 파일에서 몬스터 관계 추출"""
    html_file = Path(html_file_path)
    
    if not html_file.exists():
        print(f"Error: HTML file not found: {html_file}")
        return None
    
    # 아이템 ID 추출 (파일명에서 또는 파라미터로)
    if not item_id:
        item_id = html_file.stem.replace('item_', '')
    
    # HTML 파일 읽기
    with open(html_file, 'r', encoding='utf-8') as f:
        html_text = f.read()
    
    # 몬스터 관계 추출
    relations = extract_monster_relations_from_html(html_text, item_id)
    
    return relations


def parse_html_directory(html_dir, output_file):
    """디렉토리 내 모든 HTML 파일 파싱"""
    html_dir = Path(html_dir)
    output_file = Path(output_file)
    
    if not html_dir.exists():
        print(f"Error: HTML directory not found: {html_dir}")
        return
    
    # 기존 데이터 로드
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            all_relations = json.load(f)
    else:
        all_relations = []
    
    # HTML 파일 찾기
    html_files = sorted(html_dir.glob('item_*.html'))
    print(f"Found {len(html_files)} HTML files to parse")
    
    total_added = 0
    processed = 0
    
    for html_file in html_files:
        try:
            item_id = html_file.stem.replace('item_', '')
            
            # HTML 파일 읽기
            with open(html_file, 'r', encoding='utf-8') as f:
                html_text = f.read()
            
            # 몬스터 관계 추출
            relations = extract_monster_relations_from_html(html_text, item_id)
            
            if relations:
                # 기존 데이터와 병합
                existing_set = set((rel['monsterId'], rel['itemId']) for rel in all_relations)
                added_count = 0
                for rel in relations:
                    key = (rel['monsterId'], rel['itemId'])
                    if key not in existing_set:
                        existing_set.add(key)
                        all_relations.append(rel)
                        added_count += 1
                
                total_added += added_count
                processed += 1
                
                if processed % 50 == 0:
                    print(f"  Processed {processed}/{len(html_files)} files, added {total_added} relations...")
        
        except Exception as e:
            print(f"  Error processing {html_file.name}: {e}")
            continue
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_relations, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  - HTML files processed: {processed}")
    print(f"  - New relations added: {total_added}")
    print(f"  - Total relations: {len(all_relations)}")
    print(f"  - Output file: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python parse_item_sources.py <html_dir>")
        print("  python parse_item_sources.py <html_file> [item_id]")
        print("\nExamples:")
        print("  # 디렉토리 내 모든 HTML 파일 파싱")
        print("  python parse_item_sources.py src/request/scraped")
        print("\n  # 단일 HTML 파일 파싱")
        print("  python parse_item_sources.py src/request/scraped/item_2040000.html 2040000")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    item_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    output_file = ROOT_DIR / 'src' / 'data' / 'monster_item_relations.json'
    
    if input_path.is_dir():
        # 디렉토리 처리
        parse_html_directory(input_path, output_file)
    else:
        # 단일 파일 처리
        relations = parse_html_file(input_path, item_id)
        
        if relations:
            # 기존 데이터와 병합
            merged_relations, added_count = merge_relations(relations, output_file)
            
            # 결과 저장
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(merged_relations, f, ensure_ascii=False, indent=2)
            
            print(f"\nFound {len(relations)} monster relations")
            print(f"Added {added_count} new relations")
            print(f"Total relations: {len(merged_relations)}")
        else:
            print("No relations found")


if __name__ == "__main__":
    main()
