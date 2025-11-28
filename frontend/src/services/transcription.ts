/**
 * Transcription Service - API calls for transcription operations
 */
import api from "./api";
import type {
  JobCreateResponse,
  JobResponse,
  TranscriptionRequest,
  ModelsResponse,
} from "@/types/api";

/**
 * Upload and transcribe an audio file
 */
export async function transcribeFile(
  file: File,
  options: TranscriptionRequest = {}
): Promise<JobCreateResponse> {
  const formData = new FormData();
  formData.append("file", file);

  if (options.language) {
    formData.append("language", options.language);
  }
  if (options.model_size) {
    formData.append("model_size", options.model_size);
  }
  if (options.enable_diarization !== undefined) {
    formData.append("enable_diarization", String(options.enable_diarization));
  }
  if (options.num_speakers) {
    formData.append("num_speakers", String(options.num_speakers));
  }

  const response = await api.post<JobCreateResponse>(
    "/transcribe/file",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
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
