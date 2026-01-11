import { Monster } from '@/types/monster';
import { Region } from '@/types/region';
import { Item } from '@/types/item';
import Image from 'next/image';
import { useState, useMemo, useEffect, useRef } from 'react';
import regionData from '@/data/region_data.json';
import itemData from '@/data/item_data.json';

interface MonsterCardProps {
  monster: Monster;
  isExpiringSoon?: boolean;
  userLevel?: number;
  isRecommended?: boolean;
  onClick?: () => void;
}

export default function MonsterCard({ monster, isExpiringSoon, userLevel, isRecommended, onClick }: MonsterCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [isWarningHovered, setIsWarningHovered] = useState(false);
  const [isHpPerExpTooltipHovered, setIsHpPerExpTooltipHovered] = useState(false);
  const [isRegionsExpanded, setIsRegionsExpanded] = useState(false);
  const [shouldShowExpandButton, setShouldShowExpandButton] = useState(false);
  const regionsContainerRef = useRef<HTMLDivElement>(null);
  
  // 파티 경험치 획득 조건: 몬스터 레벨이 사용자 레벨+5를 초과하면 파티 경험치를 획득할 수 없음
  const isOutOfPartyExpRange = userLevel !== undefined && monster.level > userLevel + 5;

  const regions = regionData as Region[];
  const items = itemData as Item[];

  // 지역 정보 가져오기
  const monsterRegions = useMemo(() => {
    if (!monster.regionIds || monster.regionIds.length === 0) return [];
    return regions.filter((region) => monster.regionIds?.includes(region.id));
  }, [monster.regionIds, regions]);

  // 지역 태그가 1줄을 넘어가는지 확인
  useEffect(() => {
    if (!regionsContainerRef.current || monsterRegions.length === 0) {
      setShouldShowExpandButton(false);
      return;
    }

    const checkOverflow = () => {
      const container = regionsContainerRef.current;
      if (!container) return;

      // scrollHeight와 clientHeight를 비교하여 오버플로우 확인
      // scrollHeight가 clientHeight보다 크면 내용이 넘친 것
      const hasOverflow = container.scrollHeight > container.clientHeight;
      
      // 또는 첫 번째 줄의 높이를 기준으로 두 번째 줄이 있는지 확인
      const children = Array.from(container.children) as HTMLElement[];
      if (children.length === 0) {
        setShouldShowExpandButton(false);
        return;
      }

      // 첫 번째 줄의 높이 계산
      const firstRowHeight = children[0]?.offsetTop + children[0]?.offsetHeight || 0;
      
      // 두 번째 줄이 있는지 확인
      const hasSecondRow = children.some((child) => child.offsetTop >= firstRowHeight);
      
      setShouldShowExpandButton(hasOverflow || hasSecondRow);
    };

    // 초기 확인 (약간의 지연을 두어 렌더링 완료 후 확인)
    const timeoutId = setTimeout(checkOverflow, 100);
    
    // 리사이즈 이벤트 리스너 추가
    window.addEventListener('resize', checkOverflow);
    
    return () => {
      clearTimeout(timeoutId);
      window.removeEventListener('resize', checkOverflow);
    };
  }, [monsterRegions, isRegionsExpanded]);

  // 주요 드랍 아이템 정보 가져오기 (중복 이름 제거)
  const featuredDropItems = useMemo(() => {
    if (!monster.featuredDropItemIds || monster.featuredDropItemIds.length === 0) return [];
    const filtered = items.filter((item) => monster.featuredDropItemIds?.includes(item.id));
    
    // 같은 이름의 아이템이 중복 렌더링되지 않도록 중복 제거 (첫 번째 항목만 유지)
    const seenNames = new Set<string>();
    return filtered.filter((item) => {
      if (seenNames.has(item.name)) {
        return false;
      }
      seenNames.add(item.name);
      return true;
    });
  }, [monster.featuredDropItemIds, items]);

  // 체경비 계산 (체력 / 경험치) - useMemo로 최적화
  const hpPerExp = useMemo(() => {
    if (monster.exp === 0) return Infinity;
    return monster.hp / monster.exp;
  }, [monster.hp, monster.exp]);

  // 체경비에 따른 색상 결정
  const getHpPerExpColor = (hpPerExp: number) => {
    if (hpPerExp < 10) {
      return 'text-green-400'; // 너무 좋음
    } else if (hpPerExp < 20) {
      return 'text-yellow-400'; // 적당히 쓸만함
    } else if (hpPerExp < 33) {
      return 'text-gray-400'; // 평범한 수준
    } else {
      return 'text-red-400'; // 너무 구림
    }
  };

  // 속성 색상 및 스타일 매핑 함수
  const getAttributeStyle = (attribute: string) => {
    if (attribute.includes('불속성')) {
      return { color: 'text-red-400', bg: 'bg-red-900/30', border: 'border-red-500/50' };
    } else if (attribute.includes('전기속성')) {
      return { color: 'text-yellow-400', bg: 'bg-yellow-900/30', border: 'border-yellow-500/50' };
    } else if (attribute.includes('독속성')) {
      return { color: 'text-purple-400', bg: 'bg-purple-900/30', border: 'border-purple-500/50' };
    } else if (attribute.includes('얼음속성')) {
      return { color: 'text-sky-400', bg: 'bg-sky-900/30', border: 'border-sky-500/50' };
    } else if (attribute.includes('성속성')) {
      return { color: 'text-yellow-50', bg: 'bg-yellow-900/20', border: 'border-yellow-400/40' };
    }
    return { color: 'text-gray-300', bg: 'bg-gray-700/30', border: 'border-gray-500/50' };
  };

  // 속성 타입 파싱 (약점/반감/무효)
  const parseAttribute = (attribute: string) => {
    if (attribute.includes('약점')) {
      const name = attribute.replace('약점', '').trim();
      return { type: 'weakness', name };
    } else if (attribute.includes('반감')) {
      const name = attribute.replace('반감', '').trim();
      return { type: 'resistance', name };
    } else if (attribute.includes('무효')) {
      const name = attribute.replace('무효', '').trim();
      return { type: 'immune', name };
    }
    return { type: 'unknown', name: attribute };
  };

  return (
    <div
      className={`relative flex flex-col items-center rounded-lg border-2 bg-gray-800 p-4 shadow-sm transition-all hover:shadow-md cursor-pointer ${
        isExpiringSoon
          ? 'border-red-500 hover:border-yellow-500'
          : 'border-gray-700 hover:border-yellow-500'
      }`}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setIsWarningHovered(false);
        setIsHpPerExpTooltipHovered(false);
      }}
    >
      {/* 경고 아이콘 (레벨 차이 5 초과) */}
      {isOutOfPartyExpRange && (
        <div className="absolute left-2 top-2 z-10">
          <div 
            className="relative"
            onMouseEnter={(e) => {
              e.stopPropagation();
              setIsWarningHovered(true);
            }}
            onMouseLeave={() => setIsWarningHovered(false)}
          >
            <svg
              className="h-5 w-5 cursor-help text-yellow-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 8v4m0 4h.01"
              />
            </svg>
            {isWarningHovered && (
              <div className="absolute left-0 top-6 z-20 w-48 rounded-md bg-yellow-600 px-3 py-1.5 text-xs text-white shadow-lg">
                레벨 범위가 5 이내가 아니어서 파티 경험치를 획득할 수 없습니다
                <div className="absolute -top-1 left-2 h-2 w-2 rotate-45 bg-yellow-600"></div>
              </div>
            )}
          </div>
        </div>
      )}
      
      {isExpiringSoon && isHovered && !isWarningHovered && (
        <div className="absolute -top-10 left-1/2 z-10 -translate-x-1/2 rounded-md bg-red-600 px-3 py-1.5 text-sm text-white shadow-lg">
          곧 레범몬이 아니게 됩니다
          <div className="absolute bottom-0 left-1/2 -mb-1 h-2 w-2 -translate-x-1/2 rotate-45 bg-red-600"></div>
        </div>
      )}
      <div className="mb-3 flex h-[100px] w-[100px] items-center justify-center overflow-hidden">
        <Image
          src={monster.imageUrl}
          alt={monster.name}
          width={100}
          height={100}
          className="h-full w-full object-contain"
          unoptimized
        />
      </div>
      <div className="mb-2 flex items-center justify-center gap-2 flex-wrap">
        <h3 className="text-base font-semibold text-gray-100 sm:text-lg">
          {monster.name}
        </h3>
        {isRecommended && (
          <span className="rounded-full bg-yellow-500/20 px-2 py-0.5 text-xs font-semibold text-yellow-400 border border-yellow-500/50">
            인기
          </span>
        )}
      </div>

      {/* 지역 뱃지 */}
      {monsterRegions.length > 0 && (
        <div className="mb-2 w-full">
          <div
            ref={regionsContainerRef}
            className={`flex w-full flex-wrap gap-1.5 justify-center overflow-hidden transition-all ${
              isRegionsExpanded ? '' : 'max-h-[2.5rem]'
            }`}
          >
            {monsterRegions.map((region) => (
              <span
                key={region.id}
                className="rounded-full bg-gray-700 px-3 py-1 text-xs font-medium text-gray-300"
              >
                {region.name}
              </span>
            ))}
          </div>
          {shouldShowExpandButton && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsRegionsExpanded(!isRegionsExpanded);
              }}
              className="mt-1 w-full text-xs text-gray-400 hover:text-gray-300 transition-colors"
            >
              {isRegionsExpanded ? '접기' : '펼쳐보기'}
            </button>
          )}
        </div>
      )}


      <div className="flex w-full flex-col gap-1 text-xs text-gray-400 sm:text-sm">
        <div className="flex justify-between">
          <span className="font-medium">레벨:</span>
          <span className="latin-font numeric">{monster.level}</span>
        </div>
        <div className="flex justify-between">
          <span className="font-medium">HP:</span>
          <span className="latin-font numeric">{monster.hp.toLocaleString()}</span>
        </div>
        <div className="flex justify-between">
          <span className="font-medium">EXP:</span>
          <span className="latin-font numeric text-blue-400">
            {monster.exp.toLocaleString()}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="font-medium">체경비:</span>
          <div className="flex items-center gap-1">
            <span className={`latin-font numeric ${getHpPerExpColor(hpPerExp)}`}>
              {hpPerExp === Infinity ? '∞' : hpPerExp.toFixed(2)}
            </span>
            <div 
              className="relative"
              onMouseEnter={(e) => {
                e.stopPropagation();
                setIsHpPerExpTooltipHovered(true);
              }}
              onMouseLeave={() => setIsHpPerExpTooltipHovered(false)}
              onTouchStart={(e) => {
                e.stopPropagation();
                setIsHpPerExpTooltipHovered(!isHpPerExpTooltipHovered);
              }}
            >
              <svg
                className="h-4 w-4 cursor-help text-gray-500 hover:text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              {isHpPerExpTooltipHovered && (
                <div className="absolute right-0 top-6 z-20 w-64 rounded-md bg-gray-700 px-3 py-2 text-xs text-gray-100 shadow-lg">
                  <div className="font-semibold mb-1">체경비 (체력 대비 경험치)</div>
                  <div className="text-gray-300">
                    체력 ÷ 경험치로 계산됩니다.
                    <br />
                    체경비가 낮을수록 경험치 효율이 좋습니다.
                  </div>
                  <div className="absolute -top-1 right-4 h-2 w-2 rotate-45 bg-gray-700"></div>
                </div>
              )}
            </div>
          </div>
        </div>
        {/* 주요 드랍 */}
        {featuredDropItems.length > 0 && (
          <div className="mt-1 flex flex-col gap-1">
            <span className="font-medium text-gray-400">주요 드랍:</span>
            <div className="flex flex-wrap gap-1">
              {featuredDropItems.slice(0, 3).map((item) => (
                <span
                  key={item.id}
                  className="rounded-md bg-blue-900/40 px-2 py-0.5 text-xs font-medium text-blue-300"
                >
                  {item.name}
                </span>
              ))}
              {featuredDropItems.length > 3 && (
                <span className="rounded-md bg-blue-900/40 px-2 py-0.5 text-xs font-medium text-blue-300">
                  외 {featuredDropItems.length - 3}건
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* 속성 약점/반감 표시 */}
      {monster.attributes && monster.attributes.length > 0 && (
        <div className="mt-2 flex w-full flex-wrap gap-1.5 justify-center">
          {monster.attributes.map((attribute, index) => {
            const style = getAttributeStyle(attribute);
            const parsed = parseAttribute(attribute);
            const isWeakness = parsed.type === 'weakness';
            
            return (
              <span
                key={index}
                className={`rounded-md border px-2 py-1 text-xs ${
                  style.color
                } ${style.bg} ${style.border} ${isWeakness ? 'font-bold' : 'font-normal'}`}
              >
                {parsed.name}
                {isWeakness ? ' 약점' : parsed.type === 'resistance' ? ' 반감' : parsed.type === 'immune' ? ' 무효' : ''}
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}