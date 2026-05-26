export interface Evidence {
  reference: string;
  text: string;
  source_type: 'quran' | 'bukhari' | 'muslim' | 'tafsir';
  score: number;
  metadata?: {
    surah?: number;
    verse?: number;
    verse_key?: string;
    translation?: string;
    tafsir_name?: string;
    book?: number;
    hadith_number?: number;
  };
}

export interface QueryResponse {
  question: string;
  answer: string;
  evidence: Evidence[];
  confidence: number;
  retrieved_count: number;
}

export interface Message {
  id: string;
  type: 'user' | 'assistant' | 'error';
  content: string;
  confidence?: number;
  evidence?: Evidence[];
  timestamp: Date;
}
