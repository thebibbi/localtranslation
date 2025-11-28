/**
 * API Client for Speech Processing Backend
 */
import axios, { AxiosInstance, AxiosError } from "axios";
import type { ApiError } from "@/types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_V1_PREFIX = "/api/v1";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}${API_V1_PREFIX}`,
      timeout: 300000, // 5 minutes for long transcriptions
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiError>) => {
        if (error.response?.data?.error) {
          // Backend returned structured error
          const apiError = error.response.data.error;
          throw new Error(`${apiError.code}: ${apiError.message}`);
        } else if (error.message === "Network Error") {
          throw new Error(
            "Unable to connect to backend server. Please ensure the backend is running."
          );
        } else {
          throw new Error(error.message || "An unexpected error occurred");
        }
      }
    );
  }

  getClient(): AxiosInstance {
    return this.client;
  }

  getBaseUrl(): string {
    return API_BASE_URL;
  }
}

// Singleton instance
export const apiClient = new ApiClient();
export default apiClient.getClient();
