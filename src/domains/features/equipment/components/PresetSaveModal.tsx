'use client';

import { useState, useEffect, useRef } from 'react';

interface PresetSaveModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string) => void;
  initialName?: string;
}

export default function PresetSaveModal({
  isOpen,
  onClose,
  onSave,
  initialName = '',
}: PresetSaveModalProps) {
  const [name, setName] = useState(initialName);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setName(initialName);
      requestAnimationFrame(() => inputRef.current?.focus());
    }
  }, [isOpen, initialName]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = name.trim();
    if (trimmed) {
      onSave(trimmed);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="preset-save-title"
    >
      <div
        className="w-full max-w-sm rounded-lg bg-neutral-10 p-6 shadow-xl border border-neutral-30"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="preset-save-title" className="text-lg font-semibold text-foreground mb-4">
          프리셋 저장
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="preset-name" className="block text-sm font-medium text-neutral-70 mb-1">
              프리셋 이름
            </label>
            <input
              ref={inputRef}
              id="preset-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="예: 131 마법사 올INT"
              className="w-full px-3 py-2 bg-neutral-0 border border-neutral-30 rounded text-foreground placeholder:text-neutral-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoComplete="off"
            />
          </div>
          <div className="flex gap-2 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded bg-neutral-20 text-neutral-70 hover:bg-neutral-30 transition-colors"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={!name.trim()}
              className="px-4 py-2 rounded bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              저장
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
