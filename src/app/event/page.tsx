'use client';

import { useState, useMemo } from 'react';
import { Monster } from '@/types/monster';
import monsterData from '@/data/monster_data.json';
import regionData from '@/data/region_data.json';

// 알파벳 드롭 정보 (스크립트에서 생성된 데이터 기반)
const ALPHABET_MONSTERS: Record<string, string[]> = {
  'H': ['주황버섯', '콜드샤크', '좀비버섯', '주니어스톤볼', '파이어스톤볼', '레쉬', '울트라그레이', '다크와이번', '돼지', '아이스드레이크'],
  'A': ['리티', '타우로스피어', '루나픽시', '본피쉬', '비틀', '호돌이', '초록버섯', '마스터크로노스', '화이트팽', '스텀프', '주니어페페 인형', '트위터', '마이너 좀비', '페어리'],
  'P': ['쿨리좀비', '헥터', '포이즌푸퍼', '다크클라크', '주니어씰', '블루와이번', '깨비', '레이스', '검은 켄타우로스', '레드와이번', '와일드보어', '파이어보어', '페페', '엑스텀프', '호문쿨루', '머미독'],
  'Y': ['리티', '파란달팽이', '주니어페페', '버크', '스쿠버페페', '파이렛', '구름여우', '하프', '헹키', '스켈독', '버블링', '플라이아이', '마티안', '붉은 켄타우로스', '푸른 켄타우로스'],
  'N': ['리본돼지', '뿔버섯', '프리져', '클라크', '망령', '타우로마시스', '호브', '스켈레톤지휘관', '아이스스톤볼', '푸퍼', '빨간달팽이', '주니어예티', '루이넬', '주니어 샐리온'],
  'E': ['아이언호그', '마스크피쉬', '듀얼버크', '다크리티', '스타픽시', '크로노스', '옐로우버블티', '레츠', '스켈레톤장교', '다크코니언', '큰구름여우', '주니어 예티', '블랙 라츠', '핑크세이버', '스톤볼'],
  'W': ['삼미호', '러스터픽시', '믹스골렘', '스텀프', '초록버섯', '커즈아이', '마티안', '옐로우버블티', '핑크테니', '푸른 켄타우로스', '바이킹', '주니어부기', '고스텀프', '레쉬'],
  'R': ['물도깨비', '망둥이', '푸른 켄타우로스', '블록골렘', '다크엑스텀프', '플래툰크로노스', '분리된페페', '라츠', '스켈레톤사병', '루이넬', '스포어', '붉은 켄타우로스', '월묘', '씨클', '캡틴'],
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
};

// 이름 정규화 함수
function normalizeName(name: string): string {
  return name.replace(/\s+/g, '');
}

// 몬스터 이름으로 알파벳 찾기
function getAlphabetsForMonster(monsterName: string): string[] {
  const normalized = normalizeName(monsterName);
  const alphabets: string[] = [];
  
  for (const [alphabet, monsters] of Object.entries(ALPHABET_MONSTERS)) {
    for (const monster of monsters) {
      const normalizedMonster = normalizeName(monster);
      
      // 정확히 일치
      if (normalizedMonster === normalized) {
        alphabets.push(alphabet);
        break;
      }
      
      // 변형 이름 확인
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

export default function EventPage() {
  const monsters = monsterData as Monster[];
  const regions = regionData as Array<{ id: string; name: string; parentId: string | null; type: string }>;
  
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);

  // 지역별로 몬스터 그룹화
  const monstersByRegion = useMemo(() => {
    const grouped: Record<string, Array<Monster & { alphabets: string[] }>> = {};
    const monsterMap = new Map<string, Monster & { alphabets: string[] }>();
    
    monsters.forEach((monster) => {
      const alphabets = getAlphabetsForMonster(monster.name);
      if (alphabets.length === 0) return; // 알파벳을 드롭하지 않는 몬스터 제외
      
      // 같은 몬스터가 여러 지역에 있을 수 있으므로, 알파벳을 합쳐서 저장
      const existing = monsterMap.get(monster.id);
      if (existing) {
        // 기존 알파벳과 합치기
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
        // 중복 체크
        const existingInRegion = grouped[regionId].find(m => m.id === monster.id);
        if (!existingInRegion) {
          grouped[regionId].push(monsterMap.get(monster.id)!);
        }
      });
    });
    
    return grouped;
  }, [monsters]);

  // 필터링된 지역 목록
  const filteredRegions = useMemo(() => {
    const regionMap = new Map(regions.map(r => [r.id, r]));
    const filtered = Object.keys(monstersByRegion)
      .map(regionId => regionMap.get(regionId))
      .filter(Boolean)
      .sort((a, b) => a!.name.localeCompare(b!.name));
    
    return filtered;
  }, [monstersByRegion, regions]);

  // 선택된 지역의 몬스터
  const displayedMonsters = useMemo(() => {
    if (!selectedRegion) {
      // 전체 보기: 중복 제거
      const monsterMap = new Map<string, Monster & { alphabets: string[] }>();
      Object.values(monstersByRegion).flat().forEach(monster => {
        const existing = monsterMap.get(monster.id);
        if (existing) {
          // 알파벳 합치기
          existing.alphabets = [...new Set([...existing.alphabets, ...monster.alphabets])].sort();
        } else {
          monsterMap.set(monster.id, { ...monster });
        }
      });
      return Array.from(monsterMap.values());
    }
    return monstersByRegion[selectedRegion] || [];
  }, [selectedRegion, monstersByRegion]);

  return (
    <div className="min-h-screen bg-neutral-0">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6 text-foreground">이벤트 알파벳 드롭 몬스터</h1>
        
        {/* 지역 필터 */}
        <div className="mb-6">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedRegion(null)}
              className={`
                px-4 py-2 rounded-lg text-sm font-medium transition-colors
                ${selectedRegion === null
                  ? 'bg-neutral-20 text-foreground'
                  : 'bg-neutral-10 text-neutral-60 hover:text-foreground hover:bg-neutral-20'
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
                  px-4 py-2 rounded-lg text-sm font-medium transition-colors
                  ${selectedRegion === region!.id
                    ? 'bg-neutral-20 text-foreground'
                    : 'bg-neutral-10 text-neutral-60 hover:text-foreground hover:bg-neutral-20'
                  }
                `}
              >
                {region!.name}
              </button>
            ))}
          </div>
        </div>

        {/* 몬스터 그리드 */}
        <div className="grid grid-cols-3 md:grid-cols-4 xl:grid-cols-6 gap-4">
          {displayedMonsters.map((monster) => (
            <div
              key={monster.id}
              className="bg-neutral-10 rounded-lg p-3 border border-neutral-30 hover:border-neutral-40 transition-colors"
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
            선택한 지역에 알파벳을 드롭하는 몬스터가 없습니다.
          </div>
        )}
      </div>
    </div>
  );
}
