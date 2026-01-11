#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
검색 결과 페이지에서 아이템 개수를 확인하는 간단한 스크립트
"""
import sys
import time
from urllib.parse import urljoin, urlparse
import re

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("Error: selenium is not installed. Please install it with: pip install selenium")
    sys.exit(1)


def count_items_in_search_page(search_url):
    """검색 페이지에서 아이템 개수를 확인"""
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
        
        html = driver.page_source
        
        # 아이템 URL 패턴 찾기
        pattern = r'<a[^>]*href="[^"]*item_detail/(\d+)"[^>]*>'
        matches = re.findall(pattern, html)
        
        unique_ids = set(matches)
        count = len(unique_ids)
        
        print(f"\nFound {count} unique items in search results")
        print(f"First 10 IDs: {list(unique_ids)[:10]}")
        
        return count, list(unique_ids)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_search_results.py <search_url>")
        sys.exit(1)
    
    search_url = sys.argv[1]
    count_items_in_search_page(search_url)
