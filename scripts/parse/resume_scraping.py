#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
중단된 크롤링을 재개하거나 저장된 HTML 파일들을 다시 파싱하는 스크립트
"""
import re
import json
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("Error: selenium is not installed. Please install it with: pip install selenium")
    sys.exit(1)

# 프로젝트 루트 디렉토리
ROOT_DIR = Path(__file__).parent.parent.parent

# 상세 페이지 파싱 함수 임포트
sys.path.insert(0, str(ROOT_DIR / 'scripts' / 'parse'))
from parse_item_detail import parse_item_detail_from_html


def extract_item_urls_from_search_page(html_text, base_url):
    """검색 페이지 HTML에서 아이템 상세 페이지 URL 추출"""
    urls = []
    
    pattern = r'<a[^>]*href="([^"]*item_detail/(\d+))"[^>]*>'
    matches = re.findall(pattern, html_text)
    
    seen_ids = set()
    for url, item_id in matches:
        if item_id not in seen_ids:
            seen_ids.add(item_id)
            if url.startswith('/'):
                full_url = urljoin(base_url, url)
            elif url.startswith('http'):
                full_url = url
            else:
                full_url = urljoin(base_url, '/' + url)
            urls.append((full_url, item_id))
    
    return urls


def parse_saved_html_files(html_dir, output_file, skip_existing=True):
    """저장된 HTML 파일들을 파싱하여 데이터 업데이트"""
    html_dir = Path(html_dir)
    if not html_dir.exists():
        print(f"Error: HTML directory not found: {html_dir}")
        return
    
    # 기존 데이터 로드
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_items = json.load(f)
    else:
        existing_items = []
    
    items_dict = {item['id']: item for item in existing_items}
    
    # HTML 파일 찾기
    html_files = sorted(html_dir.glob('item_*.html'))
    print(f"Found {len(html_files)} HTML files to parse")
    
    processed = 0
    updated = 0
    failed = 0
    
    for html_file in html_files:
        try:
            # 아이템 ID 추출
            item_id = html_file.stem.replace('item_', '')
            
            # 기존 데이터 확인 (skip_existing 옵션)
            if skip_existing and item_id in items_dict:
                existing_item = items_dict[item_id]
                # 이름이 깨져있지 않으면 스킵
                if existing_item.get('name') and 'Ŭ' not in existing_item.get('name', '') and 'ĸ' not in existing_item.get('name', ''):
                    continue
            
            # HTML 파일 읽기
            with open(html_file, 'r', encoding='utf-8') as f:
                html_text = f.read()
            
            # HTML 파싱
            item = parse_item_detail_from_html(html_text, item_id)
            
            if not item:
                print(f"  Warning: Failed to parse {html_file.name}")
                failed += 1
                continue
            
            # 데이터 병합
            items_dict[item_id] = item
            updated += 1
            processed += 1
            
            if processed % 50 == 0:
                print(f"  Processed {processed}/{len(html_files)} files...")
                
        except Exception as e:
            print(f"  Error processing {html_file.name}: {e}")
            failed += 1
            continue
    
    # 결과 저장
    merged_items = list(items_dict.values())
    
    # ID로 정렬
    def sort_key(item):
        item_id = item['id']
        try:
            return (0, int(item_id))
        except ValueError:
            return (1, item_id)
    
    merged_items.sort(key=sort_key)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_items, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  - HTML files processed: {processed}")
    print(f"  - Updated: {updated}")
    print(f"  - Failed: {failed}")
    print(f"  - Output file: {output_file}")


def resume_scraping_from_checkpoint(search_url, html_dir, output_file, delay=2):
    """크롤링을 재개 (저장된 HTML 파일과 비교하여 누락된 것만 크롤링)"""
    html_dir = Path(html_dir)
    output_file = Path(output_file)
    
    # 기존 HTML 파일들 확인
    existing_html_ids = set()
    if html_dir.exists():
        for html_file in html_dir.glob('item_*.html'):
            item_id = html_file.stem.replace('item_', '')
            existing_html_ids.add(item_id)
        print(f"Found {len(existing_html_ids)} existing HTML files")
    
    # 검색 페이지에서 전체 아이템 목록 가져오기
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        
        print(f"Visiting search page: {search_url}")
        driver.get(search_url)
        time.sleep(3)
        
        search_html = driver.page_source
        base_url = f"{urlparse(search_url).scheme}://{urlparse(search_url).netloc}"
        item_urls = extract_item_urls_from_search_page(search_html, base_url)
        
        print(f"Found {len(item_urls)} items in search results")
        
        # 누락된 아이템 찾기
        missing_items = [(url, item_id) for url, item_id in item_urls if item_id not in existing_html_ids]
        
        if not missing_items:
            print("All items already scraped. Use --reparse-html to reparse existing HTML files.")
            return
        
        print(f"Found {len(missing_items)} missing items to scrape")
        
        # 기존 데이터 로드
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_items = json.load(f)
        else:
            existing_items = []
        
        items_dict = {item['id']: item for item in existing_items}
        html_dir.mkdir(parents=True, exist_ok=True)
        
        # 누락된 아이템 크롤링
        processed = 0
        added = 0
        updated = 0
        
        for i, (item_url, item_id) in enumerate(missing_items, 1):
            try:
                print(f"\n[{i}/{len(missing_items)}] Processing item {item_id}...")
                
                driver.get(item_url)
                time.sleep(delay)
                
                detail_html = driver.page_source
                
                # HTML 파일 저장
                html_file = html_dir / f"item_{item_id}.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(detail_html)
                print(f"  Saved HTML to: {html_file}")
                
                # HTML 파싱
                item = parse_item_detail_from_html(detail_html, item_id)
                
                if not item:
                    print(f"  Warning: Failed to parse item {item_id}")
                    continue
                
                print(f"  Parsed: {item['name']}")
                
                # 데이터 병합
                if item_id in items_dict:
                    items_dict[item_id] = item
                    updated += 1
                else:
                    items_dict[item_id] = item
                    added += 1
                
                processed += 1
                
            except Exception as e:
                print(f"  Error processing item {item_id}: {e}")
                continue
        
        # 최종 결과 저장
        merged_items = list(items_dict.values())
        
        def sort_key(item):
            item_id = item['id']
            try:
                return (0, int(item_id))
            except ValueError:
                return (1, item_id)
        
        merged_items.sort(key=sort_key)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_items, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  - Items processed: {processed}")
        print(f"  - Added: {added}")
        print(f"  - Updated: {updated}")
        print(f"  - Output file: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python resume_scraping.py --reparse-html <html_dir> [--skip-existing]")
        print("  python resume_scraping.py --resume <search_url> <html_dir> [--delay <seconds>]")
        print("\nExamples:")
        print("  # 저장된 HTML 파일들을 다시 파싱")
        print("  python resume_scraping.py --reparse-html src/request/scraped")
        print("\n  # 누락된 아이템만 크롤링")
        print("  python resume_scraping.py --resume 'https://...' src/request/scraped")
        sys.exit(1)
    
    output_file = ROOT_DIR / 'src' / 'data' / 'item_data.json'
    
    if sys.argv[1] == '--reparse-html':
        html_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        if not html_dir:
            print("Error: HTML directory required")
            sys.exit(1)
        
        skip_existing = '--skip-existing' in sys.argv
        parse_saved_html_files(html_dir, output_file, skip_existing)
        
    elif sys.argv[1] == '--resume':
        if len(sys.argv) < 4:
            print("Error: search_url and html_dir required")
            sys.exit(1)
        
        search_url = sys.argv[2]
        html_dir = Path(sys.argv[3])
        delay = 2
        
        if '--delay' in sys.argv:
            idx = sys.argv.index('--delay')
            if idx + 1 < len(sys.argv):
                delay = float(sys.argv[idx + 1])
        
        resume_scraping_from_checkpoint(search_url, html_dir, output_file, delay)
    else:
        print("Error: Unknown option. Use --reparse-html or --resume")
        sys.exit(1)


if __name__ == "__main__":
    main()
