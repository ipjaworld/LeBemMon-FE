import json
from pathlib import Path
import sys

# scripts/utils.py import를 위한 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import get_data_path

file_path = get_data_path("monster_data.json")

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 레벨 50-70 범위 몬스터
level_50_70 = [m for m in data if 50 <= m.get('level', 0) <= 70 and m.get('exp', 0) > 0]
print(f'레벨 50-70 범위 몬스터 수: {len(level_50_70)}개')

released = [m for m in level_50_70 if m.get('isReleased', False)]
print(f'isReleased=true인 몬스터 수: {len(released)}개')
print(f'isReleased=false인 몬스터 수: {len(level_50_70) - len(released)}개')

# 전체 데이터 통계
all_with_exp = [m for m in data if m.get('exp', 0) > 0]
all_released = [m for m in all_with_exp if m.get('isReleased', False)]
print(f'\n전체 exp > 0인 몬스터: {len(all_with_exp)}개')
print(f'전체 isReleased=true인 몬스터: {len(all_released)}개')

if len(released) == 0 and len(level_50_70) > 0:
    print(f'\n처음 5개 샘플 (모두 isReleased=false):')
    for m in level_50_70[:5]:
        print(f"  {m['name']} (레벨 {m['level']}, EXP {m.get('exp', 0)}) - isReleased: {m.get('isReleased', False)}")

