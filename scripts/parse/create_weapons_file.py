#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사용자가 처음에 제공한 전체 HTML 텍스트(9개 카테고리)를 파일로 저장하는 스크립트
"""
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
OUTPUT_FILE = ROOT_DIR / 'src' / 'request' / 'weapons_table_all.html'

# 사용자가 처음에 제공한 전체 HTML 텍스트 (9개 카테고리)
# 사용자 입력이 매우 크므로, 실제 사용 시에는 사용자가 제공한 전체 HTML 텍스트를 여기에 포함
USER_HTML_CONTENT = """
# 여기에 사용자가 처음에 제공한 전체 HTML 텍스트를 포함
# 9개 카테고리: 폴암, 활, 석궁, 완드, 스태프, 단검, 아대, 너클, 총
"""

if __name__ == "__main__":
    # 실제로는 사용자가 제공한 HTML 텍스트를 여기에 포함
    # 하지만 사용자 입력이 매우 크기 때문에, 이 스크립트를 직접 실행하기는 어렵습니다.
    print("Error: USER_HTML_CONTENT에 사용자가 제공한 전체 HTML 텍스트를 포함해야 합니다.")
    print("사용자가 처음에 제공한 HTML 텍스트를 이 스크립트에 포함시킨 후 실행하세요.")
    exit(1)

