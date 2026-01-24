'use client';

import { useState, useCallback, useEffect } from 'react';
import EquipmentWindow from '@/components/EquipmentWindow';
import EquipmentOptionPanel from '@/components/EquipmentOptionPanel';
import CharacterStatWindow from '@/components/CharacterStatWindow';
import PresetSaveModal from '@/components/PresetSaveModal';
import { EquipmentSlotType, EquipmentItem } from '@/types/equipment';
import { Item } from '@/types/item';
import { JobCategoryId, JobCategory } from '@/types/job';
import type { CharacterSnapshot, EquipmentPreset } from '@/types/preset';
import { getPresets, savePreset, loadPreset, deletePreset } from '@/utils/presetStorage';
import jobData from '@/data/job_data.json';
import itemData from '@/data/item_data.json';

const EMPTY_EQUIPMENT: Record<EquipmentSlotType, EquipmentItem | null> = {
  hat: null,
  medal: null,
  forehead: null,
  'eye-acc': null,
  'ear-acc': null,
  top: null,
  bottom: null,
  'full-body': null,
  weapon: null,
  shoes: null,
  gloves: null,
  belt: null,
  shield: null,
  cape: null,
  pendant: null,
  ring: null,
};

export default function EquipmentPage() {
  const [selectedSlot, setSelectedSlot] = useState<EquipmentSlotType | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobCategoryId | null>(null);
  const [presets, setPresets] = useState<EquipmentPreset[]>([]);
  const [selectedPresetId, setSelectedPresetId] = useState<string>('');
  const [presetLoadKey, setPresetLoadKey] = useState<string>('default');
  const [loadedPreset, setLoadedPreset] = useState<EquipmentPreset | null>(null);
  const [saveModalOpen, setSaveModalOpen] = useState(false);
  const [lastSnapshot, setLastSnapshot] = useState<CharacterSnapshot | null>(null);

  const jobs = jobData as JobCategory[];

  const refreshPresets = useCallback(() => {
    setPresets(getPresets());
  }, []);

  useEffect(() => {
    refreshPresets();
  }, [refreshPresets]);

  // 직업이 선택되지 않았으면 시뮬레이터 비활성화
  const isSimulatorDisabled = selectedJob === null || selectedJob === 'common';
  const [equipment, setEquipment] = useState<Record<EquipmentSlotType, EquipmentItem | null>>({
    ...EMPTY_EQUIPMENT,
  });
  const [hasFullBody, setHasFullBody] = useState(false);

  const onSnapshot = useCallback((s: CharacterSnapshot) => {
    setLastSnapshot(s);
  }, []);

  const handleSlotClick = (slotType: EquipmentSlotType) => {
    setSelectedSlot(slotType);
  };

  const handleSaveEquipment = (item: EquipmentItem) => {
    if (!selectedSlot) return;

    const items = itemData as Item[];
    const selectedItem = item.itemId ? items.find((i) => i.id === item.itemId) : null;

    // 옵션이 모두 없으면 null로 설정
    const hasAnyOption = !!(
      item.options?.attackPower ||
      item.options?.magicPower ||
      item.options?.str ||
      item.options?.dex ||
      item.options?.int ||
      item.options?.luk
    );
    
    // 아이템도 없고 옵션도 없으면 null로 설정
    if (!item.itemId && !hasAnyOption) {
      setEquipment((prev) => ({
        ...prev,
        [selectedSlot]: null,
      }));
      return;
    }

    // 상의 슬롯에서 한벌옷 선택 시 처리
    if (selectedSlot === 'top') {
      // 아이템이 한벌옷인지 확인
      const isFullBody = selectedItem?.mediumCategory === 'full-body';
      
      if (isFullBody) {
        // 한벌옷 착용 시 하의 슬롯 비활성화
        setHasFullBody(true);
        setEquipment((prev) => ({
          ...prev,
          top: item,
          'full-body': item, // 한벌옷도 full-body에 저장
          bottom: null, // 하의 제거
        }));
      } else {
        // 일반 상의 착용 시 한벌옷 해제
        if (hasFullBody) {
          setHasFullBody(false);
          setEquipment((prev) => ({
            ...prev,
            'full-body': null,
          }));
        }
        setEquipment((prev) => ({
          ...prev,
          top: item,
        }));
      }
    } else if (selectedSlot === 'bottom') {
      // 하의 착용 시 한벌옷 해제
      if (hasFullBody) {
        setHasFullBody(false);
        setEquipment((prev) => ({
          ...prev,
          'full-body': null,
          top: null, // 한벌옷 제거
        }));
      }
      setEquipment((prev) => ({
        ...prev,
        bottom: item,
      }));
    } else {
      setEquipment((prev) => ({
        ...prev,
        [selectedSlot]: item,
      }));
    }
  };

  // 선택된 슬롯의 현재 아이템 가져오기 (한벌옷 처리 포함)
  const getCurrentItem = (): EquipmentItem | null => {
    if (!selectedSlot) return null;
    
    if (selectedSlot === 'top' && hasFullBody && equipment['full-body']) {
      return equipment['full-body'];
    }
    
    return equipment[selectedSlot];
  };

  const handleJobChange = (job: JobCategoryId) => {
    // 직업 변경 시 프리셋 해제, 장비 초기화, 스탯만 초기화 (이름/레벨은 유지)
    setLoadedPreset(null);
    setSelectedPresetId('');
    setEquipment({ ...EMPTY_EQUIPMENT });
    setHasFullBody(false);
    // key 변경하지 않음 - CharacterStatWindow 내부에서 스탯만 리셋하도록 함
    if (job === 'common') {
      setSelectedJob(null);
    } else {
      setSelectedJob(job);
    }
  };

  const handleReset = () => {
    // 초기화: 프리셋 해제, 장비 초기화, 스탯 초기화
    setLoadedPreset(null);
    setSelectedPresetId('');
    setEquipment({ ...EMPTY_EQUIPMENT });
    setHasFullBody(false);
    setPresetLoadKey(`reset-${Date.now()}`); // CharacterStatWindow 리셋을 위한 key 변경
  };

  const handleLoadPreset = (presetId: string) => {
    setSelectedPresetId(presetId);
    if (!presetId) {
      setLoadedPreset(null);
      setPresetLoadKey('default');
      return;
    }
    const p = loadPreset(presetId);
    if (!p) return;
    setSelectedJob(p.job);
    setEquipment({ ...EMPTY_EQUIPMENT, ...p.equipment });
    setHasFullBody(p.hasFullBody);
    setLoadedPreset(p);
    setPresetLoadKey(`load-${p.id}`);
  };

  const handleSavePresetClick = () => {
    if (isSimulatorDisabled || !selectedJob) return;
    setSaveModalOpen(true);
  };

  const handleSavePresetConfirm = (name: string) => {
    if (!lastSnapshot || !selectedJob) return;
    savePreset(name, {
      job: selectedJob,
      equipment: { ...equipment },
      hasFullBody,
      character: lastSnapshot,
    });
    refreshPresets();
    setSaveModalOpen(false);
  };

  const handleDeletePreset = () => {
    if (!selectedPresetId) return;
    deletePreset(selectedPresetId);
    refreshPresets();
    if (loadedPreset?.id === selectedPresetId) {
      setLoadedPreset(null);
      setPresetLoadKey('default');
    }
    setSelectedPresetId('');
  };

  return (
    <div className="min-h-screen bg-neutral-0">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6 text-foreground">장비 시뮬레이터</h1>
        
        {/* 직업 선택 (상단 별도 배치) */}
        <div className="mb-6 flex flex-wrap items-end gap-4">
          <div>
            <label htmlFor="job-select" className="block text-sm font-medium mb-2 text-neutral-70">
              직업 선택
            </label>
            <select
              id="job-select"
              value={selectedJob || 'common'}
              onChange={(e) => handleJobChange(e.target.value as JobCategoryId)}
              className="w-full max-w-xs px-4 py-2 bg-neutral-20 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="common">직업을 선택하세요</option>
              {jobs
                .filter((job) => job.isReleased && job.id !== 'common' && job.id !== 'evan' && job.id !== 'aran')
                .map((job) => (
                  <option key={job.id} value={job.id}>
                    {job.name}
                  </option>
                ))}
            </select>
          </div>
          <div className="flex flex-wrap items-end gap-2">
            <div>
              <label htmlFor="preset-load" className="block text-sm font-medium mb-2 text-neutral-70">
                프리셋 불러오기
              </label>
              <select
                id="preset-load"
                value={selectedPresetId}
                onChange={(e) => handleLoadPreset(e.target.value)}
                className="min-w-[180px] px-4 py-2 bg-neutral-20 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">— 프리셋 선택 —</option>
                {presets.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({new Date(p.savedAt).toLocaleDateString('ko-KR')})
                  </option>
                ))}
              </select>
            </div>
            <button
              type="button"
              onClick={handleSavePresetClick}
              disabled={isSimulatorDisabled}
              className="px-4 py-2 rounded bg-blue-500 text-white text-sm font-medium hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              프리셋 저장
            </button>
            <button
              type="button"
              onClick={handleDeletePreset}
              disabled={!selectedPresetId}
              className="px-4 py-2 rounded bg-neutral-20 border border-neutral-30 text-neutral-70 text-sm font-medium hover:bg-neutral-30 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              선택 삭제
            </button>
            <button
              type="button"
              onClick={handleReset}
              disabled={isSimulatorDisabled}
              className="px-4 py-2 rounded bg-red-500 text-white text-sm font-medium hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              초기화
            </button>
          </div>
        </div>

        {/* 좌중우 레이아웃 */}
        {!isSimulatorDisabled && (
          <div className="flex gap-6 items-stretch">
            {/* 왼쪽: 장비창 */}
            <div className="flex-shrink-0 flex">
              <EquipmentWindow
                equipment={equipment}
                hasFullBody={hasFullBody}
                selectedJob={selectedJob || 'common'}
                onSlotClick={handleSlotClick}
                onJobChange={undefined}
              />
            </div>
            
            {/* 가운데: 캐릭터 정보 */}
            <div className="flex-shrink-0 flex">
              <CharacterStatWindow
                key={presetLoadKey}
                selectedJob={selectedJob!}
                equipment={equipment}
                characterName={loadedPreset?.character.characterName}
                initialLevel={loadedPreset?.character.level}
                initialAllocatedStats={loadedPreset?.character.allocatedStats}
                initialMapleWarrior20Active={loadedPreset?.character.isMapleWarrior20Active}
                onSnapshot={onSnapshot}
              />
            </div>
            
            {/* 오른쪽: 옵션 패널 */}
            <div className="flex-1 min-w-0">
              <div className="h-full">
                <EquipmentOptionPanel
                  slotType={selectedSlot}
                  currentItem={getCurrentItem()}
                  selectedJob={selectedJob || 'common'}
                  onSave={handleSaveEquipment}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      <PresetSaveModal
        isOpen={saveModalOpen}
        onClose={() => setSaveModalOpen(false)}
        onSave={handleSavePresetConfirm}
      />
    </div>
  );
}
