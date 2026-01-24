'use client';

import { useState } from 'react';
import { EquipmentSlotType, EquipmentItem, EquipmentOptions } from '@/types/equipment';
import { Item } from '@/types/item';
import itemData from '@/data/item_data.json';

interface EquipmentOptionModalProps {
  slotType: EquipmentSlotType;
  currentItem: EquipmentItem | null;
  onSave: (item: EquipmentItem) => void;
  onClose: () => void;
}

/**
 * 장비 옵션 커스터마이징 모달
 */
export default function EquipmentOptionModal({
  slotType,
  currentItem,
  onSave,
  onClose,
}: EquipmentOptionModalProps) {
  const [selectedItemId, setSelectedItemId] = useState<string>(currentItem?.itemId || '');
  const [options, setOptions] = useState<EquipmentOptions>(currentItem?.options || {});

  const items = itemData as Item[];

  // 슬롯 타입에 맞는 아이템 필터링
  const availableItems = items.filter((item) => {
    if (item.majorCategory === 'consumable') return false;
    
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
      pendant: [], // 펜던트는 별도 처리 필요
      ring: [], // 반지는 별도 처리 필요
    };

    const categories = slotCategoryMap[slotType];
    if (categories.length === 0) return false;

    return categories.includes(item.mediumCategory);
  });

  const selectedItem = items.find((item) => item.id === selectedItemId);

  const handleOptionChange = (key: keyof EquipmentOptions, value: number) => {
    setOptions((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSave = () => {
    if (!selectedItem) return;

    const equipmentItem: EquipmentItem = {
      itemId: selectedItem.id,
      name: selectedItem.name,
      imageUrl: selectedItem.imageUrl,
      options,
    };

    onSave(equipmentItem);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-neutral-20 border-2 border-neutral-30 rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-neutral-90">장비 옵션 설정</h2>
          <button
            onClick={onClose}
            className="text-neutral-60 hover:text-neutral-90 transition-colors"
          >
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>

        {/* 아이템 선택 */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2 text-neutral-70">아이템 선택</label>
          <select
            value={selectedItemId}
            onChange={(e) => setSelectedItemId(e.target.value)}
            className="w-full px-4 py-2 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">아이템을 선택하세요</option>
            {availableItems.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name} (Lv.{item.reqLevel || '?'})
              </option>
            ))}
          </select>
        </div>

        {selectedItem && (
          <div className="mb-6 p-4 bg-neutral-10 rounded border border-neutral-30">
            <div className="flex items-center gap-4">
              <img
                src={selectedItem.imageUrl}
                alt={selectedItem.name}
                className="w-16 h-16 object-contain"
              />
              <div>
                <h3 className="text-lg font-semibold text-neutral-90">{selectedItem.name}</h3>
                <p className="text-sm text-neutral-60">
                  요구 레벨: {selectedItem.reqLevel || '?'}
                </p>
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
                className="w-full px-3 py-2 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                className="w-full px-3 py-2 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-neutral-70">물리 방어력</label>
              <input
                type="number"
                value={options.physicalDefense || ''}
                onChange={(e) =>
                  handleOptionChange('physicalDefense', parseInt(e.target.value) || 0)
                }
                className="w-full px-3 py-2 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-neutral-70">마법 방어력</label>
              <input
                type="number"
                value={options.magicDefense || ''}
                onChange={(e) =>
                  handleOptionChange('magicDefense', parseInt(e.target.value) || 0)
                }
                className="w-full px-3 py-2 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-neutral-70">최대 HP</label>
              <input
                type="number"
                value={options.maxHP || ''}
                onChange={(e) => handleOptionChange('maxHP', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-neutral-70">최대 MP</label>
              <input
                type="number"
                value={options.maxMP || ''}
                onChange={(e) => handleOptionChange('maxMP', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-neutral-70">힘</label>
              <input
                type="number"
                value={options.str || ''}
                onChange={(e) => handleOptionChange('str', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-neutral-70">민첩</label>
              <input
                type="number"
                value={options.dex || ''}
                onChange={(e) => handleOptionChange('dex', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-neutral-70">지능</label>
              <input
                type="number"
                value={options.int || ''}
                onChange={(e) => handleOptionChange('int', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-neutral-70">운</label>
              <input
                type="number"
                value={options.luk || ''}
                onChange={(e) => handleOptionChange('luk', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-neutral-70">업그레이드 횟수</label>
              <input
                type="number"
                value={options.upgradeCount || ''}
                onChange={(e) =>
                  handleOptionChange('upgradeCount', parseInt(e.target.value) || 0)
                }
                className="w-full px-3 py-2 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* 버튼 */}
        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-neutral-30 text-neutral-80 rounded hover:bg-neutral-40 transition-colors"
          >
            취소
          </button>
          <button
            onClick={handleSave}
            disabled={!selectedItem}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-neutral-30 disabled:text-neutral-50 disabled:cursor-not-allowed transition-colors"
          >
            저장
          </button>
        </div>
      </div>
    </div>
  );
}
