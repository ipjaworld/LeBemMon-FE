'use client';

import { useState, useMemo, useEffect, useRef } from 'react';
import MonsterCard from '@/components/MonsterCard';
import MonsterDetailModal from '@/components/MonsterDetailModal';
import Footer from '@/components/Footer';
import LevelRangeSettingsButton from '@/components/LevelRangeSettingsButton';
import { Monster } from '@/types/monster';
import { Region } from '@/types/region';
import { Item } from '@/types/item';
import regionData from '@/data/region_data.json';
import itemData from '@/data/item_data.json';

const LEVEL_RANGE_SETTINGS_STORAGE_KEY = 'rebemon:levelRangeSettings:v1';
const DEFAULT_LEVEL_RANGE_SETTINGS = {
  showRebemonOnly: true,
  customLowerOffset: 10,
  customUpperOffset: 10,
} as const;

type StoredLevelRangeSettings = {
  showRebemonOnly?: boolean;
  customLowerOffset?: number;
  customUpperOffset?: number;
};

type MonsterWithExpiring = Monster & {
  isExpiringSoon: boolean;
};

type SortOption = 'level-asc' | 'level-desc' | 'exp-asc' | 'exp-desc' | 'hp-per-exp-asc' | 'hp-per-exp-desc' | 'region-asc' | 'name-asc' | 'name-desc';

interface MonsterSearchProps {
  monsters: Monster[];
}

export default function MonsterSearch({ monsters }: MonsterSearchProps) {
  const [level, setLevel] = useState<number | ''>('');
  const [showRebemonOnly, setShowRebemonOnly] = useState(true);
  const [levelRangeLowerOffset, setLevelRangeLowerOffset] = useState(10);
  const [levelRangeUpperOffset, setLevelRangeUpperOffset] = useState(10);
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [isQuickSelectOpen, setIsQuickSelectOpen] = useState(false);
  const quickSelectRef = useRef<HTMLDivElement>(null);

  // 외부 클릭 감지
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        quickSelectRef.current &&
        !quickSelectRef.current.contains(event.target as Node)
      ) {
        setIsQuickSelectOpen(false);
      }
    };

    if (isQuickSelectOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isQuickSelectOpen]);

  // 필터 상태
  const [searchName, setSearchName] = useState('');
  const [minLevel, setMinLevel] = useState<number | ''>('');
  const [maxLevel, setMaxLevel] = useState<number | ''>('');
  const [minHp, setMinHp] = useState<number | ''>('');
  const [maxHp, setMaxHp] = useState<number | ''>('');
  const [minExp, setMinExp] = useState<number | ''>('');
  const [maxExp, setMaxExp] = useState<number | ''>('');
  const [showExpiringOnly, setShowExpiringOnly] = useState(false);
  const [showRecommendedOnly, setShowRecommendedOnly] = useState(false);
  const [selectedRegions, setSelectedRegions] = useState<string[]>([]);

  // 정렬 상태
  const [sortBy, setSortBy] = useState<SortOption>('level-asc');

  // 선택된 몬스터 (모달용)
  const [selectedMonster, setSelectedMonster] = useState<Monster | null>(null);
  
  // 최근 확인한 몬스터 목록
  const [recentMonsters, setRecentMonsters] = useState<Monster[]>([]);
  
  // 지역 필터 펼쳐보기 상태
  const [isRegionFilterExpanded, setIsRegionFilterExpanded] = useState(false);
  const [shouldShowRegionExpandButton, setShouldShowRegionExpandButton] = useState(false);
  const regionFilterContainerRef = useRef<HTMLDivElement>(null);

  const didLoadLevelRangeSettingsRef = useRef(false);

  const regions = regionData as Region[];
  const items = itemData as Item[];

  // 레벨 범위(레범몬 on/off + 커스텀 범위) 로드
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (didLoadLevelRangeSettingsRef.current) return;

    try {
      const raw = localStorage.getItem(LEVEL_RANGE_SETTINGS_STORAGE_KEY);
      if (!raw) {
        didLoadLevelRangeSettingsRef.current = true;
        return;
      }

      const parsedUnknown = JSON.parse(raw) as unknown;
      if (!parsedUnknown || typeof parsedUnknown !== 'object' || Array.isArray(parsedUnknown)) {
        throw new Error('Invalid stored shape');
      }
      const parsed = parsedUnknown as StoredLevelRangeSettings;
      if (typeof parsed.showRebemonOnly === 'boolean') {
        setShowRebemonOnly(parsed.showRebemonOnly);
      }
      if (typeof parsed.customLowerOffset === 'number' && Number.isFinite(parsed.customLowerOffset)) {
        setLevelRangeLowerOffset(Math.max(0, Math.min(200, Math.trunc(parsed.customLowerOffset))));
      }
      if (typeof parsed.customUpperOffset === 'number' && Number.isFinite(parsed.customUpperOffset)) {
        setLevelRangeUpperOffset(Math.max(0, Math.min(200, Math.trunc(parsed.customUpperOffset))));
      }
    } catch (error) {
      console.warn('Failed to load level range settings. Resetting storage:', error);
      try {
        localStorage.removeItem(LEVEL_RANGE_SETTINGS_STORAGE_KEY);
      } catch {
        // ignore
      }
      setShowRebemonOnly(DEFAULT_LEVEL_RANGE_SETTINGS.showRebemonOnly);
      setLevelRangeLowerOffset(DEFAULT_LEVEL_RANGE_SETTINGS.customLowerOffset);
      setLevelRangeUpperOffset(DEFAULT_LEVEL_RANGE_SETTINGS.customUpperOffset);
    } finally {
      didLoadLevelRangeSettingsRef.current = true;
    }
  }, []);

  // 레벨 범위(레범몬 on/off + 커스텀 범위) 저장
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (!didLoadLevelRangeSettingsRef.current) return;

    const next: StoredLevelRangeSettings = {
      showRebemonOnly,
      // 레범몬 모드에서는 범위가 항상 -10/+10이지만,
      // OFF로 돌아왔을 때 복원되도록 커스텀 값은 항상 저장한다.
      customLowerOffset: levelRangeLowerOffset,
      customUpperOffset: levelRangeUpperOffset,
    };

    try {
      localStorage.setItem(LEVEL_RANGE_SETTINGS_STORAGE_KEY, JSON.stringify(next));
    } catch (error) {
      console.warn('Failed to save level range settings:', error);
    }
  }, [showRebemonOnly, levelRangeLowerOffset, levelRangeUpperOffset]);

  // 인기 마스터리북 ID 목록
  const popularMasteryBookIds = useMemo(() => {
    return new Set(
      items
        .filter((item) => item.isPopularMasteryBook === true)
        .map((item) => item.id)
    );
  }, [items]);

  // document.title 업데이트
  useEffect(() => {
    if (level !== '') {
      document.title = showRebemonOnly
        ? `레벨 ${level} 레범몬 - 메이플랜드 레범몬`
        : `레벨 ${level} 몬스터 - 메이플랜드 레범몬`;
    } else {
      document.title = '메이플랜드 레범몬';
    }
  }, [level, showRebemonOnly]);

  // 최근 확인한 몬스터 목록 로드 (컴포넌트 마운트 시)
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    try {
      const stored = localStorage.getItem('recentMonsters');
      if (stored) {
        const data = JSON.parse(stored);
        const now = Date.now();
        const sevenDaysInMs = 7 * 24 * 60 * 60 * 1000;
        
        // 7일 이내의 항목만 필터링하고 최신순으로 정렬
        const sortedData = data
          .filter((item: { monsterId: string; timestamp: number }) => 
            now - item.timestamp < sevenDaysInMs
          )
          .sort((a: { timestamp: number }, b: { timestamp: number }) => b.timestamp - a.timestamp);
        
        const sortedMonsters = sortedData
          .map((item: { monsterId: string }) => 
            monsters.find(m => m.id === item.monsterId)
          )
          .filter((m): m is Monster => m !== undefined);
        
        setRecentMonsters(sortedMonsters);
        
        // 만료된 항목 제거
        if (data.length !== sortedData.length) {
          localStorage.setItem('recentMonsters', JSON.stringify(sortedData));
        }
      }
    } catch (error) {
      console.error('Failed to load recent monsters:', error);
    }
  }, [monsters]);

  // 모달이 열릴 때 최근 확인한 몬스터 목록에 추가
  useEffect(() => {
    if (!selectedMonster) return;
    
    try {
      const stored = localStorage.getItem('recentMonsters');
      const data = stored ? JSON.parse(stored) : [];
      const now = Date.now();
      
      // 이미 존재하는 경우 제거 (중복 방지)
      const filtered = data.filter((item: { monsterId: string }) => 
        item.monsterId !== selectedMonster.id
      );
      
      // 최신 항목을 맨 앞에 추가
      filtered.unshift({
        monsterId: selectedMonster.id,
        timestamp: now
      });
      
      // 최대 20개까지만 저장
      const limited = filtered.slice(0, 20);
      
      localStorage.setItem('recentMonsters', JSON.stringify(limited));
      
      // 상태 업데이트
      const sortedMonsters = limited
        .map((item: { monsterId: string }) => 
          monsters.find(m => m.id === item.monsterId)
        )
        .filter((m): m is Monster => m !== undefined);
      
      setRecentMonsters(sortedMonsters);
    } catch (error) {
      console.error('Failed to save recent monster:', error);
    }
  }, [selectedMonster, monsters]);

  // 레벨 범위로 필터링된 기본 몬스터 목록 (필터 적용 전)
  const baseFilteredMonsters = useMemo(() => {
    // 먼저 출시된 몬스터만 필터링
    // TODO: 개발 완료 후 주석을 해제하세요
    const releasedMonsters = monsters.filter((monster) => monster.isReleased);
    // const releasedMonsters = monsters; // 임시: 모든 몬스터 표시 (테스트용)

    if (level === '' || level === null) {
      return [];
    }

    const levelNum = Number(level);
    if (isNaN(levelNum) || levelNum < 0) {
      return [];
    }

    let filtered: Monster[];

    const lowerOffset = showRebemonOnly ? 10 : levelRangeLowerOffset;
    const upperOffset = showRebemonOnly ? 10 : levelRangeUpperOffset;
    const minBase = levelNum - lowerOffset;
    const maxBase = levelNum + upperOffset;

    if (showRebemonOnly) {
      // 레범몬 모드: 범위는 항상 -10/+10 고정 (레벨 80 이상이면 70 이상의 몬스터도 포함)
      filtered = releasedMonsters.filter((monster) => {
        if (levelNum >= 80) {
          // 레벨 80 이상: ±10 범위 또는 70 이상의 몬스터
          return (
            (monster.level >= minBase && monster.level <= maxBase) ||
            monster.level >= 70
          );
        } else {
          // 레벨 80 미만: 범위만
          return monster.level >= minBase && monster.level <= maxBase;
        }
      });
    } else {
      // 일반 모드: 유저가 지정한 범위를 사용
      filtered = releasedMonsters.filter((monster) => {
        return monster.level >= minBase && monster.level <= maxBase;
      });
    }

    // 중복 ID 제거 (첫 번째 항목만 유지)
    const seenIds = new Set<string | number>();
    const uniqueFiltered = filtered.filter((monster) => {
      if (seenIds.has(monster.id)) {
        return false;
      }
      seenIds.add(monster.id);
      return true;
    });

    // 레벨 1업 시 레범몬이 아니게 되는지 판단 (레범몬 모드일 때만)
    return uniqueFiltered.map((monster): MonsterWithExpiring => {
      if (!showRebemonOnly) {
        return {
          ...monster,
          isExpiringSoon: false,
        };
      }

      const levelNum = Number(level);
      return {
        ...monster,
        isExpiringSoon: (() => {
          if (levelNum >= 80) {
            // 레벨 80 이상: 레벨+1일 때 범위를 벗어나는지 확인
            const nextLevel = levelNum + 1;
            const willBeOutOfRange =
              !(monster.level >= nextLevel - 10 && monster.level <= nextLevel + 10) &&
              !(monster.level >= 70);
            return willBeOutOfRange;
          } else {
            // 레벨 80 미만: 레벨+1일 때 ±10 범위를 벗어나는지 확인
            const nextLevel = levelNum + 1;
            return !(monster.level >= nextLevel - 10 && monster.level <= nextLevel + 10);
          }
        })(),
      };
    });
  }, [level, monsters, showRebemonOnly, levelRangeLowerOffset, levelRangeUpperOffset]) as MonsterWithExpiring[];

  // 검색 결과에 존재하는 지역 ID 추출
  const availableRegionIds = useMemo(() => {
    const regionIdSet = new Set<string>();
    baseFilteredMonsters.forEach((monster) => {
      if (monster.regionIds && monster.regionIds.length > 0) {
        monster.regionIds.forEach((id) => regionIdSet.add(id));
      }
    });
    return Array.from(regionIdSet);
  }, [baseFilteredMonsters]);

  // 지역 필터가 1줄을 넘어가는지 확인
  useEffect(() => {
    if (!regionFilterContainerRef.current) {
      setShouldShowRegionExpandButton(false);
      return;
    }

    const checkOverflow = () => {
      const container = regionFilterContainerRef.current;
      if (!container) return;

      const children = Array.from(container.children) as HTMLElement[];
      if (children.length === 0) {
        setShouldShowRegionExpandButton(false);
        return;
      }

      // 첫 번째 줄의 높이 계산
      const firstRowHeight = children[0]?.offsetTop + children[0]?.offsetHeight || 0;
      
      // 두 번째 줄이 있는지 확인
      const hasSecondRow = children.some((child) => child.offsetTop >= firstRowHeight);
      
      setShouldShowRegionExpandButton(hasSecondRow);
    };

    // 초기 확인 (약간의 지연을 두어 렌더링 완료 후 확인)
    const timeoutId = setTimeout(checkOverflow, 100);
    
    // 리사이즈 이벤트 리스너 추가
    window.addEventListener('resize', checkOverflow);
    
    return () => {
      clearTimeout(timeoutId);
      window.removeEventListener('resize', checkOverflow);
    };
  }, [level, baseFilteredMonsters, availableRegionIds, isRegionFilterExpanded]);

  // 인기 몬스터 여부 판단 함수
  const isRecommendedMonster = useMemo(() => {
    const recommendedSet = new Set<string>();
    // 레벨 30 미만에서 주요 드랍 없이도 인기가 될 수 있는 예외 몬스터들
    const EXCEPTION_MONSTER_IDS = new Set(['9400400', '2110200']); // 하급닌자, 뿔버섯
    // 지형/드랍 등의 이유로 무조건 인기인 몬스터들
    const ALWAYS_POPULAR_MONSTER_IDS = new Set(['8140001', '8140002']); // 하프, 블러드 하프
    // 특별 아이템 ID
    const ILBI_ID = '2070001'; // 일비 표창
    const HWABI_ID = '2070000'; // 뇌전 수리검

    baseFilteredMonsters.forEach((monster) => {
      // 무조건 인기인 예외 몬스터
      if (ALWAYS_POPULAR_MONSTER_IDS.has(monster.id)) {
        recommendedSet.add(monster.id);
        return;
      }

      // 인기 마스터리북을 드랍하는 몬스터는 무조건 인기
      const hasPopularMasteryBook = monster.featuredDropItemIds?.some(
        (itemId) => popularMasteryBookIds.has(itemId)
      );
      if (hasPopularMasteryBook) {
        recommendedSet.add(monster.id);
        return;
      }

      // 일비 표창을 드랍하는 몬스터는 무조건 인기
      const hasIlbi = monster.featuredDropItemIds?.includes(ILBI_ID) ||
        monster.dropItemIds?.includes(ILBI_ID);
      if (hasIlbi) {
        recommendedSet.add(monster.id);
        return;
      }

      // 인기 조건: 레벨 20 이상
      if (monster.level < 20) return;

      // 체경비 계산
      const hpPerExp = monster.exp === 0 ? Infinity : monster.hp / monster.exp;
      const featuredDropCount = monster.featuredDropItemIds?.length || 0;

      // 뇌전 수리검을 드랍하는 몬스터는 체경비 기준 완화 (체경비 < 35)
      const hasHwabi = monster.featuredDropItemIds?.includes(HWABI_ID) ||
        monster.dropItemIds?.includes(HWABI_ID);
      if (hasHwabi && hpPerExp < 35) {
        recommendedSet.add(monster.id);
        return;
      }

      // 레벨 30 미만: 주요 드랍이 필수 (예외 몬스터 제외)
      if (monster.level < 30) {
        // 예외 몬스터: 체경비 < 10이면 인기
        if (EXCEPTION_MONSTER_IDS.has(monster.id) && hpPerExp < 10) {
          recommendedSet.add(monster.id);
          return;
        }

        // 그 외 레벨 30 미만 몬스터는 주요 드랍이 있어야 함
        if (featuredDropCount === 0) return;

        // 주요 드랍이 있는 경우에만 체경비 조건 확인
        // 조건 1: 체경비 < 10
        if (hpPerExp < 10) {
          recommendedSet.add(monster.id);
          return;
        }

        // 조건 2: 체경비 < 15 AND 주요 드랍 >= 1개
        if (hpPerExp < 15 && featuredDropCount >= 1) {
          recommendedSet.add(monster.id);
          return;
        }

        // 조건 3: 체경비 20 안팎 (18~22) AND 주요 드랍 >= 2개
        if (hpPerExp >= 18 && hpPerExp <= 22 && featuredDropCount >= 2) {
          recommendedSet.add(monster.id);
          return;
        }
        return;
      }

      // 레벨 30 이상: 기존 조건 유지
      // 조건 1: 체경비 < 10
      if (hpPerExp < 10) {
        recommendedSet.add(monster.id);
        return;
      }

      // 조건 2: 체경비 < 15 AND 주요 드랍 >= 1개
      if (hpPerExp < 15 && featuredDropCount >= 1) {
        recommendedSet.add(monster.id);
        return;
      }

      // 조건 3: 체경비 20 안팎 (18~22) AND 주요 드랍 >= 2개
      if (hpPerExp >= 18 && hpPerExp <= 22 && featuredDropCount >= 2) {
        recommendedSet.add(monster.id);
        return;
      }
    });
    return recommendedSet;
  }, [baseFilteredMonsters, popularMasteryBookIds]);

  // 출시된 몬스터만 필터링하고, 레벨 범위로 필터링
  const filteredMonsters = useMemo(() => {
    if (baseFilteredMonsters.length === 0) {
      return [];
    }

    let monstersWithExpiring = [...baseFilteredMonsters];

    // 추가 필터 적용
    if (searchName) {
      monstersWithExpiring = monstersWithExpiring.filter((monster) =>
        monster.name.includes(searchName)
      );
    }

    if (minLevel !== '') {
      const min = Number(minLevel);
      if (!isNaN(min)) {
        monstersWithExpiring = monstersWithExpiring.filter((monster) => monster.level >= min);
      }
    }

    if (maxLevel !== '') {
      const max = Number(maxLevel);
      if (!isNaN(max)) {
        monstersWithExpiring = monstersWithExpiring.filter((monster) => monster.level <= max);
      }
    }

    if (minHp !== '') {
      const min = Number(minHp);
      if (!isNaN(min)) {
        monstersWithExpiring = monstersWithExpiring.filter((monster) => monster.hp >= min);
      }
    }

    if (maxHp !== '') {
      const max = Number(maxHp);
      if (!isNaN(max)) {
        monstersWithExpiring = monstersWithExpiring.filter((monster) => monster.hp <= max);
      }
    }

    if (minExp !== '') {
      const min = Number(minExp);
      if (!isNaN(min)) {
        monstersWithExpiring = monstersWithExpiring.filter((monster) => monster.exp >= min);
      }
    }

    if (maxExp !== '') {
      const max = Number(maxExp);
      if (!isNaN(max)) {
        monstersWithExpiring = monstersWithExpiring.filter((monster) => monster.exp <= max);
      }
    }

    if (showExpiringOnly) {
      monstersWithExpiring = monstersWithExpiring.filter((monster) => monster.isExpiringSoon);
    }

    // 인기 몬스터 필터
    if (showRecommendedOnly) {
      // 레벨 30 미만에서 주요 드랍 없이도 인기가 될 수 있는 예외 몬스터들
      const EXCEPTION_MONSTER_IDS = new Set(['9400400', '2110200']); // 하급닌자, 뿔버섯
      // 지형/드랍 등의 이유로 무조건 인기인 몬스터들
      const ALWAYS_POPULAR_MONSTER_IDS = new Set(['8140001', '8140002']); // 하프, 블러드 하프
      // 특별 아이템 ID
      const ILBI_ID = '2070001'; // 일비 표창
      const HWABI_ID = '2070000'; // 뇌전 수리검

      monstersWithExpiring = monstersWithExpiring.filter((monster) => {
        // 무조건 인기인 예외 몬스터
        if (ALWAYS_POPULAR_MONSTER_IDS.has(monster.id)) return true;

        // 인기 마스터리북을 드랍하는 몬스터는 무조건 인기
        const hasPopularMasteryBook = monster.featuredDropItemIds?.some(
          (itemId) => popularMasteryBookIds.has(itemId)
        );
        if (hasPopularMasteryBook) return true;

        // 일비 표창을 드랍하는 몬스터는 무조건 인기
        const hasIlbi = monster.featuredDropItemIds?.includes(ILBI_ID) ||
          monster.dropItemIds?.includes(ILBI_ID);
        if (hasIlbi) return true;

        // 인기 조건: 레벨 20 이상
        if (monster.level < 20) return false;

        // 체경비 계산
        const hpPerExp = monster.exp === 0 ? Infinity : monster.hp / monster.exp;
        const featuredDropCount = monster.featuredDropItemIds?.length || 0;

        // 뇌전 수리검을 드랍하는 몬스터는 체경비 기준 완화 (체경비 < 35)
        const hasHwabi = monster.featuredDropItemIds?.includes(HWABI_ID) ||
          monster.dropItemIds?.includes(HWABI_ID);
        if (hasHwabi && hpPerExp < 35) return true;

        // 레벨 30 미만: 주요 드랍이 필수 (예외 몬스터 제외)
        if (monster.level < 30) {
          // 예외 몬스터: 체경비 < 10이면 인기
          if (EXCEPTION_MONSTER_IDS.has(monster.id) && hpPerExp < 10) {
            return true;
          }

          // 그 외 레벨 30 미만 몬스터는 주요 드랍이 있어야 함
          if (featuredDropCount === 0) return false;

          // 주요 드랍이 있는 경우에만 체경비 조건 확인
          // 조건 1: 체경비 < 10
          if (hpPerExp < 10) return true;

          // 조건 2: 체경비 < 15 AND 주요 드랍 >= 1개
          if (hpPerExp < 15 && featuredDropCount >= 1) return true;

          // 조건 3: 체경비 20 안팎 (18~22) AND 주요 드랍 >= 2개
          if (hpPerExp >= 18 && hpPerExp <= 22 && featuredDropCount >= 2) return true;

          return false;
        }

        // 레벨 30 이상: 기존 조건 유지
        // 조건 1: 체경비 < 10
        if (hpPerExp < 10) return true;

        // 조건 2: 체경비 < 15 AND 주요 드랍 >= 1개
        if (hpPerExp < 15 && featuredDropCount >= 1) return true;

        // 조건 3: 체경비 20 안팎 (18~22) AND 주요 드랍 >= 2개
        if (hpPerExp >= 18 && hpPerExp <= 22 && featuredDropCount >= 2) return true;

        return false;
      });
    }

    if (selectedRegions.length > 0) {
      monstersWithExpiring = monstersWithExpiring.filter((monster) => {
        if (!monster.regionIds || monster.regionIds.length === 0) return false;
        return monster.regionIds.some((regionId) => selectedRegions.includes(regionId));
      });
    }

    // 정렬 적용
    const sorted = [...monstersWithExpiring].sort((a, b) => {
      switch (sortBy) {
        case 'level-asc':
          return a.level - b.level;
        case 'level-desc':
          return b.level - a.level;
        case 'exp-asc':
          return a.exp - b.exp;
        case 'exp-desc':
          return b.exp - a.exp;
        case 'hp-per-exp-asc': {
          // 체경비 낮은 순 (체력 / 경험치) - 효율 좋은 순
          const aHpPerExp = a.exp === 0 ? Infinity : a.hp / a.exp;
          const bHpPerExp = b.exp === 0 ? Infinity : b.hp / b.exp;
          return aHpPerExp - bHpPerExp;
        }
        case 'hp-per-exp-desc': {
          // 체경비 높은 순 (체력 / 경험치) - 효율 나쁜 순
          const aHpPerExp = a.exp === 0 ? Infinity : a.hp / a.exp;
          const bHpPerExp = b.exp === 0 ? Infinity : b.hp / b.exp;
          return bHpPerExp - aHpPerExp;
        }
        case 'region-asc': {
          // 지역 가나다순 (첫 번째 지역 기준)
          const aRegionName = a.regionIds && a.regionIds.length > 0
            ? regions.find(r => r.id === a.regionIds?.[0])?.name || ''
            : '';
          const bRegionName = b.regionIds && b.regionIds.length > 0
            ? regions.find(r => r.id === b.regionIds?.[0])?.name || ''
            : '';
          return aRegionName.localeCompare(bRegionName, 'ko');
        }
        case 'name-asc':
          return a.name.localeCompare(b.name, 'ko');
        case 'name-desc':
          return b.name.localeCompare(a.name, 'ko');
        default:
          return a.level - b.level;
      }
    });

    // 중복 ID 제거 (첫 번째 항목만 유지)
    const seenIds = new Set<string | number>();
    const uniqueSorted = sorted.filter((monster) => {
      if (seenIds.has(monster.id)) {
        return false;
      }
      seenIds.add(monster.id);
      return true;
    });

    return uniqueSorted;
  }, [baseFilteredMonsters, searchName, minLevel, maxLevel, minHp, maxHp, minExp, maxExp, showExpiringOnly, showRecommendedOnly, selectedRegions, sortBy, popularMasteryBookIds, regions]) as MonsterWithExpiring[];

  return (
    <div className="flex min-h-screen flex-col bg-gray-900">
      <div className="container mx-auto flex-1 px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8 text-center">
          <h1 className="mb-4 text-3xl font-bold text-gray-100 sm:text-4xl md:text-5xl">
            메이플랜드 레범몬
          </h1>
          <p className="text-base text-gray-400 sm:text-lg">
            레벨을 입력하면 기본 -10/+10 범위의 몬스터를 확인할 수 있으며, 범위 설정에서 커스텀할 수 있습니다
          </p>
        </div>

        <div className="mb-8 flex justify-center">
          <div className="w-full max-w-xl">
            <div className="mb-2 flex items-center justify-between">
              <label
                htmlFor="level-input"
                className="block text-sm font-medium text-gray-400"
              >
                레벨 입력
              </label>
            </div>
            <div className="relative flex gap-2">
              <LevelRangeSettingsButton
                showRebemonOnly={showRebemonOnly}
                onChangeShowRebemonOnly={setShowRebemonOnly}
                lowerOffset={levelRangeLowerOffset}
                upperOffset={levelRangeUpperOffset}
                onChangeLowerOffset={setLevelRangeLowerOffset}
                onChangeUpperOffset={setLevelRangeUpperOffset}
              />
              <input
                id="level-input"
                type="number"
                min="1"
                value={level}
                onChange={(e) => {
                  const value = e.target.value;
                  setLevel(value === '' ? '' : Number(value));
                }}
                placeholder={showRebemonOnly ? "자신의 레벨을 입력(예: 50)" : "기준 레벨 입력(예: 50)"}
                className="latin-font numeric h-10 min-w-0 flex-1 rounded-lg border border-gray-600 bg-gray-800 px-3 sm:px-4 text-base text-gray-100 shadow-sm placeholder:text-gray-500 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
              <div className="relative" ref={quickSelectRef}>
                <button
                  onClick={() => setIsQuickSelectOpen(!isQuickSelectOpen)}
                  aria-haspopup="dialog"
                  aria-expanded={isQuickSelectOpen}
                  className={`h-10 flex items-center gap-2 whitespace-nowrap rounded-lg border-2 px-3 sm:px-4 font-semibold text-xs sm:text-sm transition-all ${isQuickSelectOpen
                      ? 'border-blue-500 bg-blue-500/20 text-blue-400'
                      : 'border-blue-500 bg-blue-500 text-white hover:bg-blue-600 hover:border-blue-600 active:scale-95'
                    }`}
                >
                  <svg
                    className="h-4 w-4 sm:h-5 sm:w-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                  <span className="hidden sm:inline">빠른 선택</span>
                  <span className="sr-only sm:hidden">빠른 선택</span>
                  <svg
                    className={`h-4 w-4 transition-transform ${isQuickSelectOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>

                {/* 빠른 선택 팝업 */}
                {isQuickSelectOpen && (
                  <>
                    {/* 팝업과 버튼을 연결하는 화살표 */}
                    <div className="absolute top-full left-1/2 z-10 -translate-x-1/2 -mt-1">
                      <div className="h-3 w-3 rotate-45 border-l border-t border-gray-700 bg-gray-800"></div>
                    </div>
                    <div className="absolute top-full right-0 sm:left-0 sm:right-auto z-10 mt-2 w-[min(20rem,calc(100vw-2rem))] rounded-lg border border-gray-700 bg-gray-800 p-4 shadow-xl">
                      <div className="mb-3 flex items-center justify-between">
                        <h3 className="text-sm font-semibold text-gray-300">레벨 빠른 선택</h3>
                        <button
                          onClick={() => setIsQuickSelectOpen(false)}
                          className="rounded p-1 text-gray-400 hover:bg-gray-700 hover:text-gray-200 transition-colors"
                          aria-label="닫기"
                        >
                          <svg
                            className="h-4 w-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M6 18L18 6M6 6l12 12"
                            />
                          </svg>
                        </button>
                      </div>
                      <div className="grid grid-cols-4 gap-2">
                        {[10, 20, 30, 40, 50, 60, 70].map((levelOption) => (
                          <button
                            key={levelOption}
                            onClick={() => {
                              setLevel(levelOption);
                              setIsQuickSelectOpen(false);
                            }}
                            className="rounded-lg border-2 border-gray-600 bg-gray-700 px-3 py-2.5 text-base font-semibold text-gray-100 transition-all hover:border-blue-400 hover:bg-blue-500/20 hover:text-blue-400 active:scale-95"
                          >
                            {levelOption}
                          </button>
                        ))}
                        <button
                          onClick={() => {
                            setLevel(80);
                            setIsQuickSelectOpen(false);
                          }}
                          className="rounded-lg border-2 border-gray-600 bg-gray-700 px-3 py-2.5 text-base font-semibold text-gray-100 transition-all hover:border-blue-400 hover:bg-blue-500/20 hover:text-blue-400 active:scale-95"
                        >
                          80+
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* 최근 확인한 몬스터 목록 */}
        {recentMonsters.length > 0 && (
          <div className="mb-6 flex justify-center">
            <div className="w-full max-w-xl">
              <div className="mb-2 text-sm font-medium text-gray-400">최근 확인한 몬스터</div>
              <div className="flex flex-wrap gap-2">
                {recentMonsters.map((monster) => (
                  <button
                    key={monster.id}
                    onClick={() => setSelectedMonster(monster)}
                    className="rounded-full border border-gray-600 bg-gray-800 px-3 py-1.5 text-sm font-medium text-gray-200 transition-colors hover:border-blue-500 hover:bg-gray-700 hover:text-blue-400"
                  >
                    {monster.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 상세 검색 및 필터 UI - 레벨 입력 밑에 항상 표시 */}
        <div className="mb-6 flex justify-center">
          <div className="w-full max-w-xl flex items-start gap-4 flex-wrap">
            <div className="flex-1 min-w-[16rem]">
              <div className="rounded-lg border border-gray-700 bg-gray-800">
                <button
                  onClick={() => setIsFilterOpen(!isFilterOpen)}
                  className="h-10 flex w-full items-center justify-between px-4 text-left text-gray-200 hover:bg-gray-750 transition-colors"
                >
                  <span className="font-medium">상세 검색 및 필터</span>
                  <svg
                    className={`h-5 w-5 transition-transform ${isFilterOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {isFilterOpen && (
                  <div className="border-t border-gray-700 p-4 space-y-4">
                    {/* 이름 검색 */}
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-300">이름 검색</label>
                      <input
                        type="text"
                        value={searchName}
                        onChange={(e) => setSearchName(e.target.value)}
                        placeholder="몬스터 이름 입력"
                        className="w-full rounded-lg border border-gray-600 bg-gray-700 px-3 py-2 text-gray-100 placeholder:text-gray-500 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400"
                      />
                    </div>

                    {/* 레벨 범위 */}
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="mb-1 block text-sm font-medium text-gray-300">최소 레벨</label>
                        <input
                          type="number"
                          value={minLevel}
                          onChange={(e) => setMinLevel(e.target.value === '' ? '' : Number(e.target.value))}
                          placeholder="최소"
                          className="latin-font numeric w-full rounded-lg border border-gray-600 bg-gray-700 px-3 py-2 text-gray-100 placeholder:text-gray-500 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400"
                        />
                      </div>
                      <div>
                        <label className="mb-1 block text-sm font-medium text-gray-300">최대 레벨</label>
                        <input
                          type="number"
                          value={maxLevel}
                          onChange={(e) => setMaxLevel(e.target.value === '' ? '' : Number(e.target.value))}
                          placeholder="최대"
                          className="latin-font numeric w-full rounded-lg border border-gray-600 bg-gray-700 px-3 py-2 text-gray-100 placeholder:text-gray-500 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400"
                        />
                      </div>
                    </div>

                    {/* 정렬 옵션 */}
                    <div>
                      <label className="mb-2 block text-sm font-medium text-gray-300">정렬</label>
                      <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value as SortOption)}
                        className="w-full rounded-lg border border-gray-600 bg-gray-700 px-3 py-2 text-gray-100 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400"
                      >
                        <option value="level-asc">레벨 순 (낮은 순)</option>
                        <option value="level-desc">레벨 순 (높은 순)</option>
                        <option value="exp-asc">EXP 순 (낮은 순)</option>
                        <option value="exp-desc">EXP 순 (높은 순)</option>
                        <option value="hp-per-exp-asc">체경비 순 (낮은 순)</option>
                        <option value="hp-per-exp-desc">체경비 순 (높은 순)</option>
                        <option value="region-asc">지역 순 (가나다)</option>
                        <option value="name-asc">이름 순 (가나다)</option>
                        <option value="name-desc">이름 순 (다나가)</option>
                      </select>
                    </div>

                    {/* 인기 몬스터만 보기 */}
                    {/* <div>
                      <label className="flex items-start gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={showRecommendedOnly}
                          onChange={(e) => setShowRecommendedOnly(e.target.checked)}
                          className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-yellow-500 focus:ring-yellow-500 focus:ring-2"
                        />
                        <span className="text-sm font-medium text-gray-300">인기 몬스터만 보기</span>
                      </label>
                    </div> */}

                    {/* 필터 초기화 버튼 */}
                    <button
                      onClick={() => {
                        setSearchName('');
                        setMinLevel('');
                        setMaxLevel('');
                        setMinHp('');
                        setMaxHp('');
                        setMinExp('');
                        setMaxExp('');
                        setShowExpiringOnly(false);
                        setShowRecommendedOnly(false);
                        setSelectedRegions([]);
                        setSortBy('level-asc');
                      }}
                      className="w-full rounded-lg bg-gray-700 px-4 py-2 text-sm text-gray-300 hover:bg-gray-600 transition-colors"
                    >
                      필터 초기화
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* 인기 몬스터 보기 버튼 */}
            <div className="w-full sm:w-40 flex items-center">
              <button
                onClick={() => setShowRecommendedOnly(!showRecommendedOnly)}
                className={`h-10 w-full rounded-lg border-2 px-4 text-sm font-medium transition-all ${showRecommendedOnly
                    ? 'border-yellow-500 bg-yellow-500/20 text-yellow-400'
                    : 'border-gray-700 bg-gray-800 text-gray-300 hover:border-yellow-500/50 hover:bg-gray-750'
                  }`}
              >
                {showRecommendedOnly ? '인기 몬스터 보기 중' : '인기 몬스터 보기'}
              </button>
            </div>
          </div>
        </div>

        {/* 지역 필터 뱃지 - 검색 결과에 존재하는 지역만 표시 */}
        {level !== '' && baseFilteredMonsters.length > 0 && availableRegionIds.length > 0 && (
          <div className="mb-6 flex justify-center">
            <div className="w-full max-w-4xl">
              <div className="mb-2 text-sm font-medium text-gray-400">지역 필터</div>
              <div className="w-full">
                <div
                  ref={regionFilterContainerRef}
                  className={`flex flex-wrap gap-2 overflow-hidden transition-all ${
                    isRegionFilterExpanded ? '' : 'max-h-[3rem]'
                  }`}
                >
                  {regions
                    .filter((region) => availableRegionIds.includes(region.id))
                    .map((region) => {
                      const isSelected = selectedRegions.includes(region.id);
                      return (
                        <button
                          key={region.id}
                          onClick={() => {
                            if (isSelected) {
                              setSelectedRegions(selectedRegions.filter((id) => id !== region.id));
                            } else {
                              setSelectedRegions([...selectedRegions, region.id]);
                            }
                          }}
                          className={`rounded-full px-4 py-2 text-sm font-medium transition-all ${isSelected
                              ? 'bg-blue-600 text-white shadow-md'
                              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                            }`}
                        >
                          {region.name}
                        </button>
                      );
                    })}
                  {selectedRegions.length > 0 && (
                    <button
                      onClick={() => setSelectedRegions([])}
                      className="rounded-full bg-gray-700 px-4 py-2 text-sm font-medium text-gray-300 hover:bg-gray-600 transition-colors"
                    >
                      전체 해제
                    </button>
                  )}
                </div>
                {shouldShowRegionExpandButton && (
                  <button
                    onClick={() => setIsRegionFilterExpanded(!isRegionFilterExpanded)}
                    className="mt-2 text-sm text-gray-400 hover:text-gray-300 transition-colors"
                  >
                    {isRegionFilterExpanded ? '접기' : '펼쳐보기'}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {level !== '' && filteredMonsters.length > 0 && (
          <div className="mb-4 text-center text-gray-400">
            <p>
              레벨 <span className="latin-font font-medium">{level}</span> 기준 {showRebemonOnly ? '레범몬' : '몬스터'} {filteredMonsters.length}개
              {showRebemonOnly && Number(level) >= 80 && (
                <span className="block text-sm mt-1 text-gray-500">
                  (레벨 80 이상이므로 70 이상 몬스터도 포함됩니다)
                </span>
              )}
            </p>
          </div>
        )}

        {level !== '' && filteredMonsters.length === 0 && (
          <div className="text-center text-gray-500">
            <p>해당 레벨 범위에 몬스터가 없습니다.</p>
          </div>
        )}

        {filteredMonsters.length > 0 && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {filteredMonsters.map((monster) => (
              <MonsterCard
                key={monster.id}
                monster={monster}
                isExpiringSoon={monster.isExpiringSoon}
                userLevel={level !== '' ? Number(level) : undefined}
                isRecommended={isRecommendedMonster.has(monster.id)}
                onClick={() => setSelectedMonster(monster)}
              />
            ))}
          </div>
        )}

        {level === '' && (
          <div className="text-center text-gray-500">
            <p>레벨을 입력하시면 몬스터 목록이 표시됩니다.</p>
          </div>
        )}
      </div>
      <div className="mt-auto">
        <Footer />
      </div>
      
      {/* 상세 몬스터 카드 모달 */}
      <MonsterDetailModal
        monster={selectedMonster}
        onClose={() => setSelectedMonster(null)}
      />
    </div>
  );
}
