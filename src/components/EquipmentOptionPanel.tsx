'use client';

import { useState, useEffect, useMemo, useRef } from 'react';
import { EquipmentSlotType, EquipmentItem, EquipmentOptions } from '@/types/equipment';
import { Item } from '@/types/item';
import { JobCategoryId } from '@/types/job';
import itemData from '@/data/item_data.json';
import ItemComboBox from '@/components/ItemComboBox';

interface EquipmentOptionPanelProps {
  slotType: EquipmentSlotType | null;
  currentItem: EquipmentItem | null;
  selectedJob: JobCategoryId | null;
  onSave: (item: EquipmentItem) => void;
}

/**
 * 장비 옵션 커스터마이징 패널 (오른쪽 사이드 패널)
 */
export default function EquipmentOptionPanel({
  slotType,
  currentItem,
  selectedJob,
  onSave,
}: EquipmentOptionPanelProps) {
  const [selectedItemId, setSelectedItemId] = useState<string>('');
  const [options, setOptions] = useState<EquipmentOptions>({});
  const isInitializedRef = useRef(false);
  const prevSlotTypeRef = useRef<EquipmentSlotType | null>(null);

  const items = itemData as Item[];

  // 슬롯이 변경되거나 currentItem이 외부에서 변경될 때만 상태 동기화
  useEffect(() => {
    // 슬롯이 변경된 경우 초기화
    if (prevSlotTypeRef.current !== slotType) {
      prevSlotTypeRef.current = slotType;
      isInitializedRef.current = false;
    }

    // 슬롯이 없으면 초기화하지 않음
    if (!slotType) return;

    // 아직 초기화되지 않았거나 currentItem이 변경된 경우에만 동기화
    if (!isInitializedRef.current || currentItem) {
      const currentItemId = currentItem?.itemId || '';
      const currentOptions = currentItem?.options || {};
      
      setSelectedItemId(currentItemId);
      setOptions(currentOptions);
      isInitializedRef.current = true;
    }
  }, [slotType, currentItem?.itemId]);

  // 무기 카테고리 한글 매핑
  const getWeaponCategoryName = (category: string): string => {
    const categoryMap: Record<string, string> = {
      'one-handed-sword': '한손검',
      'two-handed-sword': '두손검',
      'one-handed-axe': '한손도끼',
      'two-handed-axe': '두손도끼',
      'one-handed-blunt': '한손둔기',
      'two-handed-blunt': '두손둔기',
      'spear': '창',
      'polearm': '폴암',
      'bow': '활',
      'crossbow': '석궁',
      'wand': '완드',
      'staff': '스태프',
      'dagger': '단검',
      'gauntlet': '아대',
      'knuckle': '너클',
      'gun': '총',
    };
    return categoryMap[category] || category;
  };

  // 직업별 무기 필터링 함수
  const isWeaponAllowedForJob = (weaponCategory: string, job: JobCategoryId | null): boolean => {
    // 무기가 아닌 경우는 직업 제한 없음
    if (slotType !== 'weapon') return true;
    
    // 직업이 선택되지 않았으면 모든 무기 허용
    if (!job || job === 'common') return true;

    // 직업별 무기 매핑
    const jobWeaponMap: Record<JobCategoryId, string[]> = {
      common: [], // 공통은 모든 무기 사용 가능
      warrior: [
        'one-handed-sword',
        'two-handed-sword',
        'one-handed-axe',
        'two-handed-axe',
        'one-handed-blunt',
        'two-handed-blunt',
        'spear',
        'polearm',
      ],
      mage: ['wand', 'staff'],
      archer: ['bow', 'crossbow'],
      rogue: ['dagger', 'gauntlet'],
      pirate: ['knuckle', 'gun'],
      evan: ['wand', 'staff'], // 에반도 마법사 계열
      aran: ['polearm'], // 아란은 폴암
    };

    const allowedWeapons = jobWeaponMap[job] || [];
    
    // 해당 직업의 허용 무기 목록에 있는지 확인
    return allowedWeapons.includes(weaponCategory);
  };

  // 슬롯 타입에 맞는 아이템 필터링
  const availableItems = useMemo(() => {
    return items.filter((item) => {
      if (!slotType || item.majorCategory === 'consumable') return false;
      
      // 슬롯 타입과 아이템 카테고리 매핑
      const slotCategoryMap: Record<EquipmentSlotType, string[]> = {
        hat: ['hat'],
        medal: [], // 칭호는 별도 처리 필요
        forehead: [], // 얼굴장식은 별도 처리 필요
        'eye-acc': [], // 눈장식은 별도 처리 필요
        'ear-acc': ['earring'],
        top: ['top', 'full-body'], // 상의 슬롯에서 한벌옷도 선택 가능
        bottom: ['bottom'],
        'full-body': ['full-body'], // 한벌옷은 상의 슬롯에서 선택
        weapon: [
          'one-handed-sword',
          'two-handed-sword',
          'one-handed-axe',
          'two-handed-axe',
          'one-handed-blunt',
          'two-handed-blunt',
          'spear',
          'polearm',
          'bow',
          'crossbow',
          'wand',
          'staff',
          'dagger',
          'gauntlet',
          'knuckle',
          'gun',
        ],
        shoes: ['shoes'],
        gloves: ['gloves'],
        belt: [], // 허리띠는 별도 처리 필요
        shield: ['shield'],
        cape: ['cape'],
        pendant: ['pendant'], // 펜던트
        ring: [], // 반지는 별도 처리 필요
      };

      const categories = slotCategoryMap[slotType];
      if (categories.length === 0) return false;

      // 슬롯 타입에 맞는 카테고리인지 확인
      if (!categories.includes(item.mediumCategory)) return false;

      // 무기인 경우 직업별 필터링
      if (slotType === 'weapon') {
        if (!isWeaponAllowedForJob(item.mediumCategory, selectedJob)) return false;
      }

      return true;
    });
  }, [slotType, selectedJob, items]);

  const selectedItem = useMemo(() => {
    return items.find((item) => item.id === selectedItemId);
  }, [selectedItemId, items]);

  const handleOptionChange = (key: keyof EquipmentOptions, value: number) => {
    setOptions((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleItemChange = (itemId: string) => {
    setSelectedItemId(itemId);
    const item = items.find((i) => i.id === itemId);
    if (item) {
      // 아이템 변경 시 옵션 초기화 (또는 기존 옵션 유지)
      setOptions({});
    }
  };

  // 옵션이나 아이템 변경 시 저장
  // 무한 루프 방지를 위해 useRef로 이전 값 추적
  const prevSaveKeyRef = useRef<string>('');
  
  useEffect(() => {
    if (!slotType || !isInitializedRef.current) return;
    
    const optionsKey = JSON.stringify(options);
    const saveKey = `${selectedItemId}|${optionsKey}`;
    
    // 실제로 변경되었을 때만 저장
    if (prevSaveKeyRef.current === saveKey) {
      return;
    }
    
    prevSaveKeyRef.current = saveKey;
    
    // 옵션이 하나라도 있으면 저장
    const hasAnyOption = !!(
      options.attackPower ||
      options.magicPower ||
      options.str ||
      options.dex ||
      options.int ||
      options.luk
    );
    
    const selectedItem = items.find((item) => item.id === selectedItemId);
    
    if (selectedItem) {
      // 아이템이 선택된 경우
      const equipmentItem: EquipmentItem = {
        itemId: selectedItem.id,
        name: selectedItem.name,
        imageUrl: selectedItem.imageUrl,
        options: hasAnyOption ? options : undefined,
      };
      onSave(equipmentItem);
    } else if (hasAnyOption) {
      // 아이템이 없지만 옵션이 있는 경우
      const equipmentItem: EquipmentItem = {
        itemId: '',
        name: '',
        imageUrl: '',
        options,
      };
      onSave(equipmentItem);
    } else {
      // 아이템도 없고 옵션도 없는 경우 - null로 처리
      const equipmentItem: EquipmentItem = {
        itemId: '',
        name: '',
        imageUrl: '',
        options: undefined,
      };
      onSave(equipmentItem);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedItemId, options, slotType]);

  if (!slotType) {
    return (
      <div className="w-full h-full bg-neutral-20 border-2 border-neutral-30 rounded-lg p-6 flex items-center justify-center">
        <p className="text-neutral-60 text-center">장비 슬롯을 선택하세요</p>
      </div>
    );
  }

  // 슬롯 타입 한글 매핑
  const slotLabels: Record<EquipmentSlotType, string> = {
    'hat': '모자',
    'medal': '칭호',
    'forehead': '얼굴장식',
    'eye-acc': '눈장식',
    'ear-acc': '귀장식',
    'top': '상의',
    'bottom': '하의',
    'full-body': '한벌옷',
    'weapon': '무기',
    'shoes': '신발',
    'gloves': '장갑',
    'belt': '허리띠',
    'shield': '방패',
    'cape': '망토',
    'pendant': '펜던트',
    'ring': '반지',
  };

  return (
    <div className="w-full h-full bg-neutral-20 border-2 border-neutral-30 rounded-lg p-6 overflow-y-auto">

      {/* 선택한 슬롯 표시 */}
      <div className="mb-6 pb-4 border-b border-neutral-30">
        <div className="text-sm text-neutral-60 mb-1">선택한 슬롯</div>
        <div className="text-lg font-semibold text-neutral-90">
          {slotType ? slotLabels[slotType] : '-'}
        </div>
      </div>

      {/* 아이템 선택 */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2 text-neutral-70">아이템 선택</label>
        <ItemComboBox
          items={availableItems}
          value={selectedItemId}
          onChange={handleItemChange}
          placeholder="아이템을 선택하세요"
        />
      </div>

      {/* 아이템 정보 및 썸네일 */}
      {selectedItem && (
        <div className="mb-6 p-4 bg-neutral-10 rounded border border-neutral-30">
          <h3 className="text-lg font-semibold text-neutral-90 mb-4">{selectedItem.name}</h3>
          <div className="flex gap-4">
            <div className="flex-shrink-0">
              <img
                src={selectedItem.imageUrl}
                alt={selectedItem.name}
                className="w-24 h-24 object-contain"
                style={{ imageRendering: 'pixelated' }}
              />
            </div>
            <div className="flex-1 space-y-2">
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span className="text-neutral-60">REQLEV:</span>
                  <span className="ml-2 text-neutral-90">{selectedItem.reqLevel || 0}</span>
                </div>
                <div>
                  <span className="text-neutral-60">REQSTR:</span>
                  <span className="ml-2 text-neutral-90">{selectedItem.reqStr || 0}</span>
                </div>
                <div>
                  <span className="text-neutral-60">REQDEX:</span>
                  <span className="ml-2 text-neutral-90">{selectedItem.reqDex || 0}</span>
                </div>
                <div>
                  <span className="text-neutral-60">REQINT:</span>
                  <span className="ml-2 text-neutral-90">{selectedItem.reqInt || 0}</span>
                </div>
                <div>
                  <span className="text-neutral-60">REQLUK:</span>
                  <span className="ml-2 text-neutral-90">{selectedItem.reqLuk || 0}</span>
                </div>
                <div>
                  <span className="text-neutral-60">REQPOP:</span>
                  <span className="ml-2 text-neutral-90">{selectedItem.reqPop || 0}</span>
                </div>
              </div>
              {selectedItem.mediumCategory && slotType === 'weapon' && (
                <div className="text-sm">
                  <span className="text-neutral-60">무기분류:</span>
                  <span className="ml-2 text-neutral-90">
                    {getWeaponCategoryName(selectedItem.mediumCategory)}
                  </span>
                </div>
              )}
              {selectedItem.attackSpeed && (
                <div className="text-sm">
                  <span className="text-neutral-60">공격속도:</span>
                  <span className="ml-2 text-neutral-90">{selectedItem.attackSpeed}</span>
                </div>
              )}
              <div className="grid grid-cols-2 gap-2 text-sm">
                {selectedItem.attackPower !== undefined && (
                  <div>
                    <span className="text-neutral-60">공격력:</span>
                    <span className="ml-2 text-neutral-90">{selectedItem.attackPower}</span>
                  </div>
                )}
                {selectedItem.magicPower !== undefined && (
                  <div>
                    <span className="text-neutral-60">마력:</span>
                    <span className="ml-2 text-neutral-90">{selectedItem.magicPower}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 옵션 설정 */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-4 text-neutral-90">추가 옵션</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1 text-neutral-70">공격력</label>
            <input
              type="number"
              value={options.attackPower || ''}
              onChange={(e) =>
                handleOptionChange('attackPower', parseInt(e.target.value) || 0)
              }
              className="w-full px-2 py-1 text-sm bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-neutral-70">마력</label>
            <input
              type="number"
              value={options.magicPower || ''}
              onChange={(e) =>
                handleOptionChange('magicPower', parseInt(e.target.value) || 0)
              }
              className="w-full px-2 py-1 text-sm bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-neutral-70">힘</label>
            <input
              type="number"
              value={options.str || ''}
              onChange={(e) => handleOptionChange('str', parseInt(e.target.value) || 0)}
              className="w-full px-2 py-1 text-sm bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-neutral-70">민첩</label>
            <input
              type="number"
              value={options.dex || ''}
              onChange={(e) => handleOptionChange('dex', parseInt(e.target.value) || 0)}
              className="w-full px-2 py-1 text-sm bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-neutral-70">지능</label>
            <input
              type="number"
              value={options.int || ''}
              onChange={(e) => handleOptionChange('int', parseInt(e.target.value) || 0)}
              className="w-full px-2 py-1 text-sm bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-neutral-70">운</label>
            <input
              type="number"
              value={options.luk || ''}
              onChange={(e) => handleOptionChange('luk', parseInt(e.target.value) || 0)}
              className="w-full px-2 py-1 text-sm bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
