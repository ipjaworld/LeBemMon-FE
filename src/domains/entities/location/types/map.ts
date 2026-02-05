/**
 * 게임 맵 타입 정의
 * 실제 인게임 맵 (헤네시스, 골렘의 사원 등)을 나타냅니다.
 * region보다 더 세부적인 단위입니다.
 */
export interface GameMap {
  /** 맵 고유 ID (게임 내 맵 ID, 예: "100000000") */
  id: string;
  
  /** 맵 이름 */
  name: string;
  
  /** 해당 맵이 속한 region ID (region_data.json의 id 참조) */
  regionId: string;
  
  /** 맵 타입 */
  mapType: MapType;
  
  /** 해당 맵에 출현하는 몬스터 ID 배열 (monster_data.json의 id 참조) */
  monsterIds: string[];
  
  /** 몬스터별 최대 스폰 수 (monsterId -> 최대 스폰 수) */
  monsterSpawns?: {
    [monsterId: string]: number;
  };
  
  /** 출시 여부 (리메이크에 존재하는지) */
  isReleased: boolean;
  
  /** 추천 레벨 범위 (선택적) */
  recommendedLevel?: {
    min: number;
    max: number;
  };
  
  /** 맵 설명/메모 (선택적) */
  description?: string;
  
  /** 포탈로 연결된 맵 ID 배열 (map_data.json의 id 참조) */
  portalMapIds?: string[];
  
  /** 맵 이미지 URL (선택적) */
  imageUrls?: {
    /** 맵 전체 렌더 이미지 */
    render?: string;
    /** 미니맵 이미지 */
    minimap?: string;
    /** 맵 아이콘 */
    icon?: string;
  };
}

/** 맵 타입 */
export type MapType = 
  | 'town'      // 마을 (안전지대)
  | 'field'     // 필드 (일반 사냥터)
  | 'dungeon'   // 던전
  | 'event'     // 이벤트 맵
  | 'etc';      // 기타

