/**
 * API Types - matching backend Pydantic models
 */

export enum ModelSize {
  TINY = "tiny",
  BASE = "base",
  SMALL = "small",
  MEDIUM = "medium",
  LARGE = "large",
}

export enum JobStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
}

export interface Word {
  word: string;
  start: number;
  end: number;
  confidence: number;
}

export interface TranscriptionSegment {
  id: number;
  text: string;
  start: number;
  end: number;
  confidence: number;
  speaker?: string;
  words?: Word[];
}

export interface TranscriptionResult {
  text: string;
  segments: TranscriptionSegment[];
  language: string;
  duration: number;
}

export interface JobResponse {
  job_id: string;
  status: JobStatus;
  progress: number;
  result?: TranscriptionResult;
  error?: string;
  created_at: string;
  completed_at?: string;
}

export interface JobCreateResponse {
  job_id: string;
  status: JobStatus;
  message: string;
}

export interface TranscriptionRequest {
  language?: string;
  model_size?: ModelSize;
  enable_diarization?: boolean;
  num_speakers?: number;
}

export interface HealthResponse {
  status: string;
  services: {
    transcription: string;
    diarization: string;
    translation: string;
  };
  version: string;
}

export interface ModelsResponse {
  whisper_models: string[];
  current_model: string;
  supported_languages: string[];
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: string;
  };
}
