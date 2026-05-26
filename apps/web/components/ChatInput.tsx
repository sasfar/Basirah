'use client';

import { useState, KeyboardEvent } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-white to-white/95 dark:from-slate-900 dark:to-slate-900/95 border-t border-slate-200 dark:border-slate-700 backdrop-blur-sm">
      <div className="container mx-auto px-4 py-4 max-w-4xl">
        <div className="flex items-end space-x-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder="Ask a question about Islam... (Shift+Enter for new line)"
            rows={1}
            className="flex-1 resize-none rounded-2xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-5 py-3 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 dark:focus:ring-emerald-400 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed transition-all max-h-32"
            style={{
              height: 'auto',
              minHeight: '48px',
            }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement;
              target.style.height = 'auto';
              target.style.height = target.scrollHeight + 'px';
            }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || disabled}
            className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 dark:disabled:bg-slate-700 text-white rounded-2xl p-3 transition-all disabled:cursor-not-allowed shadow-lg hover:shadow-xl disabled:shadow-none"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 text-center">
          Answers are grounded in the Quran and authentic Hadith
        </p>
      </div>
    </div>
  );
}
