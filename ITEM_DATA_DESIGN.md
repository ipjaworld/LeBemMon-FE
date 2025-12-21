# 아이템 데이터 구조 설계 문서

## 개요
메이플스토리 아이템 데이터베이스 구조 및 몬스터-아이템 관계 설계 문서입니다.

## 데이터 구조

### 1. 아이템 카테고리 구조

#### 대분류 (Major Category)
- `weapon`: 무기
- `common`: 공용
- `warrior`: 전사
- `mage`: 마법사
- `archer`: 궁수
- `rogue`: 도적
- `pirate`: 해적
- `consumable`: 소비

#### 중분류 (Medium Category)
각 대분류별로 세부 카테고리가 존재합니다.

**무기 (weapon)**
- 세부 카테고리는 무기 타입별로 구분 (예: 한손검, 두손검, 활, 지팡이 등)

**장비 (common, warrior, mage, archer, rogue, pirate)**
- `hat`: 모자
- `gloves`: 장갑
- `shoes`: 신발
- `full-body`: 전신
- `top`: 상의
- `bottom`: 하의
- `shield`: 방패
- `earring`: 귀고리
- `cape`: 망토
- 기타 장비 타입별 세부 카테고리

**소비 (consumable)**
- `equip-scroll`: 장비 주문서
- `etc`: 기타 소비 아이템

#### 소분류 (Minor Category)
중분류 내에서 더 세부적인 분류입니다.

**예시:**
- 소비 > 장비 주문서 > 투구
- 소비 > 장비 주문서 > 상의
- 무기 > 한손검 > 일반

### 2. 아이템 데이터 구조

```typescript
interface Item {
  id: string;                    // 아이템 고유 ID (예: "1442030")
  name: string;                  // 아이템 이름 (예: "메이플 스노우보드")
  imageUrl: string;              // 썸네일 URL
  majorCategory: string;         // 대분류
  mediumCategory: string;        // 중분류
  minorCategory?: string;        // 소분류 (선택적)
  
  // 요구사항
  reqLevel?: number;             // 요구 레벨
  reqStr?: number;               // 요구 힘
  reqDex?: number;               // 요구 민첩
  reqInt?: number;               // 요구 지능
  reqLuk?: number;               // 요구 운
  reqPop?: number;               // 요구 인기도
  
  // 아이템 스펙
  shopPrice?: number;            // 상점 판매가 (meso)
  attackSpeed?: string;          // 공격속도 (예: "보통", "빠름", "느림")
  attackPower?: number;          // 공격력
  magicPower?: number;            // 마력
  upgradeSlots?: number;         // 업그레이드 가능 횟수
  
  // 기타
  isReleased: boolean;           // 출시 여부
  description?: string;          // 아이템 설명
}
```

### 3. 몬스터-아이템 관계 구조

```typescript
interface MonsterItemRelation {
  monsterId: string;            // 몬스터 ID
  itemId: string;                // 아이템 ID
  dropRate?: number;             // 드롭 확률 (선택적, 추후 확장용)
}
```

### 4. 몬스터 데이터 확장

```typescript
interface Monster {
  // 기존 필드들...
  
  /** 드롭하는 아이템 ID 배열 */
  dropItemIds?: string[];
  
  /** 주요 드랍 아이템 ID 배열 (1~3개, null 가능) */
  featuredDropItemIds?: string[] | null;
}
```

## 데이터 예시

### 예시 1: 소비 아이템
```json
{
  "id": "2040029",
  "name": "투구 민첩 주문서 60%",
  "imageUrl": "https://maplestory.io/api/gms/200/item/2040029/icon?resize=2",
  "majorCategory": "consumable",
  "mediumCategory": "equip-scroll",
  "minorCategory": "hat",
  "isReleased": true
}
```

### 예시 2: 무기 아이템
```json
{
  "id": "1442030",
  "name": "메이플 스노우보드",
  "imageUrl": "https://maplestory.io/api/gms/200/item/1442030/icon?resize=2",
  "majorCategory": "weapon",
  "mediumCategory": "snowboard",
  "reqLevel": 70,
  "reqStr": 0,
  "reqDex": 0,
  "reqInt": 0,
  "reqLuk": 0,
  "reqPop": 0,
  "shopPrice": 1,
  "attackSpeed": "보통",
  "attackPower": 85,
  "upgradeSlots": 7,
  "isReleased": true
}
```

### 예시 3: 몬스터-아이템 관계
```json
{
  "monsterId": "8800002",
  "itemId": "2040029"
}
```

### 예시 4: 몬스터 데이터 (드롭 아이템 포함)
```json
{
  "id": "8800002",
  "name": "크림슨 발록",
  "dropItemIds": ["2040029", "1442030"],
  "featuredDropItemIds": ["2040029"]
}
```

## 파일 구조

```
src/
├── types/
│   ├── item.ts                    # 아이템 타입 정의
│   └── monster-item-relation.ts    # 몬스터-아이템 관계 타입 정의
├── data/
│   ├── item_data.json             # 아이템 데이터
│   ├── item_data.d.ts             # 아이템 데이터 타입 정의
│   ├── monster_item_relations.json # 몬스터-아이템 관계 데이터
│   └── monster_item_relations.d.ts # 관계 데이터 타입 정의
```

## 특수 규칙

### 주문서 아이템 이미지
모든 60% 주문서 아이템은 다음 이미지를 사용합니다:
- URL: `https://maplestory.io/api/gms/200/item/2040029/icon?resize=2`

이 규칙은 데이터 입력 시 자동으로 적용되거나, 프론트엔드에서 처리할 수 있습니다.

## 향후 확장 계획

1. **드롭 확률 데이터**: `MonsterItemRelation`에 `dropRate` 필드 추가
2. **아이템 상세 페이지**: 카드 클릭 시 상세 정보 표시
3. **드롭 아이템 필터링**: 특정 아이템을 드롭하는 몬스터 검색
4. **아이템 검색 기능**: 카테고리별 아이템 검색 및 필터링
5. **아이템 통계**: 드롭률, 드롭 몬스터 수 등 통계 정보

## 몬스터-아이템 관계 예시

### 예시 아이템 1: 투구 민첩 주문서 60%
- **아이템 ID**: `2040029`
- **드롭 몬스터**: 
  - 크림슨 발록 (monsterId: 추후 확인 필요)
  - 마스터 크로노스 (monsterId: 추후 확인 필요)
  - 월묘 (monsterId: 추후 확인 필요)
  - 원로그레이 (monsterId: 추후 확인 필요)

### 예시 아이템 2: 메이플 스노우보드
- **아이템 ID**: `1442030`
- **드롭 몬스터**:
  - 다크와이번 (monsterId: 추후 확인 필요)
  - 다크코니언 (monsterId: 추후 확인 필요)
  - 네스트골렘 (monsterId: 추후 확인 필요)

> **참고**: 실제 몬스터 ID는 `monster_data.json`에서 확인 후 `monster_item_relations.json`에 추가해야 합니다.

## 참고 사항

- 아이템 데이터는 방대하므로 단계적으로 추가 예정
- 초기에는 타입과 구조만 정의하고, 예시 데이터만 포함
- 실제 데이터 입력은 추후 별도 작업으로 진행
- 몬스터 이름과 ID 매핑은 `monster_data.json`을 참조하여 관계 데이터를 생성해야 함

