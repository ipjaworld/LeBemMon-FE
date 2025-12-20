import MonsterSearch from '@/components/MonsterSearch';
import { Monster } from '@/types/monster';
import monsterData from '@/data/monster_data.json';

export default function Home() {
  const monsters = monsterData as Monster[];

  return <MonsterSearch monsters={monsters} />;
}