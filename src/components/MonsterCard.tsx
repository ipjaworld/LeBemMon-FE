import { Monster } from '@/types/monster';
import Image from 'next/image';
import { useState } from 'react';

interface MonsterCardProps {
  monster: Monster;
  isExpiringSoon?: boolean;
}

export default function MonsterCard({ monster, isExpiringSoon }: MonsterCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className={`relative flex flex-col items-center rounded-lg border-2 bg-gray-800 p-4 shadow-sm transition-all hover:shadow-md ${
        isExpiringSoon
          ? 'border-red-500'
          : 'border-gray-700'
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {isExpiringSoon && isHovered && (
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
      <h3 className="mb-2 text-base font-semibold text-gray-100 sm:text-lg">
        {monster.name}
      </h3>
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
      </div>
    </div>
  );
}