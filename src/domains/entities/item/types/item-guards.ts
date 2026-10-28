/**
 * Item Type Guards
 * 
 * 런타임에서 아이템 타입을 구분하기 위한 타입 가드 함수들
 */

import type {
  Item,
  EquipmentItem,
  ConsumableItem,
  EtcItem,
  CashItem,
  MountableItem,
} from './item-types';

/**
 * 장비 아이템인지 확인
 */
export function isEquipmentItem(item: Item): item is EquipmentItem {
  return item.itemType === 'equipment';
}

/**
 * 소비 아이템인지 확인
 */
export function isConsumableItem(item: Item): item is ConsumableItem {
  return item.itemType === 'consumable';
}

/**
 * 기타 아이템인지 확인
 */
export function isEtcItem(item: Item): item is EtcItem {
  return item.itemType === 'etc';
}

/**
 * 캐시 아이템인지 확인
 */
export function isCashItem(item: Item): item is CashItem {
  return item.itemType === 'cash';
}

/**
 * 설치 아이템인지 확인
 */
export function isMountableItem(item: Item): item is MountableItem {
  return item.itemType === 'mountable';
}

/**
 * 마스터리북인지 확인
 */
export function isMasteryBook(item: Item): item is ConsumableItem {
  return isConsumableItem(item) && item.consumableType === 'mastery-book';
}

/**
 * 무기인지 확인
 */
export function isWeapon(item: Item): item is EquipmentItem {
  return isEquipmentItem(item) && item.majorCategory === 'weapon';
}

/**
 * 방어구인지 확인 (무기가 아닌 장비)
 */
export function isArmor(item: Item): item is EquipmentItem {
  return isEquipmentItem(item) && item.majorCategory !== 'weapon';
}
