import type { Metadata } from "next";
import { Montserrat } from "next/font/google";
import "./globals.css";

const montserrat = Montserrat({
  variable: "--font-montserrat",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "메이플랜드 레범몬 - 레벨 범위 몬스터 검색 | 메이플스토리월드",
  description: "메이플스토리월드 메이플랜드 레범몬(레벨 범위 몬스터) 검색 서비스. 레벨을 입력하면 해당 레벨 ±10 범위의 몬스터를 빠르게 찾을 수 있습니다. 레범몬, 레벨범위몬스터, 메이플랜드 몬스터 검색, 메랜 몬스터 정보 제공.",
  keywords: ["레범몬", "레벨 범위 몬스터", "레벨범위몬스터", "메이플랜드", "메랜", "메이플스토리월드", "몬스터 검색", "메이플랜드 몬스터", "레벨별 몬스터", "메이플 몬스터 정보"],
  openGraph: {
    title: "메이플랜드 레범몬 - 레벨 범위 몬스터 검색",
    description: "메이플스토리월드 메이플랜드에서 레벨 범위에 맞는 몬스터를 빠르게 검색하세요. 레범몬 정보를 한눈에 확인할 수 있습니다.",
    type: "website",
    locale: "ko_KR",
  },
  twitter: {
    card: "summary",
    title: "메이플랜드 레범몬",
    description: "메이플스토리월드 메이플랜드 레벨 범위 몬스터 검색 서비스",
  },
  alternates: {
    canonical: "https://rebemon.vercel.app",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className="dark">
      <head>
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css"
          crossOrigin="anonymous"
        />
      </head>
      <body
        className={`${montserrat.variable} font-sans antialiased`}
      >
        {children}
      </body>
    </html>
  );
}