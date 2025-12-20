'use client';

import { useState, useMemo, useEffect } from 'react';
import MonsterCard from '@/components/MonsterCard';
import Footer from '@/components/Footer';
import { Monster } from '@/types/monster';

type MonsterWithExpiring = Monster & {
  isExpiringSoon: boolean;
};

interface MonsterSearchProps {
  monsters: Monster[];
}

export default function MonsterSearch({ monsters }: MonsterSearchProps) {
  const [level, setLevel] = useState<number | ''>('');

  // document.title 업데이트
  useEffect(() => {
    document.title = level !== '' 
      ? `레벨 ${level} 레범몬 - 메이플랜드 레범몬`
      : '메이플랜드 레범몬';
  }, [level]);

  // 출시된 몬스터만 필터링하고, 레벨 범위로 필터링
  const filteredMonsters = useMemo(() => {
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

    // 레벨 80 이상이면 70 이상의 몬스터도 포함, 그 외에는 ±10 범위
    const filtered = releasedMonsters.filter((monster) => {
      if (levelNum >= 80) {
        // 레벨 80 이상: ±10 범위 또는 70 이상의 몬스터
        return (
          (monster.level >= levelNum - 10 && monster.level <= levelNum + 10) ||
          monster.level >= 70
        );
      } else {
        // 레벨 80 미만: ±10 범위만
        return monster.level >= levelNum - 10 && monster.level <= levelNum + 10;
      }
    });

    // 레벨 1업 시 레범몬이 아니게 되는지 판단
    return filtered
      .map((monster): MonsterWithExpiring => ({
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
      }))
      .sort((a, b) => a.level - b.level);
  }, [level, monsters]) as MonsterWithExpiring[];

  return (
    <div className="flex min-h-screen flex-col bg-gray-900">
      <div className="container mx-auto flex-1 px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8 text-center">
          <h1 className="mb-4 text-3xl font-bold text-gray-100 sm:text-4xl md:text-5xl">
            메이플랜드 레범몬
          </h1>
          <p className="text-base text-gray-400 sm:text-lg">
            레벨을 입력하면 해당 레벨 ±10 범위의 몬스터를 확인할 수 있습니다
          </p>
        </div>

        <div className="mb-8 flex justify-center">
          <div className="w-full max-w-md">
            <label
              htmlFor="level-input"
              className="mb-2 block text-sm font-medium text-gray-400"
            >
              레벨 입력
            </label>
            <input
              id="level-input"
              type="number"
              min="1"
              value={level}
              onChange={(e) => {
                const value = e.target.value;
                setLevel(value === '' ? '' : Number(value));
              }}
              placeholder="예: 50"
              className="latin-font numeric w-full rounded-lg border border-gray-600 bg-gray-800 px-4 py-3 text-lg text-gray-100 shadow-sm placeholder:text-gray-500 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>
        </div>

        {level !== '' && filteredMonsters.length > 0 && (
          <div className="mb-4 text-center text-gray-400">
            <p>
              레벨 <span className="latin-font font-medium">{level}</span> 기준 레범몬 {filteredMonsters.length}개
              {Number(level) >= 80 && (
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
    </div>
  );
}
