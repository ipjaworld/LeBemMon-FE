'use client';

import { useState, useMemo } from 'react';
import { Monster } from '@/types/monster';
import monsterData from '@/data/monster_data.json';
import regionData from '@/data/region_data.json';
import MonsterDetailModal from '@/components/MonsterDetailModal';

// 알파벳 드롭 정보 (스크립트에서 생성된 데이터 기반)
const ALPHABET_MONSTERS: Record<string, string[]> = {
  'H': ['검은 켄타우로스', '파란버섯', '삼미호', '블루와이번', '본피쉬', '비급', '예티', '호브', '메카티안', '돼지', '핑크테니'],
  'A': ['스파커', '와일드보어', '브라운테니', '포이즌푸퍼', '구름여우', '크로노스', '리셀스퀴드', '다크엑스텀프', '벨라모아', '사이티', '스켈레톤지휘관', '라이오너', '망령', '프리져', '샐리온'],
  'P': ['믹스골렘', '쿨리좀비', '호문쿨루', '뿔버섯', '러스터픽시', '페페', '핀호브'],
  'Y': ['붉은 켄타우로스', '푸른 켄타우로스', '레쉬', '호걸', '슬라임', '스티지', '비틀', '묘선'],
  'N': ['루이넬', '커즈아이', '스타픽시', '네오 휴로이드', '헹키', '마티안', '주니어페페', '리티', '파란달팽이', '로이드', '상급닌자', '주황버섯', '초록버섯'],
  'E': ['데스테니', '좀비버섯', '화이트팽', '루나픽시', '블러드 하프', '물도깨비', '버크', '듀얼버크', '삼미호', '주니어레이스', '듀얼 비틀'],
  'W': ['다크와이번', '주황버섯', '월묘', '마스터크로노스', '와일드보어', '늙은 도라지', '미요캐츠', '쿨리좀비', '스텀프', '믹스골렘'],
  'R': ['바이킹', '리게이터', '크로코', '주니어스톤볼', '헥터', '망둥이', '플래툰크로노스', '리티', '샐리온', '페어리'],
};

// 이름 변형 매핑
const NAME_VARIANTS: Record<string, string[]> = {
  '파란달팽이': ['파란 달팽이'],
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

// 몬스터 이름으로 알파벳 찾기
function getAlphabetsForMonster(monsterName: string): string[] {
  const cleanedName = removeAlphabetSuffix(monsterName);
  const normalized = normalizeName(cleanedName);
  const alphabets: string[] = [];
  
  for (const [alphabet, monsters] of Object.entries(ALPHABET_MONSTERS)) {
    for (const monster of monsters) {
      const normalizedMonster = normalizeName(monster);
      
      if (normalizedMonster === normalized) {
        alphabets.push(alphabet);
        break;
      }
      
      const variants = NAME_VARIANTS[monster] || [];
      for (const variant of variants) {
        if (normalizeName(variant) === normalized) {
          alphabets.push(alphabet);
          break;
        }
      }
    }
  }
  
  return [...new Set(alphabets)].sort();
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
    const grouped: Record<string, Array<Monster & { alphabets: string[] }>> = {};
    const monsterMap = new Map<string, Monster & { alphabets: string[] }>();
    
    monsters.forEach((monster) => {
      const alphabets = getAlphabetsForMonster(monster.name);
      if (alphabets.length === 0) return;
      
      const existing = monsterMap.get(monster.id);
      if (existing) {
        existing.alphabets = [...new Set([...existing.alphabets, ...alphabets])].sort();
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
    const grouped: Record<string, Array<Monster & { alphabets: string[] }>> = {};
    const monsterMap = new Map<string, Monster & { alphabets: string[] }>();
    
    monsters.forEach((monster) => {
      const alphabets = getAlphabetsForMonster(monster.name);
      if (alphabets.length === 0) return;
      
      const monsterWithAlphabets = { ...monster, alphabets };
      monsterMap.set(monster.id, monsterWithAlphabets);
      
      alphabets.forEach((alphabet) => {
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
        const monsterMap = new Map<string, Monster & { alphabets: string[] }>();
        Object.values(monstersByRegion).flat().forEach(monster => {
          const existing = monsterMap.get(monster.id);
          if (existing) {
            existing.alphabets = [...new Set([...existing.alphabets, ...monster.alphabets])].sort();
          } else {
            monsterMap.set(monster.id, { ...monster });
          }
        });
        return Array.from(monsterMap.values());
      }
      return monstersByRegion[selectedRegion] || [];
    } else {
      if (!selectedAlphabet) {
        const monsterMap = new Map<string, Monster & { alphabets: string[] }>();
        Object.values(monstersByAlphabet).flat().forEach(monster => {
          const existing = monsterMap.get(monster.id);
          if (existing) {
            existing.alphabets = [...new Set([...existing.alphabets, ...monster.alphabets])].sort();
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
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-foreground">이벤트 알파벳 드롭 몬스터</h1>
          
          <div className="flex gap-2">
            <button
              onClick={() => {
                setViewMode('region');
                setSelectedAlphabet(null);
              }}
              className={`
                px-4 py-2 rounded-lg text-sm font-medium transition-colors
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
                px-4 py-2 rounded-lg text-sm font-medium transition-colors
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
            <div className="flex flex-wrap gap-2">
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
          ) : (
            <div className="flex flex-wrap gap-2">
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
                  {monster.alphabets.map((alphabet) => (
                    <span
                      key={alphabet}
                      className="inline-flex items-center justify-center w-6 h-6 rounded bg-neutral-20 text-xs font-bold text-foreground"
                    >
                      {alphabet}
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
