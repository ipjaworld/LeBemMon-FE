/**
 * 지역 타입 정의
 * 지역은 계층 구조를 가지며, 최상위 지역(예: 빅토리아)과 하위 마을(예: 페리온)을 모두 포함합니다.
 */
export interface Region {
  /** 지역/마을의 고유 ID */
  id: string;
  
  /** 지역/마을의 표시 이름 */
  name: string;
  
  /** 상위 지역 ID (최상위 지역인 경우 null) */
  parentId: string | null;
  
  /** 지역 타입: 'region' (최상위 지역) 또는 'town' (마을) */
  type: 'region' | 'town';
  
  /** 출시 여부 */
  isReleased: boolean;
  
  /** 표시용 라벨 (선택적, name과 다를 경우 사용) */
  displayName?: string;
}

