/**
 * Transcription Store - State management for transcription operations
 */
import { create } from "zustand";
import type { JobResponse } from "@/types/api";

interface TranscriptionState {
  // Current job
  currentJob: JobResponse | null;
  isProcessing: boolean;
  error: string | null;

  // Results history
  history: JobResponse[];

  // Actions
  setCurrentJob: (job: JobResponse | null) => void;
  setIsProcessing: (processing: boolean) => void;
  setError: (error: string | null) => void;
  addToHistory: (job: JobResponse) => void;
  clearError: () => void;
  reset: () => void;
}

export const useTranscriptionStore = create<TranscriptionState>((set) => ({
  // Initial state
  currentJob: null,
  isProcessing: false,
  error: null,
  history: [],

  // Actions
  setCurrentJob: (job) => set({ currentJob: job }),

  setIsProcessing: (processing) => set({ isProcessing: processing }),

  setError: (error) => set({ error }),

  addToHistory: (job) =>
    set((state) => ({
      history: [job, ...state.history.slice(0, 49)], // Keep last 50 jobs
    })),

  clearError: () => set({ error: null }),

  reset: () =>
    set({
      currentJob: null,
      isProcessing: false,
      error: null,
    }),
}));
