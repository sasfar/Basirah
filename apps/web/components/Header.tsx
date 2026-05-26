'use client';

import { SunIcon, MoonIcon, TrashIcon } from '@heroicons/react/24/outline';

interface HeaderProps {
  darkMode: boolean;
  toggleDarkMode: () => void;
  onClearHistory: () => void;
  messageCount: number;
}

export default function Header({
  darkMode,
  toggleDarkMode,
  onClearHistory,
  messageCount,
}: HeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-700 z-10">
      <div className="container mx-auto px-4 py-3 max-w-4xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">🌙</span>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 dark:from-emerald-400 dark:to-teal-400 bg-clip-text text-transparent">
                Basirah
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Islamic Knowledge Assistant
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {messageCount > 0 && (
              <button
                onClick={onClearHistory}
                className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400"
                title="Clear chat history"
              >
                <TrashIcon className="w-5 h-5" />
              </button>
            )}
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-600 dark:text-slate-400"
              title={darkMode ? 'Light mode' : 'Dark mode'}
            >
              {darkMode ? (
                <SunIcon className="w-5 h-5" />
              ) : (
                <MoonIcon className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
