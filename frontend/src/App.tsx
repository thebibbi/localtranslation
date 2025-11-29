/**
 * Main App Component
 */
import { useState, useEffect } from "react";
import { FileUploader } from "./components/FileUploader";
import { TranscriptionView } from "./components/TranscriptionView";
import { useTranscriptionStore } from "./stores/transcription";
import { transcribeFile, transcribeFileFromPath, pollJobStatus, checkHealth } from "./services/transcription";
import type { ModelSize } from "./types/api";

interface TranscriptionOptions {
  language?: string;
  modelSize: ModelSize;
  enableDiarization: boolean;
  numSpeakers?: number;
}

function App() {
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">(
    "checking"
  );

  const {
    currentJob,
    isProcessing,
    error,
    setCurrentJob,
    setIsProcessing,
    setError,
    addToHistory,
    clearError,
  } = useTranscriptionStore();

  // Check backend health on mount
  useEffect(() => {
    const checkBackend = async () => {
      const isHealthy = await checkHealth();
      setBackendStatus(isHealthy ? "online" : "offline");
    };

    checkBackend();

    // Check every 30 seconds
    const interval = setInterval(checkBackend, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleFileSelect = async (
    file: File,
    options: TranscriptionOptions
  ) => {
    try {
      clearError();
      setIsProcessing(true);

      console.log("Transcribing file:", file.name, "with options:", options);

      // Upload and start transcription
      const jobCreateResponse = await transcribeFile(file, {
        language: options.language,
        model_size: options.modelSize,
        enable_diarization: options.enableDiarization,
        num_speakers: options.numSpeakers,
      });

      console.log("Job created:", jobCreateResponse.job_id);

      // Poll for job completion
      const completedJob = await pollJobStatus(
        jobCreateResponse.job_id,
        (job) => {
          console.log("Job progress:", job.progress, "%");
          setCurrentJob(job);
        }
      );

      console.log("Job completed:", completedJob);

      // Update state with completed job
      setCurrentJob(completedJob);
      addToHistory(completedJob);
      setIsProcessing(false);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "An unexpected error occurred";
      console.error("Transcription error:", errorMessage);
      setError(errorMessage);
      setIsProcessing(false);
    }
  };

  const handleFilePathSelect = async (
    filePath: string,
    fileName: string,
    mimeType: string,
    options: TranscriptionOptions
  ) => {
    try {
      clearError();
      setIsProcessing(true);

      console.log("Transcribing file from path:", filePath, "with options:", options);

      // Upload and start transcription using path-based method
      const jobCreateResponse = await transcribeFileFromPath(filePath, fileName, mimeType, {
        language: options.language,
        model_size: options.modelSize,
        enable_diarization: options.enableDiarization,
        num_speakers: options.numSpeakers,
      });

      console.log("Job created:", jobCreateResponse.job_id);

      // Poll for job completion
      const completedJob = await pollJobStatus(
        jobCreateResponse.job_id,
        (job) => {
          console.log("Job progress:", job.progress, "%");
          setCurrentJob(job);
        }
      );

      console.log("Job completed:", completedJob);

      // Update state with completed job
      setCurrentJob(completedJob);
      addToHistory(completedJob);
      setIsProcessing(false);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "An unexpected error occurred";
      console.error("Transcription error:", errorMessage);
      setError(errorMessage);
      setIsProcessing(false);
    }
  };

  const handleNewTranscription = () => {
    setCurrentJob(null);
    clearError();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Speech Processing
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Transcribe audio files with AI
              </p>
            </div>

            {/* Backend Status Indicator */}
            <div className="flex items-center gap-2">
              <div
                className={`
                  w-2 h-2 rounded-full
                  ${backendStatus === "online" ? "bg-green-500" : ""}
                  ${backendStatus === "offline" ? "bg-red-500" : ""}
                  ${backendStatus === "checking" ? "bg-yellow-500 animate-pulse" : ""}
                `}
              />
              <span className="text-sm text-gray-600">
                {backendStatus === "online" && "Backend Online"}
                {backendStatus === "offline" && "Backend Offline"}
                {backendStatus === "checking" && "Checking..."}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Backend Offline Warning */}
        {backendStatus === "offline" && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="text-sm font-medium text-red-800 mb-1">
              Backend Server Offline
            </h3>
            <p className="text-sm text-red-600">
              Unable to connect to the backend server. Please ensure it is running
              at{" "}
              <code className="bg-red-100 px-1 py-0.5 rounded">
                {import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}
              </code>
            </p>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-sm font-medium text-red-800 mb-1">Error</h3>
                <p className="text-sm text-red-600">{error}</p>
              </div>
              <button
                onClick={clearError}
                className="text-red-400 hover:text-red-600"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Processing Status */}
        {isProcessing && currentJob && (
          <div className="mb-6 p-6 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="text-lg font-medium text-blue-900 mb-2">
              Processing Transcription...
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-blue-700">
                <span>Job ID: {currentJob.job_id}</span>
                <span>{currentJob.progress}%</span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${currentJob.progress}%` }}
                />
              </div>
              <p className="text-sm text-blue-600">
                Status: {currentJob.status}
              </p>
            </div>
          </div>
        )}

        {/* Main View */}
        {!currentJob || currentJob.status !== "completed" ? (
          <FileUploader
            onFileSelect={handleFileSelect}
            onFilePathSelect={handleFilePathSelect}
            isProcessing={isProcessing}
          />
        ) : (
          <div>
            <div className="mb-6 flex justify-end">
              <button
                onClick={handleNewTranscription}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                New Transcription
              </button>
            </div>
            <TranscriptionView job={currentJob} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            Speech Processing v0.1.0 - Powered by Whisper AI
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
