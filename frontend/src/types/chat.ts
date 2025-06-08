export interface Message {
  content: string;
  sender: 'user' | 'assistant';
  timestamp: string;
}

export interface ChatState {
  messages: Message[];
  isRecording: boolean;
  isLoading: boolean;
  error: string | null;
} 