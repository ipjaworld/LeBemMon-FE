# 몬스터별 출몰 지역 정보 수집 가이드

## 개요

몬스터의 출몰 지역 정보를 체계적으로 수집하고 입력하는 방법을 안내합니다.

## 수집 방법

### 방법 1: 게임 내 직접 확인 (가장 정확)

1. **게임 플레이 중 확인**
   - 각 맵에서 출몰하는 몬스터를 직접 확인
   - 맵 이름과 지역/마을 대응 관계 기록

2. **확인해야 할 정보**
   ```
   - 맵 이름 (예: "페리온 근처 풀숲")
   - 해당 맵이 속한 마을/지역 (예: "페리온" → "victoria-perion")
   - 해당 맵에서 출몰하는 몬스터 이름들
   ```

### 방법 2: 게임 위키/커뮤니티 활용

**한국어 자료:**
- 메이플스토리 공식 위키
- 인벤, 디시인사이드 등 커뮤니티
- 유튜브 플레이 영상

**영문 자료:**
- MapleStory Wiki (fandom.com)
- Hidden Street (구버전이지만 레벨 정보 유용)

### 방법 3: 부분적/점진적 수집 (권장)

모든 몬스터를 한 번에 수집하지 않고, **자주 사용되는 지역부터 점진적으로 수집**:

1. **1단계: 빅토리아 지역 (우선순위 1)**
   - 페리온, 헤네시스, 커닝시티 등 초반 지역
   - 대부분의 저레벨 몬스터

2. **2단계: 오르비스, 엘나스 산맥 (우선순위 2)**
   - 중반 레벨 몬스터

3. **3단계: 나머지 지역 (우선순위 3)**
   - 루디브리엄, 아쿠아로드, 세계여행 등

## 필요한 정보 형태

### 입력 예시

아래와 같은 형태로 정리해주시면 됩니다:

```
달팽이 (100100)
- victoria-perion
- victoria-henesys

슬라임 (210100)
- victoria-kerning
- victoria-lith
```

또는 더 구체적으로:

```json
{
  "monsterId": "100100",
  "monsterName": "달팽이",
  "regions": [
    {
      "regionId": "victoria-perion",
      "regionName": "페리온",
      "notes": "페리온 근처 풀숲"
    },
    {
      "regionId": "victoria-henesys",
      "regionName": "헤네시스",
      "notes": "헤네시스 남쪽 풀숲"
    }
  ]
}
```

### 가장 간단한 형태 (추천)

**CSV나 텍스트 파일**로 다음과 같이 정리:

```
몬스터ID,몬스터이름,지역ID1,지역ID2,지역ID3
100100,달팽이,victoria-perion,victoria-henesys,
210100,슬라임,victoria-kerning,victoria-lith,
```

또는 더 간단하게:

```
100100: victoria-perion, victoria-henesys
210100: victoria-kerning, victoria-lith
120100: victoria-perion
```

## 지역 ID 참고표

수집 시 참고할 지역/마을 ID 목록:

### 빅토리아
- `victoria` (최상위 지역)
- `victoria-perion` (페리온)
- `victoria-henesys` (헤네시스)
- `victoria-kerning` (커닝시티)
- `victoria-lith` (리스항구)
- `victoria-ellinia` (엘리니아)
- `victoria-florina` (플로리나비치)
- `victoria-sleepywood` (슬리피우드)

### 오르비스
- `orbis` (최상위 지역)

### 엘나스 산맥
- `ellin-forest` (최상위 지역)

### 루디브리엄
- `ludibrium` (최상위 지역)

### 아쿠아로드
- `aqua-road` (최상위 지역)

### 세계여행
- `world-travel-china` (세계여행-중국)
- `world-travel-taiwan` (세계여행-대만)
- `world-travel-thailand` (세계여행-태국)
- `world-travel-japan` (세계여행-일본)
  - `japan-mushroom-shrine` (버섯신사)
  - `japan-showa-town` (쇼와마을)
  - `japan-kaede-castle` (일본:카에데성)

### 리프레
- `leafre` (최상위 지역)

### 마스테리아
- `masteria` (최상위 지역)

> 💡 **Tip**: 지역 ID는 `src/data/region_data.json` 파일에서 확인할 수 있습니다.

## 실제 수집 워크플로우 제안

### Option A: 게임 플레이 중 실시간 기록

1. 게임 플레이하며 각 맵 방문
2. 간단한 텍스트 파일이나 노트에 기록:
   ```
   [페리온 근처 풀숲]
   - 달팽이
   - 파란 달팽이
   
   [헤네시스 남쪽 풀숲]
   - 달팽이
   - 스포아
   ```
3. 나중에 정리하여 regionId 매핑

### Option B: 위키/자료에서 대량 수집

1. 각 지역별 몬스터 목록 페이지 찾기
2. 몬스터 이름과 지역 매핑 추출
3. 일괄 정리

### Option C: 커뮤니티 협업

1. 공개 GitHub 저장소나 커뮤니티에 공유
2. 여러 사용자가 각자 아는 정보 추가
3. Pull Request나 이슈로 제출

## 데이터 입력 스크립트 사용

수집한 데이터를 실제 JSON에 반영하려면, 아래 형태로 정리해주시면 스크립트로 자동 입력 가능합니다:

### 입력 파일 예시 (monster_regions.txt)

```
# 형식: 몬스터ID|지역ID1,지역ID2,지역ID3

100100|victoria-perion,victoria-henesys
100101|victoria-perion
120100|victoria-henesys
210100|victoria-kerning,victoria-lith
```

이런 형태로 제공해주시면 Python 스크립트를 만들어서 자동으로 `monster_data.json`에 `regionIds` 필드를 추가할 수 있습니다.

## 다음 단계

1. ✅ 이 가이드 확인
2. ⏳ 수집 방법 선택 (방법 1, 2, 또는 3)
3. ⏳ 데이터 수집 시작 (우선 빅토리아 지역부터)
4. ⏳ 수집한 데이터를 텍스트/CSV 형태로 정리
5. ⏳ 정리한 데이터를 제공하면 스크립트로 자동 입력

## FAQ

**Q: 모든 몬스터의 지역 정보가 필요한가요?**
A: 아니요. 우선 `isReleased: true`인 몬스터만 수집하면 됩니다. 출시되지 않은 몬스터는 나중에 추가해도 됩니다.

**Q: 하나의 몬스터가 여러 지역에 출몰하는 경우?**
A: `regionIds` 배열에 모든 지역 ID를 포함하면 됩니다.
```json
"regionIds": ["victoria-perion", "victoria-henesys", "victoria-kerning"]
```

**Q: 정확하지 않은 정보는?**
A: 일단 기록해두고, 나중에 게임 내에서 확인하여 수정하면 됩니다. 완벽하지 않아도 점진적으로 개선하면 됩니다.

**Q: 수집 속도가 느리면?**
A: 문제 없습니다. 지역별로 나눠서 수집하고, 부분적으로라도 데이터가 있으면 필터 기능을 구현할 수 있습니다. 완전한 데이터가 없어도 점진적으로 추가하면 됩니다.

