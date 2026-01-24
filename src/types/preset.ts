import type { JobCategoryId } from '@/types/job';
import type { EquipmentSlotType, EquipmentItem } from '@/types/equipment';

/** 캐릭터 스탯 창 스냅샷 (프리셋 저장/불러오기용) */
export interface CharacterSnapshot {
  characterName: string;
  level: number;
  allocatedStats: { str: number; dex: number; int: number; luk: number };
  isMapleWarrior20Active: boolean;
}

/** 장비 시뮬레이터 프리셋 */
export interface EquipmentPreset {
  id: string;
  name: string;
  savedAt: number;
  job: JobCategoryId | null;
  equipment: Record<EquipmentSlotType, EquipmentItem | null>;
  hasFullBody: boolean;
  character: CharacterSnapshot;
}
