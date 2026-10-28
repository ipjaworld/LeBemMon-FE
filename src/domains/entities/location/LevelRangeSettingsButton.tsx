'use client';

import { useEffect, useMemo, useRef, useState } from 'react';

interface LevelRangeSettingsButtonProps {
  showRebemonOnly: boolean;
  onChangeShowRebemonOnly: (next: boolean) => void;
  lowerOffset: number;
  upperOffset: number;
  onChangeLowerOffset: (next: number) => void;
  onChangeUpperOffset: (next: number) => void;
}

function clampInt(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, Math.trunc(value)));
}

export default function LevelRangeSettingsButton({
  showRebemonOnly,
  onChangeShowRebemonOnly,
  lowerOffset,
  upperOffset,
  onChangeLowerOffset,
  onChangeUpperOffset,
}: LevelRangeSettingsButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const tooltip = showRebemonOnly
    ? '레범몬만 보기가 설정되었습니다.'
    : '유저가 지정한 범위로 설정되었습니다.';

  const rangeLabel = useMemo(() => {
    if (showRebemonOnly) return '±10';
    return `-${lowerOffset}/+${upperOffset}`;
  }, [lowerOffset, showRebemonOnly, upperOffset]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div className="relative flex-shrink-0" ref={containerRef}>
      <button
        type="button"
        title={tooltip}
        aria-label="레벨 범위 설정"
        aria-haspopup="dialog"
        aria-expanded={isOpen}
        onClick={() => setIsOpen((v) => !v)}
        className={`h-10 inline-flex items-center gap-2 rounded-lg border-2 px-3 text-xs font-semibold transition-all ${
          isOpen
            ? 'border-gray-500 bg-gray-800 text-gray-100'
            : 'border-gray-700 bg-gray-800 text-gray-300 hover:border-blue-500/50 hover:bg-gray-750 hover:text-gray-100 active:scale-95'
        }`}
      >
        {/* gear (settings) icon */}
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
        <span className="latin-font numeric">{rangeLabel}</span>
      </button>

      {isOpen && (
        <>
          {/* arrow */}
          <div className="absolute top-full left-6 z-10 -mt-1">
            <div className="h-3 w-3 rotate-45 border-l border-t border-gray-700 bg-gray-800"></div>
          </div>

          <div className="absolute top-full left-0 z-10 mt-2 w-[min(22rem,calc(100vw-2rem))] rounded-lg border border-gray-700 bg-gray-800 p-4 shadow-xl">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <div className="text-sm font-semibold text-gray-200">범위 설정</div>
                <div className="mt-0.5 text-xs text-gray-400">
                  레벨 기준으로 <span className="latin-font numeric font-medium">{rangeLabel}</span> 범위를 적용합니다.
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="rounded p-1 text-gray-400 hover:bg-gray-700 hover:text-gray-200 transition-colors"
                aria-label="닫기"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <label className="flex items-start gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showRebemonOnly}
                onChange={(e) => onChangeShowRebemonOnly(e.target.checked)}
                className="mt-0.5 w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500 focus:ring-2 cursor-pointer"
              />
              <span>
                <div className="text-sm font-medium text-gray-200">레범몬만 보기</div>
                <div className="text-xs text-gray-400">
                  켜면 범위가 항상 <span className="latin-font numeric font-medium">-10/+10</span>으로 고정됩니다.
                </div>
              </span>
            </label>

            <div className="mt-4 grid grid-cols-2 gap-3">
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-300">
                  낮은 범위 (레벨 -)
                </label>
                <input
                  type="number"
                  min={0}
                  max={200}
                  inputMode="numeric"
                  disabled={showRebemonOnly}
                  value={showRebemonOnly ? 10 : lowerOffset}
                  onChange={(e) => {
                    const raw = e.target.value;
                    const next = raw === '' ? 0 : Number(raw);
                    if (!Number.isFinite(next)) return;
                    onChangeLowerOffset(clampInt(next, 0, 200));
                  }}
                  className={`latin-font numeric w-full rounded-lg border px-3 py-2 text-gray-100 placeholder:text-gray-500 focus:outline-none focus:ring-2 ${
                    showRebemonOnly
                      ? 'border-gray-700 bg-gray-900/40 text-gray-500'
                      : 'border-gray-600 bg-gray-700 focus:border-blue-400 focus:ring-blue-400'
                  }`}
                />
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-gray-300">
                  높은 범위 (레벨 +)
                </label>
                <input
                  type="number"
                  min={0}
                  max={200}
                  inputMode="numeric"
                  disabled={showRebemonOnly}
                  value={showRebemonOnly ? 10 : upperOffset}
                  onChange={(e) => {
                    const raw = e.target.value;
                    const next = raw === '' ? 0 : Number(raw);
                    if (!Number.isFinite(next)) return;
                    onChangeUpperOffset(clampInt(next, 0, 200));
                  }}
                  className={`latin-font numeric w-full rounded-lg border px-3 py-2 text-gray-100 placeholder:text-gray-500 focus:outline-none focus:ring-2 ${
                    showRebemonOnly
                      ? 'border-gray-700 bg-gray-900/40 text-gray-500'
                      : 'border-gray-600 bg-gray-700 focus:border-blue-400 focus:ring-blue-400'
                  }`}
                />
              </div>
            </div>

            {showRebemonOnly && (
              <div className="mt-3 text-xs text-gray-500">
                레범몬 모드에서는 범위 커스텀이 잠깐 비활성화됩니다.
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

