import type { EquipmentPreset } from '@/types/preset';

const STORAGE_KEY = 'rebemon-equipment-presets';

export function getPresets(): EquipmentPreset[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return parsed as EquipmentPreset[];
  } catch {
    return [];
  }
}

export function savePreset(
  name: string,
  payload: Omit<EquipmentPreset, 'id' | 'name' | 'savedAt'>
): EquipmentPreset {
  const presets = getPresets();
  const id = `preset-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
  const savedAt = Date.now();
  const preset: EquipmentPreset = { id, name, savedAt, ...payload };
  presets.push(preset);
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(presets));
  } catch (e) {
    console.warn('Failed to save preset:', e);
  }
  return preset;
}

export function loadPreset(id: string): EquipmentPreset | null {
  const presets = getPresets();
  return presets.find((p) => p.id === id) ?? null;
}

export function deletePreset(id: string): void {
  const presets = getPresets().filter((p) => p.id !== id);
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(presets));
  } catch (e) {
    console.warn('Failed to delete preset:', e);
  }
}
