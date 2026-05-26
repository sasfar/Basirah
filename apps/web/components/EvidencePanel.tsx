'use client';

import { Evidence } from '@/types';
import { useState } from 'react';

interface EvidencePanelProps {
  evidence: Evidence[];
}

export default function EvidencePanel({ evidence }: EvidencePanelProps) {
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set());

  const toggleExpand = (index: number) => {
    const newExpanded = new Set(expandedIds);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedIds(newExpanded);
  };

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'quran':
        return '📖';
      case 'bukhari':
        return '📚';
      case 'muslim':
        return '📕';
      case 'tafsir':
        return '📜';
      default:
        return '📄';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600 dark:text-green-400';
    if (score >= 0.5) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-slate-500 dark:text-slate-400';
  };

  return (
    <div className="border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50">
      <div className="px-5 py-3 space-y-2">
        {evidence.map((item, index) => (
          <div
            key={index}
            className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden"
          >
            <button
              onClick={() => toggleExpand(index)}
              className="w-full px-4 py-2 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors text-left"
            >
              <div className="flex items-center space-x-2 flex-1">
                <span className="text-sm">{getSourceIcon(item.source_type)}</span>
                <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                  {item.reference}
                </span>
                <span className={`text-xs ${getScoreColor(item.score)}`}>
                  ({Math.round(item.score * 100)}%)
                </span>
              </div>
              <span className="text-xs text-slate-400">
                {expandedIds.has(index) ? '▲' : '▼'}
              </span>
            </button>

            {expandedIds.has(index) && (
              <div className="px-4 py-3 border-t border-slate-100 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/30">
                <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                  {item.text}
                </p>
                {item.metadata && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {item.metadata.surah && (
                      <span className="text-xs px-2 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 rounded">
                        Surah {item.metadata.surah}
                      </span>
                    )}
                    {item.metadata.verse && (
                      <span className="text-xs px-2 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 rounded">
                        Verse {item.metadata.verse}
                      </span>
                    )}
                    {item.metadata.translation && (
                      <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded">
                        {item.metadata.translation}
                      </span>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
