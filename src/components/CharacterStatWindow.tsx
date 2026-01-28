'use client';

import { useState, useMemo, useEffect, useRef } from 'react';
import Image from 'next/image';
import { JobCategoryId } from '@/types/job';
import { EquipmentSlotType, EquipmentItem } from '@/types/equipment';
import type { CharacterSnapshot } from '@/types/preset';

interface CharacterStatWindowProps {
  selectedJob: JobCategoryId | null;
  equipment: Record<EquipmentSlotType, EquipmentItem | null>;
  /** 도핑 공격력 (장비 합계에 더함) */
  dopingAttackPower?: number;
  /** 도핑 마력 (장비 마력 + 스탯 INT에 더함) */
  dopingMagicPower?: number;
  characterName?: string;
  guildName?: string;
  fame?: number;
  /** 프리셋 불러오기 시 사용. key 변경 시 이 값들로 리셋 */
  initialLevel?: number;
  initialAllocatedStats?: { str: number; dex: number; int: number; luk: number };
  initialMapleWarrior20Active?: boolean;
  onSnapshot?: (s: CharacterSnapshot) => void;
}

/**
 * 메이플랜드 스타일 캐릭터 스탯 창
 * - 기본 스탯: 전직업 4,4,4,4 / 도적만 DEX 25, 나머지 4
 * - AP: (레벨-1)*5 + 9. 70 초과 +5, 120 초과 +5 (전직 보너스). 도적 -21.
 * - 표기: 총합 (좌항+우항) — 좌항=기본+AP, 우항=장비 보너스
 */
export default function CharacterStatWindow({
  selectedJob,
  equipment,
  dopingAttackPower = 0,
  dopingMagicPower = 0,
  characterName: initialCharacterName,
  guildName = '',
  fame = 0,
  initialLevel,
  initialAllocatedStats,
  initialMapleWarrior20Active,
  onSnapshot,
}: CharacterStatWindowProps) {
  // 직업별 기본 이름
  const defaultNames: Record<JobCategoryId, string> = {
    common: '초보자',
    warrior: '전사',
    mage: '마법사',
    archer: '궁수',
    rogue: '도적',
    pirate: '해적',
    evan: '에반',
    aran: '아란',
  };

  const [characterName, setCharacterName] = useState<string>(
    initialCharacterName ?? (selectedJob ? defaultNames[selectedJob] : null) ?? '캐릭터'
  );
  const [level, setLevel] = useState<number>(initialLevel ?? 120);
  const [allocatedStats, setAllocatedStats] = useState({
    str: initialAllocatedStats?.str ?? 0,
    dex: initialAllocatedStats?.dex ?? 0,
    int: initialAllocatedStats?.int ?? 0,
    luk: initialAllocatedStats?.luk ?? 0,
  });
  const [isMapleWarrior20Active, setIsMapleWarrior20Active] = useState<boolean>(
    initialMapleWarrior20Active ?? false
  );
  /** 격수용 공격력 ? 뱃지 툴팁 표시 (호버 또는 터치로 토글) */
  const [showAttackPowerHint, setShowAttackPowerHint] = useState(false);
  /** 합마력 / 손재주 ? 뱃지 툴팁 (호버) */
  const [showMagicPowerHint, setShowMagicPowerHint] = useState(false);
  const [showCraftsmanshipHint, setShowCraftsmanshipHint] = useState(false);

  // 순수스탯 직접 입력 모드 (각 스탯별로 독립적으로 관리)
  const [isDirectInputMode, setIsDirectInputMode] = useState<{
    str: boolean;
    dex: boolean;
    int: boolean;
    luk: boolean;
  }>({
    str: false,
    dex: false,
    int: false,
    luk: false,
  });
  
  // 직접 입력 중인 임시 값 (입력 중에는 이 값을 표시)
  const [directInputValues, setDirectInputValues] = useState<{
    str: number;
    dex: number;
    int: number;
    luk: number;
  }>({
    str: 0,
    dex: 0,
    int: 0,
    luk: 0,
  });

  // initialLevel이 변경되면 (프리셋 로드 시) 레벨 업데이트
  useEffect(() => {
    if (initialLevel != null) {
      setLevel(initialLevel);
    }
  }, [initialLevel]);

  // initialMapleWarrior20Active가 변경되면 (프리셋 로드 시) 업데이트
  useEffect(() => {
    if (initialMapleWarrior20Active != null) {
      setIsMapleWarrior20Active(initialMapleWarrior20Active);
    }
  }, [initialMapleWarrior20Active]);

  const prevJobRef = useRef<JobCategoryId | null>(selectedJob);

  // initialCharacterName이 변경되면 (프리셋 로드 시) 이름 업데이트
  // 직업 변경 시에는 이름을 유지 (initialCharacterName이 undefined가 되더라도)
  useEffect(() => {
    if (initialCharacterName != null && initialCharacterName !== '') {
      setCharacterName(initialCharacterName);
    }
    // initialCharacterName이 undefined인 경우는 프리셋 해제이므로 이름 유지
  }, [initialCharacterName]);

  // 직업 변경 시 AP 분배 초기화 (프리셋 불러오기로 준 initial 은 유지)
  useEffect(() => {
    if (prevJobRef.current === selectedJob) return;
    prevJobRef.current = selectedJob;
    // initialAllocatedStats가 명시적으로 제공된 경우에만 사용 (프리셋 로드 시)
    if (initialAllocatedStats != null) {
      setAllocatedStats({
        str: initialAllocatedStats.str ?? 0,
        dex: initialAllocatedStats.dex ?? 0,
        int: initialAllocatedStats.int ?? 0,
        luk: initialAllocatedStats.luk ?? 0,
      });
      return;
    }
    // initialAllocatedStats가 undefined인 경우 (직업 변경 시) 스탯만 초기화
    setAllocatedStats({ str: 0, dex: 0, int: 0, luk: 0 });
  }, [selectedJob, initialAllocatedStats]);

  // 부모에서 프리셋 저장용 스냅샷 수집
  useEffect(() => {
    onSnapshot?.({
      characterName,
      level,
      allocatedStats: { ...allocatedStats },
      isMapleWarrior20Active,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps -- onSnapshot은 parent useCallback
  }, [characterName, level, allocatedStats.str, allocatedStats.dex, allocatedStats.int, allocatedStats.luk, isMapleWarrior20Active]);

  // 직업별 기본 스탯: 도적=DEX 25, 나머지 4,4,4,4
  const baseStats = useMemo(() => {
    if (!selectedJob || selectedJob === 'common') {
      return { str: 4, dex: 4, int: 4, luk: 4 };
    }
    if (selectedJob === 'rogue') {
      return { str: 4, dex: 25, int: 4, luk: 4 };
    }
    return { str: 4, dex: 4, int: 4, luk: 4 };
  }, [selectedJob]);

  // 레벨에 따른 총 AP
  // - 기본: (레벨-1)*5 + 9 (레벨 2~4 등 추가 보정 반영)
  // - 70 초과 시 +5, 120 초과 시 +5 (전직 보너스, AP로 지급)
  // - 도적: DEX 기본 25이므로 AP 21 적음 (25-4=21)
  const totalAp = useMemo(() => {
    let baseAp = (level - 1) * 5 + 9;
    if (level > 70) baseAp += 5;
    if (level > 120) baseAp += 5;
    if (selectedJob === 'rogue') {
      return Math.max(0, baseAp - 21);
    }
    return baseAp;
  }, [level, selectedJob]);

  // 사용 가능 AP (총 AP - 분배한 AP)
  const usedAp = allocatedStats.str + allocatedStats.dex + allocatedStats.int + allocatedStats.luk;
  const availableAp = Math.max(0, totalAp - usedAp);

  // 장비 아이템의 능력치 합산 (우항)
  // 체력, 엠피, 물리방어력, 마법방어력은 사용하지 않음
  // 한벌옷은 top과 full-body에 모두 저장되므로 full-body는 제외하여 중복 계산 방지
  const equipmentStats = useMemo(() => {
    let total = {
      attackPower: 0,
      magicPower: 0,
      str: 0,
      dex: 0,
      int: 0,
      luk: 0,
      accuracy: 0,
      evasion: 0,
    };

    Object.entries(equipment).forEach(([slotType, item]) => {
      // full-body 슬롯은 제외 (한벌옷은 top에서만 계산)
      if (slotType === 'full-body') return;
      
      if (item?.options) {
        total.attackPower += item.options.attackPower || 0;
        total.magicPower += item.options.magicPower || 0;
        total.str += item.options.str || 0;
        total.dex += item.options.dex || 0;
        total.int += item.options.int || 0;
        total.luk += item.options.luk || 0;
        total.accuracy += item.options.accuracy || 0;
        total.evasion += item.options.evasion || 0;
      }
    });

    return total;
  }, [equipment]);

  // 좌항 = 기본 + AP(내가 찍은 스탯), 메이플 용사 20 적용 시 10% 증가 (소수점 버림)
  const leftStat = useMemo(() => {
    return (stat: 'str' | 'dex' | 'int' | 'luk') => {
      const baseValue = baseStats[stat] + allocatedStats[stat];
      if (isMapleWarrior20Active) {
        return Math.floor(baseValue * 1.1);
      }
      return baseValue;
    };
  }, [baseStats, allocatedStats, isMapleWarrior20Active]);
  
  const rightStat = (stat: 'str' | 'dex' | 'int' | 'luk') => equipmentStats[stat];

  // 좌항 = 기본 + AP(내가 찍은 스탯), 우항 = 장비 보너스 / 총합 = 좌항 + 우항
  // 메이플 용사 20 적용 시 좌항에 10% 증가 적용 (소수점 버림)
  const finalStats = useMemo(() => {
    const leftStr = leftStat('str');
    const leftDex = leftStat('dex');
    const leftInt = leftStat('int');
    const leftLuk = leftStat('luk');
    
    return {
      str: leftStr + equipmentStats.str,
      dex: leftDex + equipmentStats.dex,
      int: leftInt + equipmentStats.int,
      luk: leftLuk + equipmentStats.luk,
    };
  }, [leftStat, equipmentStats]);

  const handleLevelChange = (newLevel: number) => {
    if (newLevel < 1) newLevel = 1;
    if (newLevel > 200) newLevel = 200;
    setLevel(newLevel);
  };

  const handleStatChange = (stat: 'str' | 'dex' | 'int' | 'luk', delta: number, shiftKey: boolean = false) => {
    const requestedDelta = shiftKey ? delta * 10 : delta;
    setAllocatedStats((prev) => {
      const availableAp = totalAp - (prev.str + prev.dex + prev.int + prev.luk);
      // 증가 시: 요청량이 남은 AP를 초과하면 남은 AP 전부 사용
      const actualDelta =
        requestedDelta > 0
          ? Math.min(requestedDelta, Math.max(0, availableAp))
          : requestedDelta;
      const newValue = prev[stat] + actualDelta;
      if (newValue < 0) return prev;
      if (actualDelta === 0 && requestedDelta > 0) return prev; // 증가 요청인데 쓸 AP 없음
      return { ...prev, [stat]: newValue };
    });
  };

  /** 남은 AP 전부 해당 스탯에 배분 */
  const handleAllRemainingToStat = (stat: 'str' | 'dex' | 'int' | 'luk') => {
    setAllocatedStats((prev) => {
      const availableAp = totalAp - (prev.str + prev.dex + prev.int + prev.luk);
      if (availableAp <= 0) return prev;
      return { ...prev, [stat]: prev[stat] + availableAp };
    });
  };

  /** 해당 스탯 배분 AP 전부 제거 (기본 스탯만 남김) */
  const handleClearStat = (stat: 'str' | 'dex' | 'int' | 'luk') => {
    setAllocatedStats((prev) => ({ ...prev, [stat]: 0 }));
  };

  // 순수스탯 직접 입력 처리
  const handlePureStatInput = (stat: 'str' | 'dex' | 'int' | 'luk', inputValue: number) => {
    // 입력값이 음수면 무시
    if (inputValue < 0) return;
    
    // 메이플 용사 20이 활성화된 경우, 입력값을 역산하여 실제 baseValue 계산
    let requiredAp: number;
    if (isMapleWarrior20Active) {
      // leftStat = Math.floor((baseStat + allocatedAP) * 1.1) = inputValue
      // 이를 만족하는 최소 allocatedAP를 찾아야 함
      // Math.floor((baseStat + allocatedAP) * 1.1) = inputValue 이려면:
      // (baseStat + allocatedAP) * 1.1 >= inputValue
      // (baseStat + allocatedAP) * 1.1 < inputValue + 1
      // 따라서: allocatedAP >= inputValue / 1.1 - baseStat
      //        allocatedAP < (inputValue + 1) / 1.1 - baseStat
      // 최소값: Math.ceil(inputValue / 1.1 - baseStats[stat])
      const minAp = Math.ceil(inputValue / 1.1 - baseStats[stat]);
      // 최대값: Math.floor((inputValue + 1) / 1.1 - baseStats[stat]) - 1
      const maxAp = Math.floor((inputValue + 1) / 1.1 - baseStats[stat]) - 1;
      
      // minAp가 음수면 0으로 설정
      requiredAp = Math.max(0, minAp);
      
      // maxAp가 minAp보다 작으면 (즉, 정확히 맞는 값이 없으면) minAp 사용
      // 하지만 실제로는 minAp를 사용하면 Math.floor((baseStat + minAp) * 1.1)이 inputValue와 같거나 클 수 있음
      // 정확히 맞추려면 minAp를 사용
    } else {
      // 메이플 용사 20이 비활성화된 경우: leftStat = baseStat + allocatedAP = inputValue
      requiredAp = inputValue - baseStats[stat];
    }
    
    // 현재 다른 스탯에 할당된 AP 계산
    const otherStatsAp = Object.entries(allocatedStats)
      .filter(([key]) => key !== stat)
      .reduce((sum, [, value]) => sum + value, 0);
    
    // 사용 가능한 AP 계산
    const availableApForThisStat = totalAp - otherStatsAp;
    
    // AP 제약 확인
    if (requiredAp < 0) {
      // 음수면 0으로 설정
      setAllocatedStats((prev) => ({ ...prev, [stat]: 0 }));
      return;
    }
    
    if (requiredAp > availableApForThisStat) {
      // 사용 가능한 AP를 초과하면 최대값으로 설정
      setAllocatedStats((prev) => ({ ...prev, [stat]: availableApForThisStat }));
      return;
    }
    
    // 정상적으로 설정
    setAllocatedStats((prev) => ({ ...prev, [stat]: requiredAp }));
  };

  const handleAutoAllocate = () => {
    if (!selectedJob || selectedJob === 'common') {
      // 직업이 선택되지 않았으면 LUK에 배분
      setAllocatedStats({
        str: 0,
        dex: 0,
        int: 0,
        luk: totalAp,
      });
      return;
    }

    // 직업별 주 스탯에 배분
    const mainStat: Record<JobCategoryId, 'str' | 'dex' | 'int' | 'luk'> = {
      common: 'luk',
      warrior: 'str',  // 전사: STR
      mage: 'int',     // 마법사: INT
      archer: 'dex',   // 궁수: DEX
      rogue: 'luk',    // 도적: LUK
      pirate: 'dex',   // 해적: DEX (기본값)
      evan: 'int',     // 에반: INT (마법사 계열)
      aran: 'str',     // 아란: STR (전사 계열)
    };

    const stat = mainStat[selectedJob];
    setAllocatedStats({
      str: stat === 'str' ? totalAp : 0,
      dex: stat === 'dex' ? totalAp : 0,
      int: stat === 'int' ? totalAp : 0,
      luk: stat === 'luk' ? totalAp : 0,
    });
  };

  const jobNames: Record<JobCategoryId, string> = {
    common: '공통',
    warrior: '전사',
    mage: '마법사',
    archer: '궁수',
    rogue: '도적',
    pirate: '해적',
    evan: '에반',
    aran: '아란',
  };

  return (
    <div className="relative bg-[#d3d3d3] border-4 border-[#808080] rounded-lg p-4 shadow-2xl h-full flex flex-col" style={{ fontFamily: 'monospace' }}>
      {/* 창 제목 */}
      <div className="bg-[#808080] border-b-2 border-[#555555] px-4 py-2 mb-4 rounded-t flex justify-between items-center">
        <h2 className="text-base font-bold text-white tracking-wide">CHARACTER STAT</h2>
        <button className="text-white hover:text-gray-300 transition-colors bg-[#555555] w-6 h-6 flex items-center justify-center rounded">
          <span className="text-xs font-bold">×</span>
        </button>
      </div>

      <div className="space-y-4 flex-1">
        {/* 기본 정보 */}
        <div className="bg-[#f0f0f0] p-3 rounded space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-[#ff69b4] font-semibold text-sm">이름</span>
            <input
              type="text"
              value={characterName}
              onChange={(e) => setCharacterName(e.target.value)}
              className="w-32 px-2 py-1 bg-white border border-[#808080] rounded text-[#555555] text-sm text-right"
            />
          </div>
          <div className="flex justify-between items-center">
            <span className="text-[#ff69b4] font-semibold text-sm">직업</span>
            <span className="text-[#555555] text-sm">
              {selectedJob && selectedJob !== 'common' ? jobNames[selectedJob] : '-'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-[#ff69b4] font-semibold text-sm">레벨</span>
            <input
              type="number"
              value={level}
              onChange={(e) => handleLevelChange(parseInt(e.target.value) || 1)}
              min={1}
              max={200}
              className="w-16 px-2 py-1 bg-white border border-[#808080] rounded text-[#555555] text-sm text-right"
            />
          </div>
          <div className="flex justify-between items-center">
            <span className="text-[#ff69b4] font-semibold text-sm">경험치</span>
            <span className="text-[#555555] text-sm">823366 (28%)</span>
          </div>

          {/* 전사/궁수/도적: 공격력, 명중률, 회피율 */}
          {(selectedJob === 'warrior' || selectedJob === 'archer' || selectedJob === 'rogue' || selectedJob === 'aran' || selectedJob === 'pirate') && (
            <>
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-1">
                  <span className="text-[#ff69b4] font-semibold text-sm">공격력</span>
                  <span
                    role="button"
                    tabIndex={0}
                    aria-label="공격력 설명"
                    className="relative inline-flex items-center justify-center w-4 h-4 rounded-full bg-[#808080] text-white text-xs font-bold cursor-pointer hover:bg-[#666] focus:outline-none focus:ring-2 focus:ring-[#4a90e2] select-none"
                    onMouseEnter={() => setShowAttackPowerHint(true)}
                    onMouseLeave={() => setShowAttackPowerHint(false)}
                    onClick={() => setShowAttackPowerHint((v) => !v)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setShowAttackPowerHint((v) => !v);
                      }
                    }}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-2.5 h-2.5" aria-hidden>
                      <path d="M11 18h2v-2h-2v2zm1-16C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-2.21 0-4 1.79-4 4h2c0-1.1.9-2 2-2s2 .9 2 2c0 2-3 1.75-3 5h2c0-2.25 3-2.5 3-5 0-2.21-1.79-4-4-4z" />
                    </svg>
                    {showAttackPowerHint && (
                      <span
                        className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 z-10 px-2 py-1.5 text-xs font-medium text-white bg-[#333] rounded shadow-lg text-center pointer-events-none"
                        style={{ minWidth: 'max-content' }}
                      >
                        준비 중인 기능입니다
                      </span>
                    )}
                  </span>
                </span>
                <span className="text-[#555555] text-sm">{equipmentStats.attackPower + dopingAttackPower}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[#ff69b4] font-semibold text-sm">명중률</span>
                <span className="text-[#555555] text-sm">{equipmentStats.accuracy}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[#ff69b4] font-semibold text-sm">회피율</span>
                <span className="text-[#555555] text-sm">{equipmentStats.evasion}</span>
              </div>
            </>
          )}

          {/* 마법사/에반: 합마력, 손재주, 회피율 — 합마력 = 장비+버프+도핑+순수스탯 마력 합 / 손재주 = floor(INT/10)+floor(LUK/10) */}
          {(selectedJob === 'mage' || selectedJob === 'evan') && (
            <>
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-1">
                  <span className="text-[#ff69b4] font-semibold text-sm">합마력</span>
                  <span
                    role="button"
                    tabIndex={0}
                    aria-label="합마력 설명"
                    className="relative inline-flex items-center justify-center w-4 h-4 rounded-full bg-[#808080] text-white text-xs font-bold cursor-help hover:bg-[#666] focus:outline-none focus:ring-2 focus:ring-[#4a90e2] select-none"
                    onMouseEnter={() => setShowMagicPowerHint(true)}
                    onMouseLeave={() => setShowMagicPowerHint(false)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setShowMagicPowerHint((v) => !v);
                      }
                    }}
                  >
                    ?
                    {showMagicPowerHint && (
                      <span
                        className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 z-10 px-2 py-1.5 text-xs font-medium text-white bg-[#333] rounded shadow-lg text-center pointer-events-none whitespace-nowrap"
                      >
                        장비와 버프, 도핑, 순수스탯에서 모든 마력의 합입니다.
                      </span>
                    )}
                  </span>
                </span>
                <span className="text-[#555555] text-sm">{equipmentStats.magicPower + finalStats.int + dopingMagicPower}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-1">
                  <span className="text-[#ff69b4] font-semibold text-sm">손재주</span>
                  <span
                    role="button"
                    tabIndex={0}
                    aria-label="손재주 설명"
                    className="relative inline-flex items-center justify-center w-4 h-4 rounded-full bg-[#808080] text-white text-xs font-bold cursor-help hover:bg-[#666] focus:outline-none focus:ring-2 focus:ring-[#4a90e2] select-none"
                    onMouseEnter={() => setShowCraftsmanshipHint(true)}
                    onMouseLeave={() => setShowCraftsmanshipHint(false)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setShowCraftsmanshipHint((v) => !v);
                      }
                    }}
                  >
                    ?
                    {showCraftsmanshipHint && (
                      <span
                        className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 z-10 px-2 py-1.5 text-xs font-medium text-white bg-[#333] rounded shadow-lg text-center pointer-events-none whitespace-nowrap"
                      >
                        마법 명중률에 관여하는 수치입니다.
                      </span>
                    )}
                  </span>
                </span>
                <span className="text-[#555555] text-sm">
                  {Math.floor(finalStats.int / 10) + Math.floor(finalStats.luk / 10)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[#ff69b4] font-semibold text-sm">회피율</span>
                <span className="text-[#555555] text-sm">{equipmentStats.evasion}</span>
              </div>
            </>
          )}
        </div>

        {/* Ability Point */}
        <div className="bg-[#e8e8e8] p-3 rounded">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[#ff69b4] font-semibold text-sm">ABILITY POINT</span>
            <input
              type="number"
              value={availableAp}
              readOnly
              className="w-16 px-2 py-1 bg-white border border-[#808080] rounded text-[#555555] text-sm text-right"
            />
            <button
              onClick={handleAutoAllocate}
              className="px-3 py-1 bg-[#4a90e2] text-white text-xs rounded hover:bg-[#357abd] transition-colors"
            >
              자동배분
            </button>
          </div>
        </div>

        {/* 스탯: 총합 (좌항+우항) — 좌항=기본+AP, 우항=장비 */}
        <div className="bg-[#f0f0f0] p-3 rounded space-y-2">
          {/* STR */}
          <div className="flex justify-between items-center">
            <span className="text-[#00aa00] font-semibold text-sm">STR</span>
            <div className="flex items-center gap-2">
              {isDirectInputMode.str ? (
                <>
                  <span className="text-[#555555] text-sm">순수:</span>
                  <input
                    type="number"
                    value={directInputValues.str}
                    onChange={(e) => {
                      const value = parseInt(e.target.value) || 0;
                      setDirectInputValues((prev) => ({ ...prev, str: value }));
                    }}
                    onBlur={() => {
                      handlePureStatInput('str', directInputValues.str);
                      setIsDirectInputMode((prev) => ({ ...prev, str: false }));
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handlePureStatInput('str', directInputValues.str);
                        setIsDirectInputMode((prev) => ({ ...prev, str: false }));
                        e.currentTarget.blur();
                      } else if (e.key === 'Escape') {
                        setIsDirectInputMode((prev) => ({ ...prev, str: false }));
                        e.currentTarget.blur();
                      }
                    }}
                    className="w-16 px-2 py-1 bg-white border border-[#808080] rounded text-[#555555] text-sm text-right"
                    min={0}
                    autoFocus
                  />
                  <span className="text-[#555555] text-sm">
                    +{rightStat('str')} = {directInputValues.str + rightStat('str')}
                  </span>
                </>
              ) : (
                <>
                  <span className="text-[#555555] text-sm">
                    {finalStats.str} ({leftStat('str')}+{rightStat('str')})
                  </span>
                  <button
                    onClick={() => {
                      setDirectInputValues((prev) => ({ ...prev, str: leftStat('str') }));
                      setIsDirectInputMode((prev) => ({ ...prev, str: true }));
                    }}
                    className="text-[#4a90e2] hover:text-[#357abd] text-sm font-bold"
                    title="순수스탯 직접 입력"
                  >
                    +
                  </button>
                  <button
                    onClick={(e) => {
                      if (e.ctrlKey) handleAllRemainingToStat('str');
                      else handleStatChange('str', 1, e.shiftKey);
                    }}
                    disabled={availableAp <= 0}
                    className="text-[#4a90e2] hover:text-[#357abd] disabled:text-gray-400 disabled:cursor-not-allowed"
                    title="ctrl+클릭: 남은 스탯 전부 배분, shift+클릭: 10개씩 스탯 배분"
                  >
                    ↑
                  </button>
                  <button
                    onClick={(e) => {
                      if (e.ctrlKey) handleClearStat('str');
                      else handleStatChange('str', -1, e.shiftKey);
                    }}
                    disabled={allocatedStats.str <= 0}
                    className="text-[#4a90e2] hover:text-[#357abd] disabled:text-gray-400 disabled:cursor-not-allowed"
                    title="ctrl+클릭: 해당 스탯 전부 제거, shift+클릭: 10개씩 제거"
                  >
                    ↓
                  </button>
                </>
              )}
            </div>
          </div>
          
          {/* DEX */}
          <div className="flex justify-between items-center">
            <span className="text-[#00aa00] font-semibold text-sm">DEX</span>
            <div className="flex items-center gap-2">
              {isDirectInputMode.dex ? (
                <>
                  <span className="text-[#555555] text-sm">순수:</span>
                  <input
                    type="number"
                    value={directInputValues.dex}
                    onChange={(e) => {
                      const value = parseInt(e.target.value) || 0;
                      setDirectInputValues((prev) => ({ ...prev, dex: value }));
                    }}
                    onBlur={() => {
                      handlePureStatInput('dex', directInputValues.dex);
                      setIsDirectInputMode((prev) => ({ ...prev, dex: false }));
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handlePureStatInput('dex', directInputValues.dex);
                        setIsDirectInputMode((prev) => ({ ...prev, dex: false }));
                        e.currentTarget.blur();
                      } else if (e.key === 'Escape') {
                        setIsDirectInputMode((prev) => ({ ...prev, dex: false }));
                        e.currentTarget.blur();
                      }
                    }}
                    className="w-16 px-2 py-1 bg-white border border-[#808080] rounded text-[#555555] text-sm text-right"
                    min={0}
                    autoFocus
                  />
                  <span className="text-[#555555] text-sm">
                    +{rightStat('dex')} = {directInputValues.dex + rightStat('dex')}
                  </span>
                </>
              ) : (
                <>
                  <span className="text-[#555555] text-sm">
                    {finalStats.dex} ({leftStat('dex')}+{rightStat('dex')})
                  </span>
                  <button
                    onClick={() => {
                      setDirectInputValues((prev) => ({ ...prev, dex: leftStat('dex') }));
                      setIsDirectInputMode((prev) => ({ ...prev, dex: true }));
                    }}
                    className="text-[#4a90e2] hover:text-[#357abd] text-sm font-bold"
                    title="순수스탯 직접 입력"
                  >
                    +
                  </button>
                  <button
                    onClick={(e) => {
                      if (e.ctrlKey) handleAllRemainingToStat('dex');
                      else handleStatChange('dex', 1, e.shiftKey);
                    }}
                    disabled={availableAp <= 0}
                    className="text-[#4a90e2] hover:text-[#357abd] disabled:text-gray-400 disabled:cursor-not-allowed"
                    title="ctrl+클릭: 남은 스탯 전부 배분, shift+클릭: 10개씩 스탯 배분"
                  >
                    ↑
                  </button>
                  <button
                    onClick={(e) => {
                      if (e.ctrlKey) handleClearStat('dex');
                      else handleStatChange('dex', -1, e.shiftKey);
                    }}
                    disabled={allocatedStats.dex <= 0}
                    className="text-[#4a90e2] hover:text-[#357abd] disabled:text-gray-400 disabled:cursor-not-allowed"
                    title="ctrl+클릭: 해당 스탯 전부 제거, shift+클릭: 10개씩 제거"
                  >
                    ↓
                  </button>
                </>
              )}
            </div>
          </div>
          
          {/* INT */}
          <div className="flex justify-between items-center">
            <span className="text-[#00aa00] font-semibold text-sm">INT</span>
            <div className="flex items-center gap-2">
              {isDirectInputMode.int ? (
                <>
                  <span className="text-[#555555] text-sm">순수:</span>
                  <input
                    type="number"
                    value={directInputValues.int}
                    onChange={(e) => {
                      const value = parseInt(e.target.value) || 0;
                      setDirectInputValues((prev) => ({ ...prev, int: value }));
                    }}
                    onBlur={() => {
                      handlePureStatInput('int', directInputValues.int);
                      setIsDirectInputMode((prev) => ({ ...prev, int: false }));
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handlePureStatInput('int', directInputValues.int);
                        setIsDirectInputMode((prev) => ({ ...prev, int: false }));
                        e.currentTarget.blur();
                      } else if (e.key === 'Escape') {
                        setIsDirectInputMode((prev) => ({ ...prev, int: false }));
                        e.currentTarget.blur();
                      }
                    }}
                    className="w-16 px-2 py-1 bg-white border border-[#808080] rounded text-[#555555] text-sm text-right"
                    min={0}
                    autoFocus
                  />
                  <span className="text-[#555555] text-sm">
                    +{rightStat('int')} = {directInputValues.int + rightStat('int')}
                  </span>
                </>
              ) : (
                <>
                  <span className="text-[#555555] text-sm">
                    {finalStats.int} ({leftStat('int')}+{rightStat('int')})
                  </span>
                  <button
                    onClick={() => {
                      setDirectInputValues((prev) => ({ ...prev, int: leftStat('int') }));
                      setIsDirectInputMode((prev) => ({ ...prev, int: true }));
                    }}
                    className="text-[#4a90e2] hover:text-[#357abd] text-sm font-bold"
                    title="순수스탯 직접 입력"
                  >
                    +
                  </button>
                  <button
                    onClick={(e) => {
                      if (e.ctrlKey) handleAllRemainingToStat('int');
                      else handleStatChange('int', 1, e.shiftKey);
                    }}
                    disabled={availableAp <= 0}
                    className="text-[#4a90e2] hover:text-[#357abd] disabled:text-gray-400 disabled:cursor-not-allowed"
                    title="ctrl+클릭: 남은 스탯 전부 배분, shift+클릭: 10개씩 스탯 배분"
                  >
                    ↑
                  </button>
                  <button
                    onClick={(e) => {
                      if (e.ctrlKey) handleClearStat('int');
                      else handleStatChange('int', -1, e.shiftKey);
                    }}
                    disabled={allocatedStats.int <= 0}
                    className="text-[#4a90e2] hover:text-[#357abd] disabled:text-gray-400 disabled:cursor-not-allowed"
                    title="ctrl+클릭: 해당 스탯 전부 제거, shift+클릭: 10개씩 제거"
                  >
                    ↓
                  </button>
                </>
              )}
            </div>
          </div>
          
          {/* LUK */}
          <div className="flex justify-between items-center">
            <span className="text-[#00aa00] font-semibold text-sm">LUK</span>
            <div className="flex items-center gap-2">
              {isDirectInputMode.luk ? (
                <>
                  <span className="text-[#555555] text-sm">순수:</span>
                  <input
                    type="number"
                    value={directInputValues.luk}
                    onChange={(e) => {
                      const value = parseInt(e.target.value) || 0;
                      setDirectInputValues((prev) => ({ ...prev, luk: value }));
                    }}
                    onBlur={() => {
                      handlePureStatInput('luk', directInputValues.luk);
                      setIsDirectInputMode((prev) => ({ ...prev, luk: false }));
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handlePureStatInput('luk', directInputValues.luk);
                        setIsDirectInputMode((prev) => ({ ...prev, luk: false }));
                        e.currentTarget.blur();
                      } else if (e.key === 'Escape') {
                        setIsDirectInputMode((prev) => ({ ...prev, luk: false }));
                        e.currentTarget.blur();
                      }
                    }}
                    className="w-16 px-2 py-1 bg-white border border-[#808080] rounded text-[#555555] text-sm text-right"
                    min={0}
                    autoFocus
                  />
                  <span className="text-[#555555] text-sm">
                    +{rightStat('luk')} = {directInputValues.luk + rightStat('luk')}
                  </span>
                </>
              ) : (
                <>
                  <span className="text-[#555555] text-sm">
                    {finalStats.luk} ({leftStat('luk')}+{rightStat('luk')})
                  </span>
                  <button
                    onClick={() => {
                      setDirectInputValues((prev) => ({ ...prev, luk: leftStat('luk') }));
                      setIsDirectInputMode((prev) => ({ ...prev, luk: true }));
                    }}
                    className="text-[#4a90e2] hover:text-[#357abd] text-sm font-bold"
                    title="순수스탯 직접 입력"
                  >
                    +
                  </button>
                  <button
                    onClick={(e) => {
                      if (e.ctrlKey) handleAllRemainingToStat('luk');
                      else handleStatChange('luk', 1, e.shiftKey);
                    }}
                    disabled={availableAp <= 0}
                    className="text-[#4a90e2] hover:text-[#357abd] disabled:text-gray-400 disabled:cursor-not-allowed"
                    title="ctrl+클릭: 남은 스탯 전부 배분, shift+클릭: 10개씩 스탯 배분"
                  >
                    ↑
                  </button>
                  <button
                    onClick={(e) => {
                      if (e.ctrlKey) handleClearStat('luk');
                      else handleStatChange('luk', -1, e.shiftKey);
                    }}
                    disabled={allocatedStats.luk <= 0}
                    className="text-[#4a90e2] hover:text-[#357abd] disabled:text-gray-400 disabled:cursor-not-allowed"
                    title="ctrl+클릭: 해당 스탯 전부 제거, shift+클릭: 10개씩 제거"
                  >
                    ↓
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* 메이플 용사 20 토글 버튼 */}
        <button
          onClick={() => setIsMapleWarrior20Active(!isMapleWarrior20Active)}
          className={`w-full py-2 rounded transition-colors flex items-center justify-center gap-2 ${
            isMapleWarrior20Active
              ? 'bg-[#ff8800] border-2 border-[#ffaa00]'
              : 'bg-[#555555] border-2 border-[#777777]'
          }`}
          title="메이플 용사 20"
        >
          <Image
            src="/maple_20.png"
            alt="메이플 용사 20"
            width={24}
            height={24}
            className="object-contain"
            style={{ imageRendering: 'pixelated' }}
          />
          <span className={`font-semibold ${isMapleWarrior20Active ? 'text-white' : 'text-gray-400'}`}>
            메이플 용사 20
          </span>
        </button>
      </div>
    </div>
  );
}
