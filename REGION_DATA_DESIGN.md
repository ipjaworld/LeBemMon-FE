# 지역 데이터 설계 문서

## 1. 데이터 구조 설계

### 1.1 Region 타입 정의

```typescript
interface Region {
  id: string;              // 고유 ID (예: "victoria", "victoria-perion")
  name: string;            // 표시 이름 (예: "빅토리아", "페리온")
  parentId: string | null; // 상위 지역 ID (최상위 지역은 null)
  type: 'region' | 'town'; // 지역 타입
  isReleased: boolean;     // 출시 여부
}
```

### 1.2 계층 구조 표현

- **평면 구조 + parentId 패턴**: 모든 지역과 마을을 하나의 배열에 저장하고 `parentId`로 계층 관계를 표현
- **장점**: 
  - 쿼리가 간단함 (특정 지역의 모든 하위 마을 조회: `parentId === regionId`)
  - 확장성이 좋음 (나중에 더 깊은 계층 추가 가능)
  - 데이터베이스로 마이그레이션 시 자연스러운 구조

### 1.3 ID 명명 규칙

- 최상위 지역: `{영문이름}` (예: `victoria`, `orbis`)
- 하위 마을: `{상위지역영문이름}-{마을영문이름}` (예: `victoria-perion`)
- 특수 케이스 (일본:카에데성): `japan-kaede-castle` (콜론 대신 하이픈 사용)

## 2. 몬스터-지역 연결 설계

### 2.1 연결 방식

**Monster 타입에 `regionIds` 필드 추가** (string[])

```typescript
interface Monster {
  // ... 기존 필드들
  regionIds?: string[]; // 출몰 지역/마을 ID 배열
}
```

### 2.2 설계 이유

1. **정규화**: 몬스터 데이터에 지역 정보를 포함 (역정규화)
   - 장점: 몬스터 조회 시 지역 정보도 함께 조회 가능 (JOIN 불필요)
   - 단점: 데이터 중복 가능성 (하지만 몬스터-지역은 다대다 관계이므로 적절한 선택)

2. **다대다 관계**: 
   - 한 몬스터는 여러 지역에 출몰할 수 있음
   - 한 지역에는 여러 몬스터가 출몰
   - 배열로 표현하면 자연스럽게 다대다 관계 표현

3. **쿼리 효율성**:
   - "특정 지역의 몬스터 찾기": `monsters.filter(m => m.regionIds?.includes(regionId))`
   - "특정 몬스터의 출몰 지역 찾기": `regions.filter(r => monster.regionIds?.includes(r.id))`

### 2.3 대안 방식과 비교

#### 대안 1: 별도 매핑 테이블/JSON
```json
// monster_region_mapping.json
[
  { "monsterId": "100100", "regionId": "victoria-perion" },
  { "monsterId": "100100", "regionId": "victoria-henesys" }
]
```
- 장점: 완전한 정규화
- 단점: 추가 파일 관리, 쿼리 시 JOIN 필요

#### 대안 2: Region에 monsterIds 추가
```typescript
interface Region {
  monsterIds: string[];
}
```
- 단점: 한 몬스터가 여러 지역에 출몰할 경우 중복 관리 필요, 데이터 일관성 유지 어려움

**결론**: Monster에 regionIds를 추가하는 방식이 가장 실용적

## 3. 데이터 마이그레이션 플랜

### 3.1 단계별 접근

#### Phase 1: 기본 구조 구축 (현재)
- ✅ Region 타입 정의
- ✅ region_data.json 생성
- ✅ Monster 타입에 regionIds 추가 (선택적 필드)

#### Phase 2: 데이터 수집 및 입력
1. 각 몬스터의 출몰 지역 정보 수집
2. monster_data.json에 regionIds 추가
   - 초기에는 빈 배열 `[]` 또는 필드 자체를 생략
   - 점진적으로 데이터 추가

#### Phase 3: UI 구현
1. 지역 필터 UI 추가
2. 필터 로직 구현:
   ```typescript
   const filteredMonsters = useMemo(() => {
     let result = monsters.filter(m => m.isReleased);
     
     if (selectedRegionId) {
       result = result.filter(m => 
         m.regionIds?.includes(selectedRegionId) ||
         // 하위 마을을 선택한 경우, 상위 지역의 모든 몬스터도 포함할지 결정 필요
       );
     }
     
     return result;
   }, [monsters, selectedRegionId]);
   ```

#### Phase 4: 백엔드 마이그레이션 (향후)
- MongoDB/SQL 등으로 마이그레이션 시
- Region 컬렉션/테이블: 현재 JSON 구조 그대로 사용
- Monster 컬렉션/테이블: regionIds 필드 유지 (또는 별도 매핑 테이블로 변경)

## 4. 특수 케이스 처리

### 4.1 "일본:카에데성" 형태
- 처리: 마을로 분류 (`type: 'town'`)
- ID: `japan-kaede-castle` (콜론 대신 하이픈)
- 표시: 이름은 원본 유지 (`name: "일본:카에데성"`)

### 4.2 지역 단위 vs 마을 단위 필터링
- **옵션 1**: 지역 선택 시 하위 마을의 모든 몬스터 포함
- **옵션 2**: 정확히 선택한 지역/마을의 몬스터만 표시
- **권장**: 옵션 1 (사용자 경험 측면에서 더 직관적)

## 5. 확장성 고려사항

### 5.1 향후 추가 가능한 필드
- Region: `order` (정렬 순서), `imageUrl` (지역 이미지), `description`
- Monster-Region: `spawnRate` (출현 확률), `spawnTime` (출현 시간대) 등

### 5.2 성능 최적화
- 지역별 몬스터 인덱스 생성 (백엔드 마이그레이션 시)
- 캐싱 전략 (프론트엔드)

## 6. 데이터 입력 가이드

### 6.1 regionIds 입력 규칙
```json
{
  "id": "100100",
  "name": "달팽이",
  "regionIds": ["victoria-perion", "victoria-henesys"]
}
```

### 6.2 검증 규칙
- regionIds의 모든 값이 region_data.json에 존재해야 함
- 최상위 지역 ID만 포함할지, 마을 ID도 포함할지 결정 필요
  - 권장: 마을 단위로 저장 (더 세밀한 필터링 가능)

## 7. 다음 단계

1. ✅ 지역 데이터 JSON 생성
2. ⏳ 몬스터별 출몰 지역 정보 수집
3. ⏳ monster_data.json에 regionIds 추가
4. ⏳ 지역 필터 UI 구현
5. ⏳ 필터링 로직 구현

