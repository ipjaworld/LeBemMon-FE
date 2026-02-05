'use client';

import { useState, useMemo } from 'react';
import { Monster } from '@/domains/features/monster/types/monster';
import monsterData from '@/domains/features/monster/data/monster_data.json';
import regionData from '@/domains/entities/location/data/region_data.json';
import MonsterDetailModal from '@/domains/features/monster/components/MonsterDetailModal';

// 신뢰도 높은 알파벳 드롭 정보 (제보 자료 - 신뢰도 100%)
const VERIFIED_ALPHABET_MONSTERS: Record<string, string[]> = {
  'H': ['파랑버섯', '옥토퍼스', '스톤골렘', '듀얼 파이렛', '다크레쉬', '아이스 드레이크', '검은 켄타우로스', '하급닌자', '블랙라츠', '비급', '본피쉬'],
  'A': ['사이티', 'G팬텀워치', '머미독', '브라운테니', '크로노스', '포이즌 푸퍼', '프리저', '도라지'],
  'P': ['뿔버섯', '플래툰크로노스', '사이티', '믹스골렘', '쿨리좀비', '콜드아이', '호저', '흑저', '별다람쥐', '바나드그레이', '호문클루', '주니어카투스', '러스터픽시', '루모', '트리플루모', '훈련용짚인형', '파이어보어', '스켈레톤사병'],
  'Y': ['뿔버섯', '슬라임', '호돌이', '네펜데스', '다크네펜데스', '미스릴뮤테', '라츠', '레츠', '묘선', '푸른 켄타우로스', '다크 코니언'],
  'N': ['루나픽시', '커즈아이', '네오휴로이드', '헹키', '루이넬', '마티안', '초록버섯', '리본돼지', '깨비', '뉴트주니어'],
  'E': ['옥토퍼스', '루나픽시', '화이트팽', '스타픽시', '데스테니', '좀비버섯', '듀얼버크', '스켈독', '팬더테니', '타우로마시스'],
  'W': ['파랑버섯', '다크와이번', '스텀프', '빨간달팽이', '늙은도라지', '레쉬', '마스터크로노스', '미요캐츠', '강화된 미스릴뮤테', '양', '타우로스피어', '네스트골렘', '스켈로스'],
  'R': ['플래툰 크로노스', '리게이터', '크로코', '주니어스톤볼', '헥터', '마이너 좀비', '망둥이', '틱톡', '스콜피언', '울트라그레이', '바이킹'],
};

// 알파벳 드롭 정보 (전체 데이터 - 기존 + 제보)
const ALPHABET_MONSTERS: Record<string, string[]> = {
  'H': ['검은 켄타우로스', '파란버섯', '파랑버섯', '옥토퍼스', '스톤골렘', '듀얼 파이렛', '다크레쉬', '다크 레쉬', '아이스 드레이크', '아이스드레이크', '하급닌자', '블랙라츠', '블랙 라츠', '비급', '본피쉬', '본 피쉬', '삼미호', '블루와이번', '예티', '호브', '메카티안', '돼지', '핑크테니', '다크와이번'],
  'A': ['사이티', 'G팬텀워치', '머미독', '브라운테니', '크로노스', '포이즌 푸퍼', '포이즌푸퍼', '프리저', '프리져', '도라지', '스파커', '와일드보어', '구름여우', '리셀스퀴드', '다크엑스텀프', '벨라모아', '스켈레톤지휘관', '라이오너', '망령', '샐리온'],
  'P': ['뿔버섯', '플래툰크로노스', '플래툰 크로노스', '사이티', '믹스골렘', '쿨리좀비', '콜드아이', '호저', '흑저', '별다람쥐', '바나드그레이', '호문클루', '호문쿨루', '주니어카투스', '러스터픽시', '루모', '트리플루모', '훈련용짚인형', '파이어보어', '스켈레톤사병', '페페', '핀호브'],
  'Y': ['뿔버섯', '슬라임', '호돌이', '네펜데스', '다크네펜데스', '미스릴뮤테', '라츠', '레츠', '묘선', '푸른 켄타우로스', '다크 코니언', '다크코니언', '붉은 켄타우로스', '레쉬', '호걸', '스티지', '비틀'],
  'N': ['루나픽시', '커즈아이', '네오휴로이드', '네오 휴로이드', '헹키', '루이넬', '마티안', '초록버섯', '리본돼지', '깨비', '뉴트주니어', '스타픽시', '하프', '주니어페페', '리티', '파란달팽이', '로이드', '상급닌자', '주황버섯', '옐로우 버블티'],
  'E': ['옥토퍼스', '루나픽시', '화이트팽', '스타픽시', '데스테니', '좀비버섯', '듀얼버크', '스켈독', '팬더테니', '타우로마시스', '블러드 하프', '물도깨비', '버크', '삼미호', '주니어레이스', '듀얼 비틀'],
  'W': ['파랑버섯', '파란버섯', '다크와이번', '스텀프', '빨간달팽이', '늙은도라지', '늙은 도라지', '레쉬', '마스터크로노스', '마스터 크로노스', '미요캐츠', '강화된 미스릴뮤테', '양', '타우로스피어', '네스트골렘', '스켈로스', '주황버섯', '월묘', '와일드보어', '쿨리좀비', '믹스골렘'],
  'R': ['플래툰 크로노스', '플래툰크로노스', '리게이터', '크로코', '주니어스톤볼', '헥터', '마이너 좀비', '마이너좀비', '망둥이', '틱톡', '스콜피언', '울트라그레이', '바이킹', '리티', '샐리온', '페어리'],
};

// 이름 변형 매핑
const NAME_VARIANTS: Record<string, string[]> = {
  '파란달팽이': ['파란 달팽이', '파랑버섯'],
  '파랑버섯': ['파란버섯', '파란 달팽이'],
  '빨간달팽이': ['빨간 달팽이'],
  '스포어': ['스포아'],
  '검은 켄타우로스': ['검은켄타우로스', '검켄'],
  '마스크피쉬': ['마스크피시'],
  '붉은 켄타우로스': ['붉은켄타로우스', '붉은켄타우로스'],
  '하프': ['일반하프'],
  '주니어페페 인형': ['주니어페페인형', '페페인형'],
  '푸른 켄타우로스': ['푸른켄타우로스', '푸켄'],
  '헹키': ['행키'],
  '마이너 좀비': ['마이너좀비'],
  '주니어 예티': ['주니어예티'],
  '주니어 샐리온': ['주니어샐리온'],
  '블랙 라츠': ['블랙라츠'],
  '스톤볼': ['주니어 스톤볼', '주니어스톤볼'],
  '블러드 하프': ['블러드하프'],
  '다크엑스텀프': ['다크 엑스텀프'],
  '마스터크로노스': ['마스터 크로노스'],
  '본피쉬': ['본 피쉬'],
  '네오 휴로이드': ['네오휴로이드'],
  '듀얼 비틀': ['듀얼비틀'],
  '샐리온': ['주니어 샐리온'],
  '데스테니': ['마스터 데스테니'],
  '다크레쉬': ['다크 레쉬'],
  '아이스 드레이크': ['아이스드레이크'],
  '포이즌 푸퍼': ['포이즌푸퍼'],
  '프리저': ['프리져'],
  '플래툰크로노스': ['플래툰 크로노스'],
  '플래툰 크로노스': ['플래툰크로노스'],
  '호문클루': ['호문쿨루'],
  '호문쿨루': ['호문클루'],
  '다크 코니언': ['다크코니언'],
  '다크코니언': ['다크 코니언'],
  '늙은도라지': ['늙은 도라지'],
  '늙은 도라지': ['늙은도라지'],
  '강화된 미스릴뮤테': ['강화된미스릴뮤테'],
  '미스릴뮤테': ['미스릴 뮤테'],
};

// 이름 정규화 함수
function normalizeName(name: string): string {
  return name.replace(/\s+/g, '');
}

// 몬스터 이름에서 알파벳 접미사 제거 (예: "검은 켄타우로스 H" -> "검은 켄타우로스")
function removeAlphabetSuffix(name: string): string {
  const match = name.match(/^(.+?)\s+([A-Z])$/);
  if (match) {
    return match[1].trim();
  }
  return name;
}

// 알파벳 정보 타입
type AlphabetInfo = {
  alphabet: string;
  isVerified: boolean;
};

// 몬스터가 특정 알파벳을 드롭하는지 확인 (신뢰도 포함)
function isMonsterInList(monsterName: string, monsterList: string[]): boolean {
  const cleanedName = removeAlphabetSuffix(monsterName);
  const normalized = normalizeName(cleanedName);
  
  for (const monster of monsterList) {
    const normalizedMonster = normalizeName(monster);
    
    if (normalizedMonster === normalized) {
      return true;
    }
    
    const variants = NAME_VARIANTS[monster] || [];
    for (const variant of variants) {
      if (normalizeName(variant) === normalized) {
        return true;
      }
    }
  }
  
  return false;
}

// 몬스터 이름으로 알파벳 찾기 (신뢰도 정보 포함)
function getAlphabetsForMonster(monsterName: string): AlphabetInfo[] {
  const cleanedName = removeAlphabetSuffix(monsterName);
  const normalized = normalizeName(cleanedName);
  const alphabetMap = new Map<string, boolean>();
  
  // 전체 데이터에서 알파벳 찾기
  for (const [alphabet, monsters] of Object.entries(ALPHABET_MONSTERS)) {
    if (isMonsterInList(monsterName, monsters)) {
      // 신뢰도 높은 데이터에 포함되어 있는지 확인
      const verifiedMonsters = VERIFIED_ALPHABET_MONSTERS[alphabet] || [];
      const isVerified = isMonsterInList(monsterName, verifiedMonsters);
      alphabetMap.set(alphabet, isVerified);
    }
  }
  
  // 알파벳 순서대로 정렬하여 반환
  return Array.from(alphabetMap.entries())
    .map(([alphabet, isVerified]) => ({ alphabet, isVerified }))
    .sort((a, b) => a.alphabet.localeCompare(b.alphabet));
}

type ViewMode = 'region' | 'alphabet';

export default function EventPageClient() {
  const monsters = monsterData as Monster[];
  const regions = regionData as Array<{ id: string; name: string; parentId: string | null; type: string }>;
  
  const [viewMode, setViewMode] = useState<ViewMode>('region');
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  const [selectedAlphabet, setSelectedAlphabet] = useState<string | null>(null);
  const [selectedMonster, setSelectedMonster] = useState<Monster | null>(null);

  const monstersByRegion = useMemo(() => {
    const grouped: Record<string, Array<Monster & { alphabets: AlphabetInfo[] }>> = {};
    const monsterMap = new Map<string, Monster & { alphabets: AlphabetInfo[] }>();
    
    monsters.forEach((monster) => {
      const alphabets = getAlphabetsForMonster(monster.name);
      if (alphabets.length === 0) return;
      
      const existing = monsterMap.get(monster.id);
      if (existing) {
        // 중복 제거 및 병합
        const alphabetMap = new Map<string, boolean>();
        existing.alphabets.forEach(a => alphabetMap.set(a.alphabet, a.isVerified));
        alphabets.forEach(a => {
          const current = alphabetMap.get(a.alphabet);
          // 둘 중 하나라도 verified면 verified로 유지
          alphabetMap.set(a.alphabet, current === true || a.isVerified);
        });
        existing.alphabets = Array.from(alphabetMap.entries())
          .map(([alphabet, isVerified]) => ({ alphabet, isVerified }))
          .sort((a, b) => a.alphabet.localeCompare(b.alphabet));
      } else {
        const monsterWithAlphabets = { ...monster, alphabets };
        monsterMap.set(monster.id, monsterWithAlphabets);
      }
      
      const regionIds = monster.regionIds || [];
      regionIds.forEach((regionId) => {
        if (!grouped[regionId]) {
          grouped[regionId] = [];
        }
        const existingInRegion = grouped[regionId].find(m => m.id === monster.id);
        if (!existingInRegion) {
          grouped[regionId].push(monsterMap.get(monster.id)!);
        }
      });
    });
    
    return grouped;
  }, [monsters]);

  const monstersByAlphabet = useMemo(() => {
    const grouped: Record<string, Array<Monster & { alphabets: AlphabetInfo[] }>> = {};
    const monsterMap = new Map<string, Monster & { alphabets: AlphabetInfo[] }>();
    
    monsters.forEach((monster) => {
      const alphabets = getAlphabetsForMonster(monster.name);
      if (alphabets.length === 0) return;
      
      const monsterWithAlphabets = { ...monster, alphabets };
      monsterMap.set(monster.id, monsterWithAlphabets);
      
      alphabets.forEach((alphabetInfo) => {
        const alphabet = alphabetInfo.alphabet;
        if (!grouped[alphabet]) {
          grouped[alphabet] = [];
        }
        const existingInAlphabet = grouped[alphabet].find(m => m.id === monster.id);
        if (!existingInAlphabet) {
          grouped[alphabet].push(monsterWithAlphabets);
        }
      });
    });
    
    return grouped;
  }, [monsters]);

  const filteredRegions = useMemo(() => {
    const regionMap = new Map(regions.map(r => [r.id, r]));
    const filtered = Object.keys(monstersByRegion)
      .map(regionId => regionMap.get(regionId))
      .filter(Boolean)
      .sort((a, b) => a!.name.localeCompare(b!.name));
    
    return filtered;
  }, [monstersByRegion, regions]);

  const availableAlphabets = useMemo(() => {
    return Object.keys(monstersByAlphabet).sort();
  }, [monstersByAlphabet]);

  const displayedMonsters = useMemo(() => {
    if (viewMode === 'region') {
      if (!selectedRegion) {
        const monsterMap = new Map<string, Monster & { alphabets: AlphabetInfo[] }>();
        Object.values(monstersByRegion).flat().forEach(monster => {
          const existing = monsterMap.get(monster.id);
          if (existing) {
            // 중복 제거 및 병합
            const alphabetMap = new Map<string, boolean>();
            existing.alphabets.forEach(a => alphabetMap.set(a.alphabet, a.isVerified));
            monster.alphabets.forEach(a => {
              const current = alphabetMap.get(a.alphabet);
              alphabetMap.set(a.alphabet, current === true || a.isVerified);
            });
            existing.alphabets = Array.from(alphabetMap.entries())
              .map(([alphabet, isVerified]) => ({ alphabet, isVerified }))
              .sort((a, b) => a.alphabet.localeCompare(b.alphabet));
          } else {
            monsterMap.set(monster.id, { ...monster });
          }
        });
        return Array.from(monsterMap.values());
      }
      return monstersByRegion[selectedRegion] || [];
    } else {
      if (!selectedAlphabet) {
        const monsterMap = new Map<string, Monster & { alphabets: AlphabetInfo[] }>();
        Object.values(monstersByAlphabet).flat().forEach(monster => {
          const existing = monsterMap.get(monster.id);
          if (existing) {
            // 중복 제거 및 병합
            const alphabetMap = new Map<string, boolean>();
            existing.alphabets.forEach(a => alphabetMap.set(a.alphabet, a.isVerified));
            monster.alphabets.forEach(a => {
              const current = alphabetMap.get(a.alphabet);
              alphabetMap.set(a.alphabet, current === true || a.isVerified);
            });
            existing.alphabets = Array.from(alphabetMap.entries())
              .map(([alphabet, isVerified]) => ({ alphabet, isVerified }))
              .sort((a, b) => a.alphabet.localeCompare(b.alphabet));
          } else {
            monsterMap.set(monster.id, { ...monster });
          }
        });
        return Array.from(monsterMap.values());
      }
      return monstersByAlphabet[selectedAlphabet] || [];
    }
  }, [viewMode, selectedRegion, selectedAlphabet, monstersByRegion, monstersByAlphabet]);

  return (
    <div className="min-h-screen bg-neutral-0">
      <div className="container mx-auto px-4 py-4 md:py-8">
        <div className="mb-4 md:mb-6">
          <h1 className="text-xl md:text-3xl font-bold text-foreground mb-4 md:mb-0">이벤트 알파벳 드롭 몬스터</h1>
          
          <div className="flex gap-2">
            <button
              onClick={() => {
                setViewMode('region');
                setSelectedAlphabet(null);
              }}
              className={`
                flex-1 md:flex-none px-3 md:px-4 py-2 rounded-lg text-sm font-medium transition-colors
                ${viewMode === 'region'
                  ? 'bg-purple-600/30 border border-purple-500/50 text-purple-300 shadow-md shadow-purple-500/20'
                  : 'bg-neutral-10 text-neutral-60 hover:text-foreground hover:bg-neutral-20'
                }
              `}
            >
              지역별 보기
            </button>
            <button
              onClick={() => {
                setViewMode('alphabet');
                setSelectedRegion(null);
              }}
              className={`
                flex-1 md:flex-none px-3 md:px-4 py-2 rounded-lg text-sm font-medium transition-colors
                ${viewMode === 'alphabet'
                  ? 'bg-purple-600/30 border border-purple-500/50 text-purple-300 shadow-md shadow-purple-500/20'
                  : 'bg-neutral-10 text-neutral-60 hover:text-foreground hover:bg-neutral-20'
                }
              `}
            >
              알파벳별 보기
            </button>
          </div>
        </div>
        
        <div className="mb-6">
          {viewMode === 'region' ? (
            <>
              {/* 모바일: select box */}
              <div className="md:hidden">
                <select
                  value={selectedRegion || ''}
                  onChange={(e) => setSelectedRegion(e.target.value || null)}
                  className="w-full px-4 py-2 rounded-lg text-sm font-medium bg-neutral-10 border border-neutral-30 text-foreground focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50"
                >
                  <option value="">전체</option>
                  {filteredRegions.map((region) => (
                    <option key={region!.id} value={region!.id}>
                      {region!.name}
                    </option>
                  ))}
                </select>
              </div>
              {/* 데스크톱: 버튼 그리드 */}
              <div className="hidden md:flex flex-wrap gap-2">
                <button
                  onClick={() => setSelectedRegion(null)}
                  className={`
                    px-4 py-2 rounded-lg text-sm font-medium transition-colors border
                    ${selectedRegion === null
                      ? 'bg-purple-600/30 border-purple-500/50 text-purple-300 shadow-md shadow-purple-500/20'
                      : 'bg-neutral-10 border-neutral-30 text-neutral-60 hover:text-foreground hover:bg-neutral-20 hover:border-neutral-40'
                    }
                  `}
                >
                  전체
                </button>
                {filteredRegions.map((region) => (
                  <button
                    key={region!.id}
                    onClick={() => setSelectedRegion(region!.id)}
                    className={`
                      px-4 py-2 rounded-lg text-sm font-medium transition-colors border
                      ${selectedRegion === region!.id
                        ? 'bg-purple-600/30 border-purple-500/50 text-purple-300 shadow-md shadow-purple-500/20'
                        : 'bg-neutral-10 border-neutral-30 text-neutral-60 hover:text-foreground hover:bg-neutral-20 hover:border-neutral-40'
                      }
                    `}
                  >
                    {region!.name}
                  </button>
                ))}
              </div>
            </>
          ) : (
            <>
              {/* 모바일: select box */}
              <div className="md:hidden">
                <select
                  value={selectedAlphabet || ''}
                  onChange={(e) => setSelectedAlphabet(e.target.value || null)}
                  className="w-full px-4 py-2 rounded-lg text-sm font-medium bg-neutral-10 border border-neutral-30 text-foreground focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50"
                >
                  <option value="">전체</option>
                  {availableAlphabets.map((alphabet) => (
                    <option key={alphabet} value={alphabet}>
                      {alphabet}
                    </option>
                  ))}
                </select>
              </div>
              {/* 데스크톱: 버튼 그리드 */}
              <div className="hidden md:flex flex-wrap gap-2">
                <button
                  onClick={() => setSelectedAlphabet(null)}
                  className={`
                    px-4 py-2 rounded-lg text-sm font-medium transition-colors border
                    ${selectedAlphabet === null
                      ? 'bg-purple-600/30 border-purple-500/50 text-purple-300 shadow-md shadow-purple-500/20'
                      : 'bg-neutral-10 border-neutral-30 text-neutral-60 hover:text-foreground hover:bg-neutral-20 hover:border-neutral-40'
                    }
                  `}
                >
                  전체
                </button>
                {availableAlphabets.map((alphabet) => (
                  <button
                    key={alphabet}
                    onClick={() => setSelectedAlphabet(alphabet)}
                    className={`
                      px-4 py-2 rounded-lg text-sm font-medium transition-colors border
                      ${selectedAlphabet === alphabet
                        ? 'bg-purple-600/30 border-purple-500/50 text-purple-300 shadow-md shadow-purple-500/20'
                        : 'bg-neutral-10 border-neutral-30 text-neutral-60 hover:text-foreground hover:bg-neutral-20 hover:border-neutral-40'
                      }
                    `}
                  >
                    {alphabet}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        <div className="grid grid-cols-3 md:grid-cols-4 xl:grid-cols-6 gap-4">
          {displayedMonsters.map((monster) => (
            <div
              key={monster.id}
              onClick={() => setSelectedMonster(monster)}
              className="bg-neutral-10 rounded-lg p-3 border border-neutral-30 hover:border-neutral-40 transition-colors cursor-pointer"
            >
              <div className="aspect-square mb-2 bg-neutral-20 rounded overflow-hidden">
                <img
                  src={monster.imageUrl}
                  alt={monster.name}
                  className="w-full h-full object-contain"
                  loading="lazy"
                />
              </div>
              <div className="text-center">
                <h3 className="text-sm font-medium text-foreground mb-1 line-clamp-2">
                  {monster.name}
                </h3>
                <div className="flex flex-wrap gap-1 justify-center">
                  {monster.alphabets.map((alphabetInfo) => (
                    <span
                      key={alphabetInfo.alphabet}
                      className="inline-flex items-center justify-center min-w-[1.5rem] h-6 px-1 rounded bg-neutral-20 text-xs font-bold text-foreground"
                      title={alphabetInfo.isVerified ? undefined : '확인되지 않은 정보'}
                    >
                      {alphabetInfo.alphabet}
                      {!alphabetInfo.isVerified && (
                        <span className="ml-0.5 text-[0.625rem] text-neutral-50">?</span>
                      )}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {displayedMonsters.length === 0 && (
          <div className="text-center py-12 text-neutral-60">
            {viewMode === 'region'
              ? '선택한 지역에 알파벳을 드롭하는 몬스터가 없습니다.'
              : '선택한 알파벳을 드롭하는 몬스터가 없습니다.'
            }
          </div>
        )}
      </div>
      
      <MonsterDetailModal
        monster={selectedMonster}
        onClose={() => setSelectedMonster(null)}
        onMonsterClick={(monster) => setSelectedMonster(monster)}
      />
    </div>
  );
}
