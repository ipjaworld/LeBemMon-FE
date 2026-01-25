'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Header() {
  const pathname = usePathname();

  const tabs = [
    { name: '레범몬', path: '/' },
    { name: '이벤트', path: '/event' },
    { name: '장비 시뮬레이터', path: '/equipment' },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-neutral-30 bg-neutral-0">
      <div className="container mx-auto px-4">
        <nav className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-1">
            {tabs.map((tab) => {
              const isActive = pathname === tab.path || 
                (tab.path === '/' && pathname === '/');
              
              return (
                <Link
                  key={tab.path}
                  href={tab.path}
                  className={`
                    px-4 py-2 rounded-lg text-sm font-medium transition-colors
                    ${isActive 
                      ? 'bg-neutral-20 text-foreground' 
                      : 'text-neutral-60 hover:text-foreground hover:bg-neutral-10'
                    }
                  `}
                >
                  {tab.name}
                </Link>
              );
            })}
          </div>
          <div className="hidden md:block text-xs text-neutral-60">
            제작: 가스실광분견(민재쿤)
          </div>
        </nav>
      </div>
    </header>
  );
}
