'use client';

import { Monster } from '@/types/monster';
import { Item } from '@/types/item';
import { Region } from '@/types/region';
import { GameMap } from '@/types/map';
import Image from 'next/image';
import { useMemo, useState } from 'react';
import itemData from '@/data/item_data.json';
import regionData from '@/data/region_data.json';
import mapData from '@/data/map_data.json';
import monsterItemRelations from '@/data/monster_item_relations.json';
import monsterData from '@/data/monster_data.json';

interface MonsterItemRelation {
  monsterId: string;
  itemId: string;
}

interface MonsterDetailModalProps {
  monster: Monster | null;
  onClose: () => void;
  onMonsterClick?: (monster: Monster) => void;
}

export default function MonsterDetailModal({ monster, onClose, onMonsterClick }: MonsterDetailModalProps) {
  const [showStats, setShowStats] = useState(false);
  const items = itemData as Item[];
  const regions = regionData as Region[];
  const maps = mapData as GameMap[];
  const relations = monsterItemRelations as MonsterItemRelation[];
  const allMonsters = monsterData as Monster[];

  // 드롭 아이템 목록
  const dropItems = useMemo(() => {
    if (!monster) return [];
    
    // 1. monster_item_relations에서 아이템 ID 수집
    const itemIdsFromRelations = relations
      .filter((rel) => rel.monsterId === monster.id)
      .map((rel) => rel.itemId);
    
    // 2. monster.dropItemIds에서 아이템 ID 수집
    const itemIdsFromDropItems = monster.dropItemIds || [];
    
    // 3. monster.featuredDropItemIds에서 아이템 ID 수집
    const itemIdsFromFeatured = monster.featuredDropItemIds || [];
    
    // 4. 모든 아이템 ID 통합 (중복 제거)
    const allItemIds = new Set([
      ...itemIdsFromRelations,
      ...itemIdsFromDropItems,
      ...itemIdsFromFeatured,
    ]);
    
    // 5. 아이템 필터링
    const filtered = items
      .filter((item) => allItemIds.has(item.id))
      .filter((item) => {
        // "클래식메이플 드랍테이블 검색 &amp; 데이터베이스" 제외
        if (item.name.includes('클래식메이플 드랍테이블 검색')) {
          return false;
        }
        
        // 주문서인 경우 10%, 60%, 100%만 표시
        if (item.name.includes('주문서')) {
          const percentMatch = item.name.match(/(\d+)%/);
          if (percentMatch) {
            const percent = parseInt(percentMatch[1], 10);
            return percent === 10 || percent === 60 || percent === 100;
          }
        }
        
        // "[마스터리북]" 태그를 가진 아이템은 항상 포함
        if (item.name.includes('[마스터리북]')) {
          return true;
        }
        
        return true;
      });
    
    // 같은 이름의 아이템이 중복 렌더링되지 않도록 중복 제거 (첫 번째 항목만 유지)
    const seenNames = new Set<string>();
    return filtered.filter((item) => {
      if (seenNames.has(item.name)) {
        return false;
      }
      seenNames.add(item.name);
      return true;
    });
  }, [monster, relations, items]);

  // 지역 정보
  const monsterRegions = useMemo(() => {
    if (!monster || !monster.regionIds || monster.regionIds.length === 0) return [];
    return regions.filter((region) => monster.regionIds?.includes(region.id));
  }, [monster, regions]);

  const regionNameById = useMemo(() => {
    return new Map(regions.map((r) => [r.id, r.name]));
  }, [regions]);

  // 변신 전 몬스터 정보
  const transformsFromMonster = useMemo(() => {
    if (!monster || !monster.transformsFromMonsterId) return null;
    return allMonsters.find((m) => m.id === monster.transformsFromMonsterId) || null;
  }, [monster, allMonsters]);

  // 출현 사냥터(맵) 정보: map_data.json에서 역으로 산출
  const huntingMaps = useMemo(() => {
    if (!monster) return [];
    return maps
      .filter((m) => m.isReleased)
      .filter((m) => m.mapType !== 'town') // 사냥터 성격만 우선 노출
      .filter((m) => m.monsterIds?.includes(monster.id))
      .sort((a, b) => {
        const ar = regionNameById.get(a.regionId) ?? a.regionId;
        const br = regionNameById.get(b.regionId) ?? b.regionId;
        if (ar !== br) return ar.localeCompare(br, 'ko');
        if (a.mapType !== b.mapType) return a.mapType.localeCompare(b.mapType);
        return a.name.localeCompare(b.name, 'ko');
      });
  }, [monster, maps, regionNameById]);

  // 변신 전 몬스터의 출현 사냥터 정보
  const transformsFromHuntingMaps = useMemo(() => {
    if (!transformsFromMonster) return [];
    return maps
      .filter((m) => m.isReleased)
      .filter((m) => m.mapType !== 'town')
      .filter((m) => m.monsterIds?.includes(transformsFromMonster.id))
      .sort((a, b) => {
        const ar = regionNameById.get(a.regionId) ?? a.regionId;
        const br = regionNameById.get(b.regionId) ?? b.regionId;
        if (ar !== br) return ar.localeCompare(br, 'ko');
        if (a.mapType !== b.mapType) return a.mapType.localeCompare(b.mapType);
        return a.name.localeCompare(b.name, 'ko');
      });
  }, [transformsFromMonster, maps, regionNameById]);


  // 체경비 계산
  const hpPerExp = useMemo(() => {
    if (!monster || monster.exp === 0) return Infinity;
    return monster.hp / monster.exp;
  }, [monster]);

  // 체경비에 따른 색상 결정
  const getHpPerExpColor = (hpPerExp: number) => {
    if (hpPerExp < 10) {
      return 'text-green-400';
    } else if (hpPerExp < 20) {
      return 'text-yellow-400';
    } else if (hpPerExp < 33) {
      return 'text-gray-400';
    } else {
      return 'text-red-400';
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

  // 속성 타입 파싱
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

  if (!monster) return null;

  return (
    <>
      {/* 배경 오버레이 */}
      <div
        className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* 모달 */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className="relative w-full max-w-5xl max-h-[90vh] overflow-y-auto rounded-2xl border border-gray-700/80 bg-gradient-to-b from-gray-900 to-gray-950 shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* 상단 바 (시선 고정 + 닫기) */}
          <div className="sticky top-0 z-10 border-b border-gray-800 bg-gray-900/70 backdrop-blur">
            <div className="flex items-center gap-3 px-4 py-3 sm:px-6">
              <div className="relative h-10 w-10 overflow-hidden rounded-lg border border-gray-800 bg-gray-950">
                <Image
                  src={monster.imageUrl}
                  alt={monster.name}
                  fill
                  className="object-contain"
                  unoptimized
                />
              </div>

              <div className="min-w-0 flex-1">
                <div className="truncate text-base font-semibold text-gray-100 sm:text-lg">
                  {monster.name}
                </div>
                <div className="flex flex-nowrap items-center gap-x-2 gap-y-1 text-xs text-gray-400">
                  <span className="latin-font numeric">Lv {monster.level}</span>
                  {monster.attributes && monster.attributes.length > 0 && (
                    <>
                      <span className="text-gray-600">·</span>
                      <div className="flex flex-nowrap items-center gap-1.5">
                        {monster.attributes.map((attribute, index) => {
                          const style = getAttributeStyle(attribute);
                          const parsed = parseAttribute(attribute);
                          const isWeakness = parsed.type === 'weakness';

                          return (
                            <span
                              key={index}
                              className={`rounded border px-2 py-0.5 text-xs ${
                                style.color
                              } ${style.bg} ${style.border} ${isWeakness ? 'font-bold' : 'font-normal'}`}
                            >
                              {parsed.name}
                              {isWeakness
                                ? ' 약점'
                                : parsed.type === 'resistance'
                                ? ' 반감'
                                : parsed.type === 'immune'
                                ? ' 무효'
                                : ''}
                            </span>
                          );
                        })}
                      </div>
                    </>
                  )}
                </div>
              </div>

              <button
                onClick={onClose}
                className="bg-gray-900 p-2 text-gray-300 transition-colors hover:text-white"
                aria-label="닫기"
              >
                <svg
                  className="h-5 w-5"
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
          </div>

          {/* 모달 내용 */}
          <div className="px-4 py-5 sm:px-6 sm:py-6">
            {/* 핵심 스탯 (최상단: 스캔 우선) */}
            <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div className="rounded-xl border border-gray-800 bg-gray-900/40 p-4">
                <div className="text-xs text-gray-400">HP</div>
                <div className="mt-1 text-lg font-semibold text-gray-100 latin-font numeric">
                  {monster.hp.toLocaleString()}
                </div>
              </div>
              <div className="rounded-xl border border-gray-800 bg-gray-900/40 p-4">
                <div className="text-xs text-gray-400">EXP</div>
                <div className="mt-1 text-lg font-semibold text-blue-400 latin-font numeric">
                  {monster.exp.toLocaleString()}
                </div>
              </div>
              <div className="rounded-xl border border-gray-800 bg-gray-900/40 p-4">
                <div className="text-xs text-gray-400">체경비</div>
                <div className={`mt-1 text-lg font-semibold latin-font numeric ${getHpPerExpColor(hpPerExp)}`}>
                  {hpPerExp === Infinity ? '∞' : hpPerExp.toFixed(2)}
                </div>
              </div>
              <button
                onClick={() => setShowStats(!showStats)}
                className={`rounded-xl border p-4 transition-all ${
                  showStats
                    ? 'border-blue-500 bg-blue-500/20'
                    : 'border-gray-800 bg-gray-900/40 hover:border-blue-500/50 hover:bg-gray-900/60'
                }`}
              >
                <div className="text-xs text-gray-400">능력치</div>
                <div className="mt-1 flex items-center gap-1 text-lg font-semibold text-gray-100">
                  <span>상세 정보</span>
                  <svg
                    className={`h-4 w-4 transition-transform ${showStats ? 'rotate-180' : ''}`}
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
                </div>
              </button>
            </div>

            {/* 능력치 상세 정보 */}
            {showStats && monster.stats && (
              <div className="mb-6 rounded-2xl border border-gray-800 bg-gray-900/30 p-4">
                <h3 className="mb-4 text-base font-semibold text-gray-100">능력치 상세</h3>
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
                  {monster.stats.mp !== undefined && (
                    <div className="rounded-xl border border-gray-800 bg-gray-900/40 p-3">
                      <div className="text-xs text-gray-400">MP</div>
                      <div className="mt-1 text-base font-semibold text-gray-100 latin-font numeric">
                        {monster.stats.mp.toLocaleString()}
                      </div>
                    </div>
                  )}
                  {monster.stats.knockbackDamage !== undefined && (
                    <div className="rounded-xl border border-gray-800 bg-gray-900/40 p-3">
                      <div className="text-xs text-gray-400">넉백 가능 데미지</div>
                      <div className="mt-1 text-base font-semibold text-gray-100 latin-font numeric">
                        {typeof monster.stats.knockbackDamage === 'string'
                          ? monster.stats.knockbackDamage
                          : monster.stats.knockbackDamage.toLocaleString()}
                      </div>
                    </div>
                  )}
                  {monster.stats.physicalDamage !== undefined && (
                    <div className="rounded-xl border border-gray-800 bg-gray-900/40 p-3">
                      <div className="text-xs text-gray-400">물리 데미지</div>
                      <div className="mt-1 text-base font-semibold text-gray-100 latin-font numeric">
                        {monster.stats.physicalDamage.toLocaleString()}
                      </div>
                    </div>
                  )}
                  {monster.stats.magicDamage !== undefined && (
                    <div className="rounded-xl border border-gray-800 bg-gray-900/40 p-3">
                      <div className="text-xs text-gray-400">마법 데미지</div>
                      <div className="mt-1 text-base font-semibold text-gray-100 latin-font numeric">
                        {monster.stats.magicDamage.toLocaleString()}
                      </div>
                    </div>
                  )}
                  {monster.stats.physicalDefense !== undefined && (
                    <div className="rounded-xl border border-gray-800 bg-gray-900/40 p-3">
                      <div className="text-xs text-gray-400">물리 방어력</div>
                      <div className="mt-1 text-base font-semibold text-gray-100 latin-font numeric">
                        {monster.stats.physicalDefense.toLocaleString()}
                      </div>
                    </div>
                  )}
                  {monster.stats.magicDefense !== undefined && (
                    <div className="rounded-xl border border-gray-800 bg-gray-900/40 p-3">
                      <div className="text-xs text-gray-400">마법 방어력</div>
                      <div className="mt-1 text-base font-semibold text-gray-100 latin-font numeric">
                        {monster.stats.magicDefense.toLocaleString()}
                      </div>
                    </div>
                  )}
                  {monster.stats.speed !== undefined && (
                    <div className="rounded-xl border border-gray-800 bg-gray-900/40 p-3">
                      <div className="text-xs text-gray-400">속도</div>
                      <div className="mt-1 text-base font-semibold text-gray-100 latin-font numeric">
                        {monster.stats.speed.toLocaleString()}
                      </div>
                    </div>
                  )}
                  {monster.stats.requiredAccuracy !== undefined && (
                    <div className="rounded-xl border border-gray-800 bg-gray-900/40 p-3">
                      <div className="text-xs text-gray-400">필요 명중</div>
                      <div className="mt-1 text-base font-semibold text-gray-100 latin-font numeric">
                        {monster.stats.requiredAccuracy.toFixed(2)}
                      </div>
                    </div>
                  )}
                  {monster.stats.mesos !== undefined && (
                    <div className="rounded-xl border border-gray-800 bg-gray-900/40 p-3">
                      <div className="text-xs text-gray-400">메소</div>
                      <div className="mt-1 text-base font-semibold text-yellow-400 latin-font numeric">
                        {monster.stats.mesos.toLocaleString()}
                      </div>
                    </div>
                  )}
                </div>
                {!monster.stats || Object.keys(monster.stats).length === 0 ? (
                  <div className="mt-4 text-center text-sm text-gray-400">
                    능력치 정보가 아직 준비되지 않았습니다.
                  </div>
                ) : null}
              </div>
            )}

            <div className="grid grid-cols-1 gap-6 md:grid-cols-12">
              {/* 왼쪽: 맥락 정보 */}
              <div className="md:col-span-5">
                {/* 출몰 지역 */}
                <div className="mb-6 rounded-2xl border border-gray-800 bg-gray-900/30 p-4">
                  <div className="mb-3 flex items-end justify-between">
                    <h3 className="text-base font-semibold text-gray-100">출몰 지역</h3>
                  </div>

                  {monsterRegions.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {monsterRegions.map((region) => (
                        <span
                          key={region.id}
                          className="rounded-full border border-gray-700 bg-gray-800/40 px-3 py-1.5 text-sm font-medium text-gray-200"
                        >
                          {region.name}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <div className="text-sm text-gray-400">
                      출몰 지역 데이터가 아직 준비되지 않았습니다.
                    </div>
                  )}
                </div>

                {/* 출현 사냥터 (맵) */}
                <div className="mb-6 rounded-2xl border border-gray-800 bg-gray-900/30 p-4">
                  <div className="mb-3 flex items-end justify-between gap-3">
                    <h3 className="text-base font-semibold text-gray-100">
                      출현 사냥터 <span className="text-gray-400">({huntingMaps.length})</span>
                    </h3>
                  </div>

                  {transformsFromMonster && transformsFromHuntingMaps.length > 0 ? (
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 text-xs text-gray-400">
                        <span>이 몬스터는 다음 몬스터를 사냥하여 변신합니다:</span>
                      </div>
                      <div className="flex items-center gap-2 rounded-lg border border-gray-700 bg-gray-800/50 p-2">
                        {onMonsterClick && (
                          <button
                            onClick={() => onMonsterClick(transformsFromMonster)}
                            className="group relative flex shrink-0 items-center gap-2 rounded-lg border border-gray-700 bg-gray-900/50 p-2 transition-colors hover:border-blue-500 hover:bg-gray-800"
                            title={transformsFromMonster.name}
                          >
                            <div className="relative h-10 w-10 overflow-hidden rounded border border-gray-700">
                              <Image
                                src={transformsFromMonster.imageUrl}
                                alt={transformsFromMonster.name}
                                fill
                                className="object-contain"
                                unoptimized
                              />
                            </div>
                            <span className="text-sm font-medium text-gray-200 group-hover:text-blue-400">
                              {transformsFromMonster.name}
                            </span>
                          </button>
                        )}
                        {!onMonsterClick && (
                          <div className="flex shrink-0 items-center gap-2 rounded-lg border border-gray-700 bg-gray-900/50 p-2">
                            <div className="relative h-10 w-10 overflow-hidden rounded border border-gray-700">
                              <Image
                                src={transformsFromMonster.imageUrl}
                                alt={transformsFromMonster.name}
                                fill
                                className="object-contain"
                                unoptimized
                              />
                            </div>
                            <span className="text-sm font-medium text-gray-200">
                              {transformsFromMonster.name}
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="max-h-[140px] overflow-y-auto pr-1">
                        <div className="space-y-2">
                          {transformsFromHuntingMaps.map((m) => {
                            const regionName = regionNameById.get(m.regionId) ?? m.regionId;
                            const spawnCount = m.monsterSpawns?.[transformsFromMonster.id];
                            const levelRange = m.recommendedLevel
                              ? `${m.recommendedLevel.min}~${m.recommendedLevel.max}`
                              : null;

                            return (
                              <div
                                key={m.id}
                                className="flex items-start justify-between gap-3 rounded-xl border border-gray-800 bg-gray-950/20 px-3 py-2"
                              >
                                <div className="min-w-0">
                                  <div className="truncate text-sm font-medium text-gray-100">
                                    {m.name}
                                  </div>
                                  <div className="mt-0.5 flex flex-wrap gap-x-2 gap-y-1 text-xs text-gray-400">
                                    <span className="truncate">{regionName}</span>
                                    {levelRange && (
                                      <>
                                        <span className="text-gray-600">·</span>
                                        <span className="latin-font numeric">추천 {levelRange}</span>
                                      </>
                                    )}
                                  </div>
                                </div>

                                {typeof spawnCount === 'number' && (
                                  <div className="shrink-0 rounded-full border border-gray-800 bg-gray-900/40 px-2.5 py-1 text-xs text-gray-300 latin-font numeric">
                                    최대 {spawnCount}마리
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  ) : huntingMaps.length > 0 ? (
                    <div className="max-h-[140px] overflow-y-auto pr-1">
                      <div className="space-y-2">
                        {huntingMaps.map((m) => {
                          const regionName = regionNameById.get(m.regionId) ?? m.regionId;
                          const spawnCount = m.monsterSpawns?.[monster.id];
                          const levelRange = m.recommendedLevel
                            ? `${m.recommendedLevel.min}~${m.recommendedLevel.max}`
                            : null;

                          return (
                            <div
                              key={m.id}
                              className="flex items-start justify-between gap-3 rounded-xl border border-gray-800 bg-gray-950/20 px-3 py-2"
                            >
                              <div className="min-w-0">
                                <div className="truncate text-sm font-medium text-gray-100">
                                  {m.name}
                                </div>
                                <div className="mt-0.5 flex flex-wrap gap-x-2 gap-y-1 text-xs text-gray-400">
                                  <span className="truncate">{regionName}</span>
                                  {levelRange && (
                                    <>
                                      <span className="text-gray-600">·</span>
                                      <span className="latin-font numeric">추천 {levelRange}</span>
                                    </>
                                  )}
                                </div>
                              </div>

                              {typeof spawnCount === 'number' && (
                                <div className="shrink-0 rounded-full border border-gray-800 bg-gray-900/40 px-2.5 py-1 text-xs text-gray-300 latin-font numeric">
                                  최대 {spawnCount}마리
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ) : (
                    <div className="text-sm text-gray-400">
                      출현 사냥터 데이터가 아직 없습니다. (향후 연동 준비 완료)
                    </div>
                  )}
                </div>

              </div>

              {/* 오른쪽: 행동 정보 (드랍) */}
              <div className="md:col-span-7">
                <div className="rounded-2xl border border-gray-800 bg-gray-900/30 p-4">
                  <div className="mb-3 flex items-end justify-between">
                    <h3 className="text-base font-semibold text-gray-100">
                      드롭 아이템 <span className="text-gray-400">({dropItems.length})</span>
                    </h3>
                    <div className="text-xs text-gray-500">표시 필터 적용됨</div>
                  </div>

                  {dropItems.length > 0 ? (
                    <div className="max-h-[268px] overflow-y-auto pr-1">
                      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
                        {dropItems.map((item) => (
                          <div
                            key={item.id}
                            className="group flex flex-col items-center rounded-xl border border-gray-800 bg-gray-950/20 p-3 transition-colors hover:border-blue-500/60 hover:bg-gray-950/30"
                          >
                            <div className="relative mb-2 h-16 w-16 overflow-hidden rounded-lg border border-gray-800 bg-gray-950">
                              <Image
                                src={item.imageUrl}
                                alt={item.name}
                                fill
                                className="object-contain"
                                unoptimized
                              />
                            </div>
                            <div className="w-full text-center">
                              <div className="text-xs font-medium text-gray-200 line-clamp-2">
                                {item.name}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="rounded-xl border border-gray-800 bg-gray-950/20 p-8 text-center text-gray-400">
                      드롭 아이템 정보가 없습니다.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
