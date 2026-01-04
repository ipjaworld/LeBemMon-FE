import { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: '레범몬 : 메이플랜드 레벨 범위 몬스터 간편 조회',
    short_name: '레범몬',
    description: '메이플랜드 레벨 범위 몬스터를 간편하게 검색하고 비교해보세요!',
    start_url: '/',
    display: 'standalone',
    background_color: '#1a1a1a',
    theme_color: '#6366f1',
    icons: [
      {
        src: '/icon.png',
        sizes: '512x512',
        type: 'image/png',
      },
    ],
  };
}


