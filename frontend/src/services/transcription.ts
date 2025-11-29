/**
 * Transcription Service - API calls for transcription operations
 */
import { getClient, Body } from "@tauri-apps/api/http";
import { readBinaryFile } from "@tauri-apps/api/fs";
import api from "./api";
import type {
  JobCreateResponse,
  JobResponse,
  TranscriptionRequest,
  ModelsResponse,
} from "@/types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Upload and transcribe an audio file using Tauri's HTTP client
 * This properly handles multipart form data in Tauri
 */
export async function transcribeFile(
  file: File,
  options: TranscriptionRequest = {}
): Promise<JobCreateResponse> {
  const client = await getClient();
  
  // Read file content as Uint8Array
  const fileBuffer = await file.arrayBuffer();
  const fileData = new Uint8Array(fileBuffer);
  
  // Build form data using Tauri's Body.form with proper file part
  // According to Tauri docs, file can be a path string OR an array buffer
  // The fileName is REQUIRED for Tauri's multipart to work correctly
  const formData = new FormData();
  formData.append("file", new Blob([fileData], { type: file.type || "audio/mpeg" }), file.name);
  
  // Add optional parameters as form fields
  if (options.language) {
    formData.append("language", options.language);
  }
  formData.append("model_size", options.model_size || "base");
  formData.append("enable_diarization", String(options.enable_diarization ?? false));
  if (options.num_speakers) {
    formData.append("num_speakers", String(options.num_speakers));
  }

  const response = await client.post<JobCreateResponse | { error: { code: string; message: string } }>(
    `${API_BASE_URL}/api/v1/transcribe/file`,
    Body.form(formData),
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  // Check for error response
  if (!response.ok) {
    const errorData = response.data as { error?: { code: string; message: string } };
    if (errorData?.error) {
      throw new Error(`${errorData.error.code}: ${errorData.error.message}`);
    }
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.data as JobCreateResponse;
}

/**
 * Alternative: Upload file from path (for Tauri file dialog)
 * This reads the file directly from disk using the path
 */
export async function transcribeFileFromPath(
  filePath: string,
  fileName: string,
  mimeType: string,
  options: TranscriptionRequest = {}
): Promise<JobCreateResponse> {
  const client = await getClient();
  
  // Read file content from disk
  const fileData = await readBinaryFile(filePath);
  
  // Build FormData with the file
  const formData = new FormData();
  formData.append("file", new Blob([fileData.buffer as ArrayBuffer], { type: mimeType }), fileName);
  
  if (options.language) {
    formData.append("language", options.language);
  }
  formData.append("model_size", options.model_size || "base");
  formData.append("enable_diarization", String(options.enable_diarization ?? false));
  if (options.num_speakers) {
    formData.append("num_speakers", String(options.num_speakers));
  }

  const response = await client.post<JobCreateResponse | { error: { code: string; message: string } }>(
    `${API_BASE_URL}/api/v1/transcribe/file`,
    Body.form(formData),
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  if (!response.ok) {
    const errorData = response.data as { error?: { code: string; message: string } };
    if (errorData?.error) {
      throw new Error(`${errorData.error.code}: ${errorData.error.message}`);
    }
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.data as JobCreateResponse;
}

/**
 * Get job status and result
 */
export async function getJobStatus(jobId: string): Promise<JobResponse> {
  const response = await api.get<JobResponse>(`/transcribe/job/${jobId}`);
  return response.data;
}

/**
 * Poll job status until completion or failure
 */
export async function pollJobStatus(
  jobId: string,
  onProgress?: (job: JobResponse) => void,
  pollInterval: number = 2000
): Promise<JobResponse> {
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const job = await getJobStatus(jobId);

        // Call progress callback if provided
        if (onProgress) {
          onProgress(job);
        }

        // Check if job is complete
        if (job.status === "completed") {
          resolve(job);
        } else if (job.status === "failed") {
          reject(new Error(job.error || "Job failed"));
        } else {
          // Continue polling
          setTimeout(poll, pollInterval);
        }
      } catch (error) {
        reject(error);
      }
    };

    // Start polling
    poll();
  });
}

/**
 * Get available models and languages
 */
export async function getAvailableModels(): Promise<ModelsResponse> {
  const response = await api.get<ModelsResponse>("/models");
  return response.data;
}

/**
 * Check API health
 */
export async function checkHealth(): Promise<boolean> {
  try {
    await api.get("/health");
    return true;
  } catch {
    return false;
  }
}
