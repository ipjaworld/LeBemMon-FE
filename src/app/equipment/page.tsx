import type { Metadata } from 'next';
import EquipmentPageClient from '@/domains/features/equipment/components/EquipmentPageClient';

export const metadata: Metadata = {
  title: '장비 시뮬레이터 | 레범몬',
  description:
    '메이플랜드(메이플스토리월드) 장비 시뮬레이터. 직업별 장비 옵션과 스탯을 시뮬레이션하고, 프리셋으로 저장·불러오기할 수 있습니다.',
  keywords: [
    '레범몬',
    '메이플랜드',
    '메이플스토리월드',
    '장비 시뮬레이터',
    '스탯 시뮬레이터',
    '직업별 장비',
    '옵션 시뮬레이션',
  ],
  openGraph: {
    title: '장비 시뮬레이터 | 레범몬',
    description: '메이플랜드 장비 시뮬레이터. 직업별 장비·스탯 시뮬레이션, 프리셋 저장.',
    type: 'website',
    locale: 'ko_KR',
    siteName: '레범몬',
    url: 'https://rebemon.xyz/equipment',
  },
  twitter: {
    card: 'summary',
    title: '장비 시뮬레이터 | 레범몬',
    description: '메이플랜드 장비 시뮬레이터. 직업별 장비·스탯 시뮬레이션, 프리셋 저장.',
  },
  alternates: {
    canonical: 'https://rebemon.xyz/equipment',
  },
};

export default function EquipmentPage() {
  return <EquipmentPageClient />;
}
