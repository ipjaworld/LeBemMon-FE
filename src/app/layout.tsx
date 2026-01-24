import type { Metadata } from "next";
import { Montserrat } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";

const montserrat = Montserrat({
  variable: "--font-montserrat",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "메이플랜드 레범몬 | 레벨 범위 몬스터 간편 조회",
  description:
    "메이플랜드 레범몬(메랜 레범몬) 검색. 레벨을 입력하면 해당 레벨 ±10 범위의 몬스터를 빠르게 찾고 비교할 수 있습니다.",
  keywords: [
    "레범몬",
    "메랜 레범몬",
    "메이플랜드 레범몬",
    "메랜 레벨 범위 몬스터",
    "메이플랜드",
    "메랜",
    "메이플스토리월드",
    "레벨 범위 몬스터",
    "몬스터 검색",
    "메이플랜드 몬스터",
    "레벨별 몬스터",
  ],
  authors: [{ name: "레범몬" }],
  creator: "레범몬",
  publisher: "레범몬",
  openGraph: {
    title: "메이플랜드 레범몬 | 레벨 범위 몬스터 간편 조회",
    description: "메이플랜드 레범몬(메랜 레범몬) 검색. 레벨 범위 몬스터를 빠르게 찾고 비교하세요.",
    type: "website",
    locale: "ko_KR",
    siteName: "레범몬",
    url: "https://rebemon.xyz",
    images: [
      {
        url: "/icon.png",
        width: 512,
        height: 512,
        alt: "레범몬 파비콘",
      },
    ],
  },
  twitter: {
    card: "summary",
    title: "메이플랜드 레범몬 | 레벨 범위 몬스터 간편 조회",
    description: "메이플랜드 레범몬(메랜 레범몬) 검색. 레벨 범위 몬스터를 빠르게 찾고 비교하세요.",
    images: ["/icon.png"],
  },
  alternates: {
    canonical: "https://rebemon.xyz",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  verification: {
    google: "google42c7fc98589ab843",
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
        <Header />
        {children}
      </body>
    </html>
  );
}