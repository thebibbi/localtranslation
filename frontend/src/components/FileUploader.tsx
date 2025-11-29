/**
 * FileUploader Component - Drag and drop or browse file selection
 */
import React, { useState, useRef } from "react";
import { open } from "@tauri-apps/api/dialog";
import type { ModelSize } from "@/types/api";

interface FileUploaderProps {
  onFileSelect: (file: File, options: TranscriptionOptions) => void;
  onFilePathSelect?: (filePath: string, fileName: string, mimeType: string, options: TranscriptionOptions) => void;
  isProcessing: boolean;
}

interface TranscriptionOptions {
  language?: string;
  modelSize: ModelSize;
  enableDiarization: boolean;
  numSpeakers?: number;
}

const SUPPORTED_FORMATS = [
  ".wav",
  ".mp3",
  ".m4a",
  ".flac",
  ".ogg",
  ".mp4",
  ".mov",
  ".avi",
];
const MAX_FILE_SIZE_MB = 500;

// Store selected file info - either a File object (drag/drop) or path info (Tauri dialog)
interface SelectedFileInfo {
  type: "file" | "path";
  file?: File;
  path?: string;
  fileName: string;
  mimeType: string;
}

export const FileUploader: React.FC<FileUploaderProps> = ({
  onFileSelect,
  onFilePathSelect,
  isProcessing,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFileInfo, setSelectedFileInfo] = useState<SelectedFileInfo | null>(null);
  const [modelSize, setModelSize] = useState<ModelSize>("base" as ModelSize);
  const [language, setLanguage] = useState<string>("");
  const [enableDiarization, setEnableDiarization] = useState(false);
  const [numSpeakers, setNumSpeakers] = useState<string>("");
  const [error, setError] = useState<string>("");

  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFileName = (fileName: string): boolean => {
    const ext = `.${fileName.split(".").pop()?.toLowerCase()}`;
    if (!SUPPORTED_FORMATS.includes(ext)) {
      setError(`Unsupported format. Supported: ${SUPPORTED_FORMATS.join(", ")}`);
      return false;
    }
    setError("");
    return true;
  };

  const validateFile = (file: File): boolean => {
    if (!validateFileName(file.name)) return false;

    // Check file size
    const sizeMB = file.size / (1024 * 1024);
    if (sizeMB > MAX_FILE_SIZE_MB) {
      setError(`File too large (${sizeMB.toFixed(1)}MB). Max: ${MAX_FILE_SIZE_MB}MB`);
      return false;
    }

    setError("");
    return true;
  };

  const handleFileChange = (file: File) => {
    if (validateFile(file)) {
      setSelectedFileInfo({
        type: "file",
        file,
        fileName: file.name,
        mimeType: file.type || "audio/mpeg",
      });
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileChange(files[0]);
    }
  };

  const getMimeType = (ext: string): string => {
    const mimeTypes: Record<string, string> = {
      mp3: "audio/mpeg",
      wav: "audio/wav",
      m4a: "audio/mp4",
      flac: "audio/flac",
      ogg: "audio/ogg",
      mp4: "video/mp4",
      mov: "video/quicktime",
      avi: "video/x-msvideo",
    };
    return mimeTypes[ext] || "audio/mpeg";
  };

  const handleBrowseClick = async () => {
    try {
      const selected = await open({
        multiple: false,
        filters: [
          {
            name: "Audio/Video",
            extensions: SUPPORTED_FORMATS.map((f) => f.replace(".", "")),
          },
        ],
      });

      if (selected && typeof selected === "string") {
        const fileName = selected.split("/").pop() || "audio";
        const ext = fileName.split(".").pop()?.toLowerCase() || "mp3";
        const mimeType = getMimeType(ext);

        if (validateFileName(fileName)) {
          // Store the path - we'll read the file when submitting
          setSelectedFileInfo({
            type: "path",
            path: selected,
            fileName,
            mimeType,
          });
          setError("");
        }
      }
    } catch (err) {
      console.error("File dialog error:", err);
      setError("Failed to open file dialog");
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFileInfo) {
      setError("Please select a file");
      return;
    }

    const options: TranscriptionOptions = {
      modelSize,
      language: language || undefined,
      enableDiarization,
      numSpeakers: numSpeakers ? parseInt(numSpeakers, 10) : undefined,
    };

    if (selectedFileInfo.type === "file" && selectedFileInfo.file) {
      // Drag and drop - use File object
      onFileSelect(selectedFileInfo.file, options);
    } else if (selectedFileInfo.type === "path" && selectedFileInfo.path && onFilePathSelect) {
      // Tauri dialog - use path-based upload
      onFilePathSelect(selectedFileInfo.path, selectedFileInfo.fileName, selectedFileInfo.mimeType, options);
    } else if (selectedFileInfo.type === "path" && selectedFileInfo.path) {
      // Fallback: if no path handler, show error
      setError("Path-based upload not supported. Please use drag and drop.");
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Drag and Drop Area */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
            transition-colors duration-200
            ${isDragging ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"}
            ${isProcessing ? "opacity-50 cursor-not-allowed" : ""}
          `}
          onClick={!isProcessing ? handleBrowseClick : undefined}
        >
          <div className="space-y-4">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div>
              {selectedFileInfo ? (
                <p className="text-sm text-gray-700 font-medium">{selectedFileInfo.fileName}</p>
              ) : (
                <>
                  <p className="text-base text-gray-700">
                    Drop audio file here or click to browse
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    Supported: {SUPPORTED_FORMATS.join(", ")} (max {MAX_FILE_SIZE_MB}MB)
                  </p>
                </>
              )}
            </div>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept={SUPPORTED_FORMATS.join(",")}
            onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
            disabled={isProcessing}
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Options */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Model Size
            </label>
            <select
              value={modelSize}
              onChange={(e) => setModelSize(e.target.value as ModelSize)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isProcessing}
            >
              <option value="tiny">Tiny (fastest, lowest quality)</option>
              <option value="base">Base (recommended)</option>
              <option value="small">Small (better quality)</option>
              <option value="medium">Medium (high quality)</option>
              <option value="large">Large (best quality, slowest)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Language (optional)
            </label>
            <input
              type="text"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              placeholder="e.g., en, es, fr (auto-detect if empty)"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isProcessing}
            />
          </div>

          {/* Diarization Options */}
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center justify-between mb-4">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Speaker Diarization
                </label>
                <p className="text-xs text-gray-500">
                  Identify and label different speakers in the audio
                </p>
              </div>
              <button
                type="button"
                onClick={() => setEnableDiarization(!enableDiarization)}
                disabled={isProcessing}
                className={`
                  relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                  ${enableDiarization ? "bg-blue-600" : "bg-gray-200"}
                  ${isProcessing ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
                `}
              >
                <span
                  className={`
                    inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                    ${enableDiarization ? "translate-x-6" : "translate-x-1"}
                  `}
                />
              </button>
            </div>

            {enableDiarization && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Speakers (optional)
                </label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={numSpeakers}
                  onChange={(e) => setNumSpeakers(e.target.value)}
                  placeholder="Auto-detect if empty"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isProcessing}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Leave empty to auto-detect the number of speakers
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!selectedFileInfo || isProcessing}
          className={`
            w-full py-3 px-4 rounded-lg font-medium text-white
            transition-colors duration-200
            ${
              !selectedFileInfo || isProcessing
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700"
            }
          `}
        >
          {isProcessing ? "Processing..." : "Transcribe Audio"}
        </button>
      </form>
    </div>
  );
};
