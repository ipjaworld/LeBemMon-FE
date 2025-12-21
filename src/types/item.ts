/**
 * 아이템 타입 정의
 */

export type ItemMajorCategory = 
  | 'weapon'      // 무기
  | 'common'      // 공용
  | 'warrior'    // 전사
  | 'mage'       // 마법사
  | 'archer'     // 궁수
  | 'rogue'      // 도적
  | 'pirate'     // 해적
  | 'consumable'; // 소비

export type ItemMediumCategory = 
  // 장비 공통
  | 'hat'         // 모자
  | 'gloves'      // 장갑
  | 'shoes'       // 신발
  | 'full-body'   // 전신
  | 'top'         // 상의
  | 'bottom'      // 하의
  | 'shield'      // 방패
  | 'earring'     // 귀고리
  | 'cape'        // 망토
  // 무기
  | 'snowboard'   // 스노우보드
  | 'sword'       // 검
  | 'wand'        // 지팡이
  | 'bow'         // 활
  // 소비
  | 'equip-scroll' // 장비 주문서
  | 'shuriken'     // 표창
  | 'etc';         // 기타

/**
 * 아이템 인터페이스
 */
export interface Item {
  /** 아이템 고유 ID */
  id: string;
  
  /** 아이템 이름 */
  name: string;
  
  /** 썸네일 이미지 URL */
  imageUrl: string;
  
  /** 대분류 */
  majorCategory: ItemMajorCategory;
  
  /** 중분류 */
  mediumCategory: ItemMediumCategory;
  
  /** 소분류 (선택적) */
  minorCategory?: string;
  
  /** 요구 레벨 */
  reqLevel?: number;
  
  /** 요구 힘 */
  reqStr?: number;
  
  /** 요구 민첩 */
  reqDex?: number;
  
  /** 요구 지능 */
  reqInt?: number;
  
  /** 요구 운 */
  reqLuk?: number;
  
  /** 요구 인기도 */
  reqPop?: number;
  
  /** 상점 판매가 (meso) */
  shopPrice?: number;
  
  /** 공격속도 (예: "보통", "빠름", "느림") */
  attackSpeed?: string;
  
  /** 공격력 */
  attackPower?: number;
  
  /** 마력 */
  magicPower?: number;
  
  /** 업그레이드 가능 횟수 */
  upgradeSlots?: number;
  
  /** 출시 여부 */
  isReleased: boolean;
  
  /** 아이템 설명 (선택적) */
  description?: string;
}

