'use client';

import { useState, useMemo } from 'react';
import { JobCategory, JobCategoryId } from '@/domains/entities/job/types/job';
import { EquipmentSlotType, EquipmentSlot, EquipmentItem, JobEquipment, hasItem, hasOptions } from '@/domains/features/equipment/types/equipment';
import jobData from '@/domains/entities/job/data/job_data.json';

interface EquipmentWindowProps {
  equipment: Record<EquipmentSlotType, EquipmentItem | null>;
  hasFullBody: boolean;
  selectedJob: JobCategoryId | null;
  onSlotClick?: (slotType: EquipmentSlotType) => void;
  onJobChange?: (job: JobCategoryId | null) => void; // 선택적, 상단에서 관리할 수도 있음
  /** 반지 윗칸(도핑) 슬롯 클릭 시 */
  onDopingSlotClick?: () => void;
}

/**
 * 메이플랜드 스타일 장비창 컴포넌트
 */
export default function EquipmentWindow({
  equipment,
  hasFullBody,
  selectedJob,
  onSlotClick,
  onJobChange,
  onDopingSlotClick,
}: EquipmentWindowProps) {

  const jobs = jobData as JobCategory[];

  // 6x5 그리드 레이아웃 정의
  const gridLayout: (EquipmentSlot | null)[][] = useMemo(() => {
    const layout: (EquipmentSlot | null)[][] = Array(6).fill(null).map(() => Array(5).fill(null));

    // 1행: 빈칸, 모자
    layout[0][0] = null;
    layout[0][1] = { type: 'hat', label: '모자', position: { row: 0, col: 1 }, enabled: true };

    // 2행: 칭호, 얼굴장식, 빈칸, 반지, 반지
    layout[1][0] = { type: 'medal', label: '칭호', position: { row: 1, col: 0 }, enabled: true };
    layout[1][1] = { type: 'forehead', label: '얼굴장식', position: { row: 1, col: 1 }, enabled: true };
    layout[1][2] = null;
    layout[1][3] = { type: 'ring', label: '반지', position: { row: 1, col: 3 }, enabled: true };
    layout[1][4] = { type: 'ring', label: '반지', position: { row: 1, col: 4 }, enabled: true };

    // 3행: 빈칸, 빈칸, 눈장식, 귀장식, 빈칸
    layout[2][0] = null;
    layout[2][1] = null;
    layout[2][2] = { type: 'eye-acc', label: '눈장식', position: { row: 2, col: 2 }, enabled: true };
    layout[2][3] = { type: 'ear-acc', label: '귀장식', position: { row: 2, col: 3 }, enabled: true };
    layout[2][4] = null;

    // 4행: 망토, 상의, 펜던트, 무기, 방패
    layout[3][0] = { type: 'cape', label: '망토', position: { row: 3, col: 0 }, enabled: true };
    layout[3][1] = { type: 'top', label: '상의', position: { row: 3, col: 1 }, enabled: true };
    layout[3][2] = { type: 'pendant', label: '펜던트', position: { row: 3, col: 2 }, enabled: true };
    layout[3][3] = { type: 'weapon', label: '무기', position: { row: 3, col: 3 }, enabled: true };
    layout[3][4] = { type: 'shield', label: '방패', position: { row: 3, col: 4 }, enabled: true };

    // 5행: 장갑, 하의, 벨트, 반지, 반지
    layout[4][0] = { type: 'gloves', label: '장갑', position: { row: 4, col: 0 }, enabled: true };
    layout[4][1] = { type: 'bottom', label: '하의', position: { row: 4, col: 1 }, enabled: !hasFullBody };
    layout[4][2] = { type: 'belt', label: '허리띠', position: { row: 4, col: 2 }, enabled: true };
    layout[4][3] = { type: 'ring', label: '반지', position: { row: 4, col: 3 }, enabled: true };
    layout[4][4] = { type: 'ring', label: '반지', position: { row: 4, col: 4 }, enabled: true };

    // 6행: 빈칸, 빈칸, 신발, 이후 빈칸
    layout[5][0] = null;
    layout[5][1] = null;
    layout[5][2] = { type: 'shoes', label: '신발', position: { row: 5, col: 2 }, enabled: true };
    layout[5][3] = null;
    layout[5][4] = null;

    // 한벌옷 착용 시 하의 슬롯 비활성화
    if (hasFullBody && layout[4][1]) {
      layout[4][1].enabled = false;
    }

    return layout;
  }, [hasFullBody]);

  const handleSlotClick = (slot: EquipmentSlot) => {
    if (!slot.enabled) return;
    if (onSlotClick && slot.type) {
      onSlotClick(slot.type);
    }
  };

  return (
    <div className="flex flex-col items-center h-full">
      {/* 장비창 UI */}
      <div className="relative bg-[#d3d3d3] border-4 border-[#808080] rounded-lg p-4 shadow-2xl h-full flex flex-col">
        {/* 창 제목 */}
        <div className="bg-[#808080] border-b-2 border-[#555555] px-4 py-2 mb-4 rounded-t flex justify-between items-center">
          <h2 className="text-base font-bold text-white tracking-wide">EQUIPMENT INVENTORY</h2>
          <button className="text-white hover:text-gray-300 transition-colors bg-[#555555] w-6 h-6 flex items-center justify-center rounded">
            <span className="text-xs font-bold">×</span>
          </button>
        </div>

        {/* 6x5 그리드 */}
        <div className="grid grid-cols-5 gap-1 w-[400px] bg-[#f0f0f0] p-2 rounded">
          {gridLayout.map((row, rowIndex) =>
            row.map((slot, colIndex) => {
              // 반지 윗칸(row 0, col 4): 도핑 슬롯 (장비처럼 한 칸 차지)
              if (rowIndex === 0 && colIndex === 4 && onDopingSlotClick) {
                return (
                  <button
                    key={`${rowIndex}-${colIndex}`}
                    type="button"
                    onClick={onDopingSlotClick}
                    className="aspect-square relative border-2 border-[#e0559a] rounded bg-[#ff69b4] hover:bg-[#ff85c1] cursor-pointer flex flex-col items-center justify-center p-1 transition-colors"
                    style={{ boxShadow: 'inset 0 0 4px rgba(224, 85, 154, 0.4)' }}
                    aria-label="도핑 입력"
                    title="도핑"
                  >
                    <span className="text-white text-lg font-bold">?</span>
                  </button>
                );
              }
              if (!slot) {
                return (
                  <div
                    key={`${rowIndex}-${colIndex}`}
                    className="aspect-square bg-transparent border border-transparent"
                  />
                );
              }

              // 한벌옷 착용 시 상의 슬롯에 한벌옷 아이템 표시
              let slotItem: EquipmentItem | null = null;
              if (slot.type) {
                if (slot.type === 'top' && hasFullBody && equipment['full-body']) {
                  slotItem = equipment['full-body'];
                } else {
                  slotItem = equipment[slot.type];
                }
              }
              const isEnabled = slot.enabled;
              const hasItemInSlot = hasItem(slotItem);
              const hasCustomOptions = hasOptions(slotItem);

              return (
                <div
                  key={`${rowIndex}-${colIndex}`}
                  onClick={() => handleSlotClick(slot)}
                  className={`
                    aspect-square relative border-2 rounded
                    ${isEnabled
                      ? hasCustomOptions && !hasItemInSlot
                        ? 'bg-[#b0d4ff] border-[#ffaa00] cursor-pointer hover:bg-[#8fc5ff] transition-colors'
                        : 'bg-[#b0d4ff] border-[#4a90e2] cursor-pointer hover:bg-[#8fc5ff] transition-colors'
                      : 'bg-[#ffb0b0] border-[#e24a4a] cursor-not-allowed opacity-60'
                    }
                    flex flex-col items-center justify-center p-1
                  `}
                  style={{
                    boxShadow: isEnabled
                      ? hasCustomOptions && !hasItemInSlot
                        ? 'inset 0 0 4px rgba(255, 170, 0, 0.4)'
                        : 'inset 0 0 4px rgba(74, 144, 226, 0.3)'
                      : 'inset 0 0 4px rgba(226, 74, 74, 0.2)',
                  }}
                >
                  {hasItemInSlot && slotItem ? (
                    <>
                      <img
                        src={slotItem.imageUrl}
                        alt={slotItem.name}
                        className="w-full h-full object-contain"
                        style={{ imageRendering: 'pixelated' }}
                      />
                      <span className="absolute bottom-0 left-0 right-0 bg-black/80 text-white text-[9px] px-1 truncate text-center">
                        {slotItem.name}
                      </span>
                    </>
                  ) : hasCustomOptions ? (
                    <div className="flex flex-col items-center justify-center w-full h-full">
                      <span className="text-[11px] text-[#555555] text-center px-1 font-semibold mb-1">
                        {slot.label}
                      </span>
                      <span className="text-[9px] text-[#ff8800] text-center px-1 font-bold">
                        옵션 설정됨
                      </span>
                    </div>
                  ) : (
                    <span className="text-[10px] text-[#555555] text-center px-1 font-semibold">
                      {slot.label}
                    </span>
                  )}
                </div>
              );
            })
          )}
        </div>
        {/* 높이 맞추기를 위한 빈 공간 */}
        <div className="flex-1"></div>
      </div>
    </div>
  );
}
