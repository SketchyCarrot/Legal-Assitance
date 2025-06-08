import create from 'zustand';
import { Message, ChatState } from '../types/chat';

interface ChatStore extends ChatState {
  addMessage: (message: Message) => void;
  setIsRecording: (isRecording: boolean) => void;
  setIsLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  clearMessages: () => void;
}

const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  isRecording: false,
  isLoading: false,
  error: null,
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),
  setIsRecording: (isRecording) =>
    set(() => ({
      isRecording,
    })),
  setIsLoading: (isLoading) =>
    set(() => ({
      isLoading,
    })),
  setError: (error) =>
    set(() => ({
      error,
    })),
  clearMessages: () =>
    set(() => ({
      messages: [],
    })),
}));

export default useChatStore; 