/**
 * Item Type Hierarchy
 * 
 * 5가지 아이템 타입:
 * - EquipmentItem: 장비 (무기, 방어구, 악세서리)
 * - ConsumableItem: 소비 (포션, 주문서, 마스터리북, 표창)
 * - EtcItem: 기타 (전리품, 퀘스트 아이템, 재료)
 * - CashItem: 캐시 (치장용, 캐시샵 전용)
 * - MountableItem: 설치 (의자, 장식품)
 */

import { JobCategoryId, JobSubCategoryId } from '@/domains/entities/job/types/job';

// ============================================================
// Item Type Discriminator
// ============================================================

export type ItemType = 'equipment' | 'consumable' | 'etc' | 'cash' | 'mountable';

// ============================================================
// Category Types
// ============================================================

/** 장비 대분류 (직업군) */
export type EquipmentMajorCategory =
  | 'weapon'    // 무기
  | 'common'    // 공용
  | 'warrior'   // 전사
  | 'mage'      // 마법사
  | 'archer'    // 궁수
  | 'rogue'     // 도적
  | 'pirate';   // 해적

/** 장비 중분류 (슬롯/무기 종류) */
export type EquipmentMediumCategory =
  // 방어구
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
  | 'snowboard'           // 스노우보드
  | 'one-handed-sword'    // 한손검
  | 'two-handed-sword'    // 두손검
  | 'one-handed-axe'      // 한손도끼
  | 'two-handed-axe'      // 두손도끼
  | 'one-handed-blunt'    // 한손둔기
  | 'two-handed-blunt'    // 두손둔기
  | 'spear'               // 창
  | 'polearm'             // 폴암
  | 'bow'                 // 활
  | 'crossbow'            // 석궁
  | 'wand'                // 완드
  | 'staff'               // 스태프
  | 'dagger'              // 단검
  | 'gauntlet'            // 아대
  | 'knuckle'             // 너클
  | 'gun';                // 총

/** 소비 아이템 세부 타입 */
export type ConsumableType =
  | 'potion'        // 포션
  | 'scroll'        // 주문서
  | 'mastery-book'  // 마스터리북
  | 'throwing'      // 표창/화살
  | 'other';        // 기타 소비

/** 기타 아이템 세부 타입 */
export type EtcType =
  | 'loot'          // 전리품 (몬스터 드롭)
  | 'quest'         // 퀘스트 아이템
  | 'material'      // 재료
  | 'summon-stone'  // 소환의 돌
  | 'magic-stone'   // 마법의 돌
  | 'other';        // 기타

/** 캐시 아이템 세부 타입 */
export type CashType =
  | 'costume'       // 치장용
  | 'pet'           // 펫
  | 'effect'        // 이펙트
  | 'other';        // 기타

/** 설치 아이템 세부 타입 */
export type MountableType =
  | 'chair'         // 의자
  | 'decoration'    // 장식품
  | 'other';        // 기타

// ============================================================
// Base Item (공통 필드)
// ============================================================

export interface BaseItem {
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
}

// ============================================================
// EquipmentItem (장비)
// ============================================================

export interface EquipmentItem extends BaseItem {
  itemType: 'equipment';

  /** 대분류 (직업군) */
  majorCategory: EquipmentMajorCategory;

  /** 중분류 (슬롯/무기 종류) */
  mediumCategory: EquipmentMediumCategory;

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

  // --- 기타 ---
  /** 최대 HP */
  maxHP?: number;
  /** 최대 MP */
  maxMP?: number;
  /** 업그레이드 가능 횟수 */
  upgradeSlots?: number;

  /** 착용 가능 직업군 (신규) */
  equippableJobs?: JobCategoryId[];
}

// ============================================================
// ConsumableItem (소비)
// ============================================================

export interface ConsumableItem extends BaseItem {
  itemType: 'consumable';

  /** 소비 아이템 세부 타입 */
  consumableType: ConsumableType;

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

// ============================================================
// EtcItem (기타)
// ============================================================

export interface EtcItem extends BaseItem {
  itemType: 'etc';

  /** 기타 아이템 세부 타입 */
  etcType: EtcType;
}

// ============================================================
// CashItem (캐시)
// ============================================================

export interface CashItem extends BaseItem {
  itemType: 'cash';

  /** 캐시 아이템 세부 타입 */
  cashType: CashType;
}

// ============================================================
// MountableItem (설치)
// ============================================================

export interface MountableItem extends BaseItem {
  itemType: 'mountable';

  /** 설치 아이템 세부 타입 */
  mountableType: MountableType;
}

// ============================================================
// Union Type
// ============================================================

/** 모든 아이템 타입의 유니온 */
export type Item = EquipmentItem | ConsumableItem | EtcItem | CashItem | MountableItem;
