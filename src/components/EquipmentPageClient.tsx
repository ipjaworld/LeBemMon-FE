'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
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

export default function EquipmentPageClient() {
  const [selectedSlot, setSelectedSlot] = useState<EquipmentSlotType | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobCategoryId | null>(null);
  const [presets, setPresets] = useState<EquipmentPreset[]>([]);
  const [selectedPresetId, setSelectedPresetId] = useState<string>('');
  const [presetLoadKey, setPresetLoadKey] = useState<string>('default');
  const [loadedPreset, setLoadedPreset] = useState<EquipmentPreset | null>(null);
  const [saveModalOpen, setSaveModalOpen] = useState(false);
  const [lastSnapshot, setLastSnapshot] = useState<CharacterSnapshot | null>(null);
  /** 버프/도핑: 버프, 도핑1, 도핑2 (격수=공격력에만, 법사=마력에만 반영) */
  const [buffValue, setBuffValue] = useState<number>(0);
  const [doping1, setDoping1] = useState<number>(0);
  const [doping2, setDoping2] = useState<number>(0);
  /** 도핑 입력 패널 표시 여부 */
  const [showDopingPanel, setShowDopingPanel] = useState(false);
  const dopingPanelRef = useRef<HTMLDivElement>(null);
  const leftColumnRef = useRef<HTMLDivElement>(null);

  const jobs = jobData as JobCategory[];

  const refreshPresets = useCallback(() => {
    setPresets(getPresets());
  }, []);

  useEffect(() => {
    refreshPresets();
  }, [refreshPresets]);

  // 도핑 패널 외부 클릭 시 닫기 (왼쪽 장비 영역·패널 밖 클릭 시)
  useEffect(() => {
    if (!showDopingPanel) return;
    const handleClickOutside = (e: MouseEvent) => {
      const el = e.target as Node;
      if (dopingPanelRef.current?.contains(el) || leftColumnRef.current?.contains(el)) return;
      setShowDopingPanel(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showDopingPanel]);

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

    const hasAnyOption = !!(
      item.options?.attackPower ||
      item.options?.magicPower ||
      item.options?.str ||
      item.options?.dex ||
      item.options?.int ||
      item.options?.luk
    );
    
    if (!item.itemId && !hasAnyOption) {
      setEquipment((prev) => ({
        ...prev,
        [selectedSlot]: null,
      }));
      return;
    }

    if (selectedSlot === 'top') {
      const isFullBody = selectedItem?.mediumCategory === 'full-body';
      
      if (isFullBody) {
        setHasFullBody(true);
        setEquipment((prev) => ({
          ...prev,
          top: item,
          'full-body': item,
          bottom: null,
        }));
      } else {
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
      if (hasFullBody) {
        setHasFullBody(false);
        setEquipment((prev) => ({
          ...prev,
          'full-body': null,
          top: null,
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

  const getCurrentItem = (): EquipmentItem | null => {
    if (!selectedSlot) return null;
    
    if (selectedSlot === 'top' && hasFullBody && equipment['full-body']) {
      return equipment['full-body'];
    }
    
    return equipment[selectedSlot];
  };

  const handleJobChange = (job: JobCategoryId) => {
    setLoadedPreset(null);
    setSelectedPresetId('');
    setEquipment({ ...EMPTY_EQUIPMENT });
    setHasFullBody(false);
    if (job === 'common') {
      setSelectedJob(null);
    } else {
      setSelectedJob(job);
    }
  };

  const handleReset = () => {
    setLoadedPreset(null);
    setSelectedPresetId('');
    setEquipment({ ...EMPTY_EQUIPMENT });
    setHasFullBody(false);
    setPresetLoadKey(`reset-${Date.now()}`);
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

        {!isSimulatorDisabled && (
          <div className="flex gap-6 items-stretch">
            {/* 왼쪽 장비 영역: 도핑 슬롯은 장비창 그리드 내 반지 윗칸에 있음 */}
            <div ref={leftColumnRef} className="flex-shrink-0 flex relative">
              {showDopingPanel && (
                <div
                  ref={dopingPanelRef}
                  className="absolute top-14 right-0 z-20 w-56 bg-neutral-20 border-2 border-neutral-40 rounded-lg shadow-xl p-3 space-y-3"
                >
                  <div className="text-sm font-semibold text-neutral-80">버프/도핑</div>
                  <div>
                    <label className="block text-xs font-medium text-neutral-70 mb-1">버프</label>
                    <input
                      type="number"
                      min={0}
                      value={buffValue || ''}
                      onChange={(e) => setBuffValue(parseInt(e.target.value, 10) || 0)}
                      className="w-full px-2 py-1.5 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 text-sm"
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-neutral-70 mb-1">도핑1</label>
                    <input
                      type="number"
                      min={0}
                      value={doping1 || ''}
                      onChange={(e) => setDoping1(parseInt(e.target.value, 10) || 0)}
                      className="w-full px-2 py-1.5 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 text-sm"
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-neutral-70 mb-1">도핑2</label>
                    <input
                      type="number"
                      min={0}
                      value={doping2 || ''}
                      onChange={(e) => setDoping2(parseInt(e.target.value, 10) || 0)}
                      className="w-full px-2 py-1.5 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 text-sm"
                      placeholder="0"
                    />
                  </div>
                </div>
              )}
              <EquipmentWindow
                equipment={equipment}
                hasFullBody={hasFullBody}
                selectedJob={selectedJob || 'common'}
                onSlotClick={handleSlotClick}
                onJobChange={undefined}
                onDopingSlotClick={() => setShowDopingPanel((v) => !v)}
              />
            </div>

            <div className="flex-shrink-0 flex">
              <CharacterStatWindow
                key={presetLoadKey}
                selectedJob={selectedJob!}
                equipment={equipment}
                dopingAttackPower={
                  selectedJob === 'warrior' || selectedJob === 'archer' || selectedJob === 'rogue' || selectedJob === 'aran' || selectedJob === 'pirate'
                    ? buffValue + doping1 + doping2
                    : 0
                }
                dopingMagicPower={
                  selectedJob === 'mage' || selectedJob === 'evan'
                    ? buffValue + doping1 + doping2
                    : 0
                }
                characterName={loadedPreset?.character.characterName}
                initialLevel={loadedPreset?.character.level}
                initialAllocatedStats={loadedPreset?.character.allocatedStats}
                initialMapleWarrior20Active={loadedPreset?.character.isMapleWarrior20Active}
                onSnapshot={onSnapshot}
              />
            </div>
            
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
