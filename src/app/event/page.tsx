import type { Metadata } from 'next';
import EventPageClient from '@/components/EventPageClient';

export const metadata: Metadata = {
  title: '이벤트 알파벳 드롭 몬스터 | 레범몬',
  description:
    '메이플랜드(메이플스토리월드) 이벤트 알파벳 드롭 몬스터. 지역별·알파벳별로 어떤 몬스터가 어떤 글자를 드롭하는지 조회할 수 있습니다.',
  keywords: [
    '레범몬',
    '메이플랜드',
    '메이플스토리월드',
    '알파벳 이벤트',
    '알파벳 드롭',
    '이벤트 몬스터',
    '지역별 몬스터',
    '알파벳별 몬스터',
  ],
  openGraph: {
    title: '이벤트 알파벳 드롭 몬스터 | 레범몬',
    description: '메이플랜드 이벤트 알파벳 드롭 몬스터. 지역별·알파벳별 조회.',
    type: 'website',
    locale: 'ko_KR',
    siteName: '레범몬',
    url: 'https://rebemon.xyz/event',
  },
  twitter: {
    card: 'summary',
    title: '이벤트 알파벳 드롭 몬스터 | 레범몬',
    description: '메이플랜드 이벤트 알파벳 드롭 몬스터. 지역별·알파벳별 조회.',
  },
  alternates: {
    canonical: 'https://rebemon.xyz/event',
  },
};

export default function EventPage() {
  return <EventPageClient />;
}
