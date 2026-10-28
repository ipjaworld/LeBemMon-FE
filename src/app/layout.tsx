import type { Metadata } from "next";
import { Montserrat } from "next/font/google";
import "./globals.css";
import Header from "@/shared/ui/Header";
import Footer from "@/shared/ui/Footer";

const montserrat = Montserrat({
  variable: "--font-montserrat",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://rebemon.xyz"),
  authors: [{ name: "레범몬" }],
  creator: "레범몬",
  publisher: "레범몬",
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
  openGraph: {
    type: "website",
    locale: "ko_KR",
    siteName: "레범몬",
    images: [
      { url: "/icon.png", width: 512, height: 512, alt: "레범몬 파비콘" },
    ],
  },
  twitter: {
    card: "summary",
    images: ["/icon.png"],
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
        <div className="flex flex-col min-h-screen">
          <Header />
          <main className="flex-1">
            {children}
          </main>
          <Footer />
        </div>
      </body>
    </html>
  );
}