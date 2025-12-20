import { Monster } from '@/types/monster';
import Image from 'next/image';
import { useState } from 'react';

interface MonsterCardProps {
  monster: Monster;
  isExpiringSoon?: boolean;
  userLevel?: number;
}

export default function MonsterCard({ monster, isExpiringSoon, userLevel }: MonsterCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  
  // 레벨 차이가 5를 초과하는지 확인
  const isOutOfPartyExpRange = userLevel !== undefined && Math.abs(userLevel - monster.level) > 5;

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
      {/* 경고 아이콘 (레벨 차이 5 초과) */}
      {isOutOfPartyExpRange && (
        <div className="absolute left-2 top-2 z-10">
          <div className="relative">
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
            {isHovered && (
              <div className="absolute left-0 top-6 z-20 w-48 rounded-md bg-yellow-600 px-3 py-1.5 text-xs text-white shadow-lg">
                레벨 범위가 5 이내가 아니어서 파티 경험치를 획득할 수 없습니다
                <div className="absolute -top-1 left-2 h-2 w-2 rotate-45 bg-yellow-600"></div>
              </div>
            )}
          </div>
        </div>
      )}
      
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