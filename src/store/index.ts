import { create } from 'zustand';
import { VoiceMessage } from '../types';
import * as StorageService from '../services/storage';

interface AppState {
  history: VoiceMessage[];
  isLoading: boolean;
  loadHistory: () => Promise<void>;
  addMessage: (message: VoiceMessage) => Promise<void>;
  deleteMessage: (id: string) => Promise<void>;
  processAudio: (uri: string) => Promise<void>;
}

export const useStore = create<AppState>((set, get) => ({
  history: [],
  isLoading: false,
  loadHistory: async () => {
    const messages = await StorageService.getMessages();
    set({ history: messages });
  },
  addMessage: async (message) => {
    await StorageService.saveMessage(message);
    set((state) => ({ history: [message, ...state.history] }));
  },
  deleteMessage: async (id) => {
    await StorageService.deleteMessage(id);
    set((state) => ({ history: state.history.filter((m) => m.id !== id) }));
  },
  processAudio: async (uri) => {
    // Logic to be called from UI
  }
}));
