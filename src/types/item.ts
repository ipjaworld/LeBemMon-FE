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
  | 'pendant'     // 펜던트
  // 무기
  | 'snowboard'   // 스노우보드
  | 'one-handed-sword'    // 한손검
  | 'two-handed-sword'    // 두손검
  | 'one-handed-axe'      // 한손도끼
  | 'two-handed-axe'      // 두손도끼
  | 'one-handed-blunt'    // 한손둔기
  | 'two-handed-blunt'    // 두손둔기
  | 'spear'       // 창
  | 'polearm'     // 폴암
  | 'bow'         // 활
  | 'crossbow'    // 석궁
  | 'wand'        // 완드
  | 'staff'       // 스태프
  | 'dagger'      // 단검
  | 'gauntlet'    // 아대
  | 'knuckle'     // 너클
  | 'gun'         // 총
  // 소비
  | 'equip-scroll' // 장비 주문서
  | 'mastery-book' // 마스터리북
  | 'shuriken'     // 표창
  | 'etc';         // 기타

import { JobCategoryId, JobSubCategoryId } from './job';

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
  
  /** 마법방어력 */
  magicDefense?: number;
  
  /** 업그레이드 가능 횟수 */
  upgradeSlots?: number;
  
  /** 최대 HP */
  maxHP?: number;
  
  /** 최대 MP */
  maxMP?: number;
  
  /** 출시 여부 */
  isReleased: boolean;
  
  /** 아이템 설명 (선택적) */
  description?: string;
  
  /** 마스터리북: 스킬 이름 */
  skillName?: string;
  
  /** 마스터리북: 스킬 레벨 (10, 20, 30 등) */
  skillLevel?: number;
  
  /** 마스터리북: 직업 카테고리 */
  jobCategory?: JobCategoryId;
  
  /** 마스터리북: 직업 세부 분류 */
  jobSubCategory?: JobSubCategoryId;
  
  /** 마스터리북: 인기 마스터리북 여부 */
  isPopularMasteryBook?: boolean;
}

