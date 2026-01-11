#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메이플노트 사이트에서 아이템 검색 결과를 가져와서 각 상세 페이지를 방문하고
HTML을 추출하여 파싱하는 자동화 스크립트
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
from parse_item_detail import parse_item_detail_from_html, merge_with_existing_data


def extract_item_urls_from_search_page(html_text, base_url):
    """검색 페이지 HTML에서 아이템 상세 페이지 URL 추출"""
    urls = []
    
    # 패턴: <a> 태그에서 href에 item_detail/{id}가 있는 경우
    pattern = r'<a[^>]*href="([^"]*item_detail/(\d+))"[^>]*>'
    matches = re.findall(pattern, html_text)
    
    seen_ids = set()
    for url, item_id in matches:
        if item_id not in seen_ids:
            seen_ids.add(item_id)
            # 상대 URL인 경우 절대 URL로 변환
            if url.startswith('/'):
                full_url = urljoin(base_url, url)
            elif url.startswith('http'):
                full_url = url
            else:
                full_url = urljoin(base_url, '/' + url)
            urls.append((full_url, item_id))
    
    return urls


def scrape_item_details(search_url, output_dir=None, max_items=None, delay=2):
    """
    검색 페이지에서 아이템 목록을 가져와서 각 상세 페이지를 방문하고 데이터를 추출
    
    Args:
        search_url: 검색 결과 페이지 URL
        output_dir: HTML 파일을 저장할 디렉토리 (선택적)
        max_items: 최대 처리할 아이템 수 (None이면 전체)
        delay: 각 페이지 사이 대기 시간 (초)
    """
    # 출력 디렉토리 설정
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Selenium 웹드라이버 설정
    print("Initializing browser...")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창 없이 실행
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        
        # 검색 페이지 방문
        print(f"Visiting search page: {search_url}")
        driver.get(search_url)
        time.sleep(3)  # 페이지 로딩 대기
        
        # 검색 페이지 HTML 가져오기
        search_html = driver.page_source
        
        # 아이템 URL 목록 추출
        base_url = f"{urlparse(search_url).scheme}://{urlparse(search_url).netloc}"
        item_urls = extract_item_urls_from_search_page(search_html, base_url)
        
        print(f"Found {len(item_urls)} items in search results")
        
        if max_items:
            item_urls = item_urls[:max_items]
            print(f"Processing first {max_items} items...")
        
        # 데이터 파일 경로
        output_file = ROOT_DIR / 'src' / 'data' / 'item_data.json'
        
        # 기존 데이터 로드 (한 번만 로드)
        print(f"Loading existing data from: {output_file}")
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_items = json.load(f)
        else:
            existing_items = []
        
        # ID를 키로 하는 딕셔너리 생성
        items_dict = {item['id']: item for item in existing_items}
        
        # 각 아이템 상세 페이지 방문
        processed = 0
        added = 0
        updated = 0
        
        for i, (item_url, item_id) in enumerate(item_urls, 1):
            try:
                print(f"\n[{i}/{len(item_urls)}] Processing item {item_id}...")
                
                # 상세 페이지 방문
                driver.get(item_url)
                time.sleep(delay)  # 페이지 로딩 대기
                
                # HTML 가져오기
                detail_html = driver.page_source
                
                # HTML 파일로 저장 (선택적)
                if output_dir:
                    html_file = output_dir / f"item_{item_id}.html"
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
                    print(f"  Result: Updated")
                else:
                    items_dict[item_id] = item
                    added += 1
                    print(f"  Result: Added")
                
                processed += 1
                
            except Exception as e:
                print(f"  Error processing item {item_id}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # 최종 결과 저장
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
        print(f"  - Total items processed: {processed}")
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
            print("\nBrowser closed.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scrape_item_details.py <search_url> [--output-dir <dir>] [--max-items <n>] [--delay <seconds>]")
        print("\nExample:")
        print("  python scrape_item_details.py 'https://xn--o80b01o9mlw3kdzc.com/itemnote_search?searchInput=주문서'")
        print("  python scrape_item_details.py 'https://xn--o80b01o9mlw3kdzc.com/itemnote_search?searchInput=주문서' --max-items 10 --delay 3")
        sys.exit(1)
    
    search_url = sys.argv[1]
    output_dir = None
    max_items = None
    delay = 2
    
    # 명령줄 인자 파싱
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--output-dir' and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--max-items' and i + 1 < len(sys.argv):
            max_items = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--delay' and i + 1 < len(sys.argv):
            delay = float(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    scrape_item_details(search_url, output_dir, max_items, delay)


if __name__ == "__main__":
    main()
