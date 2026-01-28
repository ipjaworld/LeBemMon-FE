/**
 * 장비 슬롯 타입 정의
 */

export type EquipmentSlotType =
  | 'hat'           // 모자
  | 'medal'         // 칭호
  | 'forehead'      // 얼굴장식
  | 'eye-acc'       // 눈장식
  | 'ear-acc'       // 귀장식
  | 'top'           // 상의
  | 'bottom'        // 하의
  | 'full-body'     // 한벌옷 (전신)
  | 'weapon'        // 무기
  | 'shoes'         // 신발
  | 'gloves'        // 장갑
  | 'belt'          // 허리띠
  | 'shield'        // 방패
  | 'cape'          // 망토
  | 'pendant'       // 펜던트
  | 'ring';         // 반지

/**
 * 장비 슬롯 정보
 */
export interface EquipmentSlot {
  /** 슬롯 타입 */
  type: EquipmentSlotType | null;
  /** 슬롯 라벨 (한글) */
  label: string;
  /** 그리드 위치 (row, col) */
  position: { row: number; col: number };
  /** 활성화 여부 */
  enabled: boolean;
}

/**
 * 장비 아이템 설정
 */
export interface EquipmentItem {
  /** 아이템 ID (아이템이 없을 경우 빈 문자열) */
  itemId: string;
  /** 아이템 이름 (아이템이 없을 경우 빈 문자열) */
  name: string;
  /** 아이템 이미지 URL (아이템이 없을 경우 빈 문자열) */
  imageUrl: string;
  /** 추가 옵션 (커스터마이징 가능) */
  options?: EquipmentOptions;
}

/**
 * 아이템이 있는지 확인하는 헬퍼 함수
 */
export function hasItem(item: EquipmentItem | null): boolean {
  return item !== null && item.itemId !== '';
}

/**
 * 옵션이 있는지 확인하는 헬퍼 함수
 */
export function hasOptions(item: EquipmentItem | null): boolean {
  if (!item || !item.options) return false;
  const opts = item.options;
  return !!(
    opts.attackPower ||
    opts.magicPower ||
    opts.str ||
    opts.dex ||
    opts.int ||
    opts.luk
  );
}

/**
 * 장비 옵션
 */
export interface EquipmentOptions {
  /** 공격력 */
  attackPower?: number;
  /** 마력 */
  magicPower?: number;
  /** 물리 방어력 */
  physicalDefense?: number;
  /** 마법 방어력 */
  magicDefense?: number;
  /** 최대 HP */
  maxHP?: number;
  /** 최대 MP */
  maxMP?: number;
  /** 힘 */
  str?: number;
  /** 민첩 */
  dex?: number;
  /** 지능 */
  int?: number;
  /** 운 */
  luk?: number;
  /** 명중률 */
  accuracy?: number;
  /** 회피율 */
  evasion?: number;
  /** 강화 횟수 */
  upgradeCount?: number;
}

/**
 * 직업별 장비 설정
 */
export interface JobEquipment {
  /** 직업 ID */
  jobId: string;
  /** 각 슬롯별 장비 아이템 */
  equipment: Record<EquipmentSlotType, EquipmentItem | null>;
  /** 한벌옷 착용 여부 (한벌옷 착용 시 하의 슬롯 비활성화) */
  hasFullBody: boolean;
}
