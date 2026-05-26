'use client';

import { useState, useRef, useEffect } from 'react';
import { Message, QueryResponse } from '@/types';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import Header from '@/components/Header';

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setDarkMode(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    if (!darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  const handleSendMessage = async (question: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: question,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          top_k: 15,
          max_tokens: 500,
          temperature: 0.3,
        }),
      });

      if (!response.ok) throw new Error('Failed to get response');

      const data: QueryResponse = await response.json();

      // Add assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.answer,
        confidence: data.confidence,
        evidence: data.evidence,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'error',
        content: 'Failed to get response. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => {
    setMessages([]);
  };

  return (
    <div className={`min-h-screen flex flex-col ${darkMode ? 'dark' : ''}`}>
      <div className="flex-1 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 transition-colors">
        <Header
          darkMode={darkMode}
          toggleDarkMode={toggleDarkMode}
          onClearHistory={clearHistory}
          messageCount={messages.length}
        />

        <main className="container mx-auto px-4 pb-32 pt-24 max-w-4xl">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-[60vh] text-center">
              <div className="text-6xl mb-6">🌙</div>
              <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-emerald-600 to-teal-600 dark:from-emerald-400 dark:to-teal-400 bg-clip-text text-transparent">
                Basirah
              </h1>
              <p className="text-xl text-slate-600 dark:text-slate-400 mb-8">
                Islamic Knowledge Assistant
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-500 max-w-md">
                Ask questions about the Quran and authentic Hadith. All answers are grounded in retrieved evidence with citations.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {loading && (
                <div className="flex items-center space-x-2 text-slate-500 dark:text-slate-400">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-emerald-600"></div>
                  <span>Searching sources and generating answer...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </main>

        <ChatInput onSend={handleSendMessage} disabled={loading} />
      </div>
    </div>
  );
}
