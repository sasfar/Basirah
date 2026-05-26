'use client';

import { Message } from '@/types';
import { useState } from 'react';
import EvidencePanel from './EvidencePanel';
import { ClipboardIcon, CheckIcon } from '@heroicons/react/24/outline';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const [showEvidence, setShowEvidence] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (message.type === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] bg-emerald-600 text-white rounded-2xl rounded-tr-sm px-5 py-3 shadow-md">
          <p className="text-sm">{message.content}</p>
        </div>
      </div>
    );
  }

  if (message.type === 'error') {
    return (
      <div className="flex justify-start">
        <div className="max-w-[80%] bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 rounded-2xl rounded-tl-sm px-5 py-3 shadow-md border border-red-200 dark:border-red-800">
          <p className="text-sm">{message.content}</p>
        </div>
      </div>
    );
  }

  // Assistant message
  const confidenceColor =
    (message.confidence ?? 0) >= 0.7
      ? 'text-green-600 dark:text-green-400'
      : (message.confidence ?? 0) >= 0.4
      ? 'text-yellow-600 dark:text-yellow-400'
      : 'text-red-600 dark:text-red-400';

  return (
    <div className="flex justify-start">
      <div className="max-w-[85%] bg-white dark:bg-slate-800 rounded-2xl rounded-tl-sm shadow-lg border border-slate-200 dark:border-slate-700">
        {/* Header */}
        <div className="flex items-center justify-between px-5 pt-3 pb-2 border-b border-slate-100 dark:border-slate-700">
          <div className="flex items-center space-x-2">
            <span className="text-lg">🌙</span>
            <span className="font-semibold text-slate-900 dark:text-slate-100">
              Basirah
            </span>
          </div>
          <div className="flex items-center space-x-3">
            {message.confidence !== undefined && (
              <span className={`text-xs font-medium ${confidenceColor}`}>
                {Math.round(message.confidence * 100)}% confident
              </span>
            )}
            <button
              onClick={copyToClipboard}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
              title="Copy answer"
            >
              {copied ? (
                <CheckIcon className="w-4 h-4 text-green-600" />
              ) : (
                <ClipboardIcon className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="px-5 py-4">
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <p className="text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
          </div>
        </div>

        {/* Evidence Toggle */}
        {message.evidence && message.evidence.length > 0 && (
          <div className="px-5 pb-3">
            <button
              onClick={() => setShowEvidence(!showEvidence)}
              className="text-sm text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 font-medium flex items-center space-x-1"
            >
              <span>📚 {message.evidence.length} Sources</span>
              <span className="text-xs">{showEvidence ? '▲' : '▼'}</span>
            </button>
          </div>
        )}

        {/* Evidence Panel */}
        {showEvidence && message.evidence && (
          <EvidencePanel evidence={message.evidence} />
        )}
      </div>
    </div>
  );
}
