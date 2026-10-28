/**
 * 아이템 타입 정의
 * 
 * 이 파일은 하위 호환성을 위해 유지됩니다.
 * 새 코드에서는 item-types.ts의 타입을 직접 사용하세요.
 */

import { JobCategoryId, JobSubCategoryId } from '@/domains/entities/job/types/job';

// ============================================================
// Re-export new type system
// ============================================================

export type {
  ItemType,
  EquipmentMajorCategory,
  EquipmentMediumCategory,
  ConsumableType,
  EtcType,
  CashType,
  MountableType,
  BaseItem,
  EquipmentItem,
  ConsumableItem,
  EtcItem,
  CashItem,
  MountableItem,
} from './item-types';

export {
  isEquipmentItem,
  isConsumableItem,
  isEtcItem,
  isCashItem,
  isMountableItem,
  isMasteryBook,
  isWeapon,
  isArmor,
} from './item-guards';

// ============================================================
// Legacy Types (하위 호환성)
// ============================================================

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

// ============================================================
// Item Interface (통합 인터페이스 - 하위 호환성 유지)
// ============================================================

/**
 * 아이템 인터페이스
 * 
 * 모든 아이템 타입의 필드를 포함하는 통합 인터페이스입니다.
 * 타입 안전성을 위해 item-types.ts의 세분화된 타입 사용을 권장합니다.
 */
export interface Item {
  /** 아이템 고유 ID */
  id: string;
  
  /** 아이템 이름 */
  name: string;
  
  /** 썸네일 이미지 URL */
  imageUrl: string;
  
  /** 출시 여부 */
  isReleased: boolean;
  
  /** 아이템 설명 */
  description?: string;
  
  /** 상점 판매가 (meso) */
  shopPrice?: number;

  // --- 아이템 타입 구분 (신규) ---
  /** 아이템 타입 */
  itemType?: 'equipment' | 'consumable' | 'etc' | 'cash' | 'mountable';
  
  /** 소비 아이템 세부 타입 */
  consumableType?: 'potion' | 'scroll' | 'mastery-book' | 'throwing' | 'other';

  // --- 카테고리 (장비/소비) ---
  /** 대분류 */
  majorCategory: ItemMajorCategory;
  
  /** 중분류 */
  mediumCategory: ItemMediumCategory;
  
  /** 소분류 */
  minorCategory?: string;

  // --- 요구 스탯 ---
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

  // --- 제공 스탯 (신규) ---
  /** 힘 */
  str?: number;
  /** 민첩 */
  dex?: number;
  /** 지능 */
  int?: number;
  /** 운 */
  luk?: number;

  // --- 전투 스탯 ---
  /** 공격력 */
  attackPower?: number;
  /** 마력 */
  magicPower?: number;
  /** 물리방어력 (신규) */
  physicalDefense?: number;
  /** 마법방어력 */
  magicDefense?: number;
  /** 공격속도 */
  attackSpeed?: string;

  // --- 기타 장비 ---
  /** 최대 HP */
  maxHP?: number;
  /** 최대 MP */
  maxMP?: number;
  /** 업그레이드 가능 횟수 */
  upgradeSlots?: number;
  /** 착용 가능 직업군 (신규) */
  equippableJobs?: JobCategoryId[];

  // --- 마스터리북 전용 ---
  /** 스킬 이름 */
  skillName?: string;
  /** 스킬 레벨 (10, 20, 30 등) */
  skillLevel?: number;
  /** 직업 카테고리 */
  jobCategory?: JobCategoryId;
  /** 직업 세부 분류 */
  jobSubCategory?: JobSubCategoryId;
  /** 인기 마스터리북 여부 */
  isPopularMasteryBook?: boolean;
}
