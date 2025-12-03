export interface VoiceMessage {
  id: string;
  filePath: string;
  transcription: string;
  summary: string;
  createdAt: number;
  duration?: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

export type SummaryLength = 'short' | 'medium';

export interface AppSettings {
  summaryLength: SummaryLength;
  theme: 'light' | 'dark';
}
