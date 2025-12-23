# Scripts 디렉토리

Python 스크립트들이 목적별로 정리되어 있습니다.

## 폴더 구조

```
scripts/
  ├── parse/           # 데이터 파싱 스크립트
  ├── generate/        # 데이터 생성 스크립트
  ├── update/          # 데이터 업데이트 스크립트
  ├── add/             # 데이터 추가 스크립트
  ├── fix/             # 데이터 수정/정리 스크립트
  ├── validate/        # 데이터 검증 스크립트
  └── utils.py         # 공통 유틸리티 함수
```

## 사용법

### 공통 유틸리티

모든 스크립트는 `utils.py`의 헬퍼 함수를 사용할 수 있습니다:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import get_data_path

# src/data/ 폴더 내 파일 경로
monster_file = get_data_path('monster_data.json')
item_file = get_data_path('item_data.json')
```

### 실행

프로젝트 루트에서 실행:

```bash
# 예시
python scripts/generate/generate_mastery_books.py
python scripts/update/update_monster_exp_latest.py
python scripts/validate/check_data.py
```

## 각 폴더 설명

### parse/
원본 데이터를 파싱하여 JSON으로 변환하는 스크립트

- `parse_monster_db.py` - HTML에서 몬스터 데이터 추출

### generate/
새로운 데이터를 생성하는 스크립트

- `generate_mastery_books.py` - 마스터리북 데이터 생성

### update/
기존 데이터를 업데이트하는 스크립트

- `update_monster_exp.py` - 몬스터 경험치 업데이트
- `update_monster_exp_latest.py` - 최신 패치 경험치 업데이트
- `update_monster_ids.py` - 몬스터 ID 업데이트
- `update_earring_dex_scroll.py` - 드랍 아이템 업데이트

### add/
데이터에 필드나 항목을 추가하는 스크립트

- `add_new_monsters.py` - 새 몬스터 추가
- `add_isReleased_field.py` - isReleased 필드 추가
- `add_region_ids.py` - 지역 ID 추가

### fix/
데이터를 수정하거나 정리하는 스크립트

- `remove_duplicate_monsters.py` - 중복 몬스터 제거
- `assign_regions_by_pattern.py` - 패턴으로 지역 할당

### validate/
데이터를 검증하거나 통계를 확인하는 스크립트

- `check_data.py` - 데이터 검증 및 통계

## 주의사항

- 모든 스크립트는 프로젝트 루트(`D:\2025_project\rebemon`)에서 실행해야 합니다
- 데이터 파일 경로는 `utils.py`의 헬퍼 함수를 사용하는 것을 권장합니다
- 스크립트 실행 전에 데이터 백업을 권장합니다

