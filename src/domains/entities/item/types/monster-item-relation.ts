/**
 * 몬스터-아이템 관계 타입 정의
 */

export interface MonsterItemRelation {
  /** 몬스터 ID */
  monsterId: string;
  
  /** 아이템 ID */
  itemId: string;
  
  /** 드롭 확률 (선택적, 추후 확장용) */
  dropRate?: number;
}

