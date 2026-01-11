#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사용자가 제공한 HTML 텍스트를 파일로 저장하는 헬퍼 스크립트
stdin에서 HTML을 읽어서 파일로 저장
"""
import sys
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent.parent
REQUEST_DIR = ROOT_DIR / 'src' / 'request'
REQUEST_DIR.mkdir(parents=True, exist_ok=True)

def main():
    if len(sys.argv) > 1:
        # 파일명이 제공된 경우
        filename = sys.argv[1]
        if not filename.endswith('.html'):
            filename += '.html'
        output_file = REQUEST_DIR / filename
    else:
        # 기본 파일명 사용 (타임스탬프 포함)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = REQUEST_DIR / f'user_input_{timestamp}.html'
    
    # stdin에서 HTML 읽기
    html_content = sys.stdin.read()
    
    if not html_content.strip():
        print("Error: No input provided")
        sys.exit(1)
    
    # 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML content saved to: {output_file}")
    print(f"Size: {len(html_content)} characters")
    return str(output_file)

if __name__ == "__main__":
    main()

