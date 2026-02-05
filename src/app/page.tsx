import type { Metadata } from 'next';
import MonsterSearch from '@/domains/features/monster/components/MonsterSearch';
import { Monster } from '@/domains/features/monster/types/monster';
import monsterData from '@/domains/features/monster/data/monster_data.json';

export const metadata: Metadata = {
  title: '메이플랜드 레범몬 | 레벨 범위 몬스터 간편 조회',
  description:
    '메이플랜드 레범몬(메랜 레범몬) 검색. 레벨을 입력하면 해당 레벨 ±10 범위의 몬스터를 빠르게 찾고 비교할 수 있습니다.',
  keywords: [
    '레범몬',
    '메랜 레범몬',
    '메이플랜드 레범몬',
    '메랜 레벨 범위 몬스터',
    '메이플랜드',
    '메랜',
    '메이플스토리월드',
    '레벨 범위 몬스터',
    '몬스터 검색',
    '메이플랜드 몬스터',
    '레벨별 몬스터',
  ],
  openGraph: {
    title: '메이플랜드 레범몬 | 레벨 범위 몬스터 간편 조회',
    description: '메이플랜드 레범몬(메랜 레범몬) 검색. 레벨 범위 몬스터를 빠르게 찾고 비교하세요.',
    url: 'https://rebemon.xyz',
  },
  twitter: {
    title: '메이플랜드 레범몬 | 레벨 범위 몬스터 간편 조회',
    description: '메이플랜드 레범몬(메랜 레범몬) 검색. 레벨 범위 몬스터를 빠르게 찾고 비교하세요.',
  },
  alternates: {
    canonical: 'https://rebemon.xyz',
  },
};

export default function Home() {
  const monsters = monsterData as Monster[];
  return <MonsterSearch monsters={monsters} />;
}
