'use client';

import { useState, useRef, useEffect, useMemo } from 'react';
import { Item } from '@/domains/entities/item/types/item';
import { matchesSearch, getMatchScore } from '@/shared/utils/hangul';

interface ItemComboBoxProps {
  items: Item[];
  value: string;
  onChange: (itemId: string) => void;
  placeholder?: string;
}

export default function ItemComboBox({
  items,
  value,
  onChange,
  placeholder = '아이템을 선택하세요',
}: ItemComboBoxProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const selectedItem = items.find((item) => item.id === value);

  // 검색 및 정렬된 아이템 목록
  const filteredAndSortedItems = useMemo(() => {
    if (!searchQuery.trim()) {
      return items;
    }

    const matched = items.filter((item) => matchesSearch(item.name, searchQuery));
    
    // 매칭 점수로 정렬
    return matched.sort((a, b) => {
      const scoreA = getMatchScore(a.name, searchQuery);
      const scoreB = getMatchScore(b.name, searchQuery);
      return scoreB - scoreA;
    });
  }, [items, searchQuery]);

  // 외부 클릭 감지
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchQuery('');
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [isOpen]);

  // 드롭다운 열릴 때 입력 필드 포커스
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // 키보드 네비게이션
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) {
      if (e.key === 'Enter' || e.key === 'ArrowDown') {
        setIsOpen(true);
        e.preventDefault();
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev < filteredAndSortedItems.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : 0));
        break;
      case 'Enter':
        e.preventDefault();
        if (filteredAndSortedItems[highlightedIndex]) {
          handleItemSelect(filteredAndSortedItems[highlightedIndex].id);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        setSearchQuery('');
        break;
    }
  };

  const handleItemSelect = (itemId: string) => {
    onChange(itemId);
    setIsOpen(false);
    setSearchQuery('');
    setHighlightedIndex(0);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setHighlightedIndex(0);
    if (!isOpen) {
      setIsOpen(true);
    }
  };

  const handleInputFocus = () => {
    setIsOpen(true);
  };

  // 하이라이트된 항목이 보이도록 스크롤
  useEffect(() => {
    if (isOpen && dropdownRef.current) {
      const highlightedElement = dropdownRef.current.children[highlightedIndex] as HTMLElement;
      if (highlightedElement) {
        highlightedElement.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [highlightedIndex, isOpen]);

  return (
    <div ref={containerRef} className="relative">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={isOpen ? searchQuery : (selectedItem ? selectedItem.name : '')}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="w-full px-4 py-2 bg-neutral-10 border border-neutral-30 rounded text-neutral-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="button"
          onClick={() => {
            setIsOpen(!isOpen);
            if (!isOpen) {
              setSearchQuery('');
            }
          }}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-neutral-60 hover:text-neutral-80"
        >
          <svg
            className={`w-5 h-5 transition-transform ${isOpen ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      {isOpen && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-1 bg-neutral-10 border border-neutral-30 rounded shadow-lg max-h-60 overflow-y-auto"
        >
          {filteredAndSortedItems.length === 0 ? (
            <div className="px-4 py-2 text-neutral-60 text-sm">검색 결과가 없습니다.</div>
          ) : (
            filteredAndSortedItems.map((item, index) => (
              <div
                key={item.id}
                onClick={() => handleItemSelect(item.id)}
                className={`px-4 py-2 cursor-pointer text-sm ${
                  index === highlightedIndex
                    ? 'bg-blue-500 text-white'
                    : 'text-neutral-80 hover:bg-neutral-20'
                }`}
                onMouseEnter={() => setHighlightedIndex(index)}
              >
                <div className="flex justify-between items-center">
                  <span>{item.name}</span>
                  {item.reqLevel && (
                    <span className={`text-xs ${index === highlightedIndex ? 'text-blue-100' : 'text-neutral-60'}`}>
                      Lv.{item.reqLevel}
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
