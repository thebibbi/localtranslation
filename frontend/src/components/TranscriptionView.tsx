/**
 * TranscriptionView Component - Display transcription results
 */
import React, { useState } from "react";
import type { JobResponse, TranscriptionSegment } from "@/types/api";

interface TranscriptionViewProps {
  job: JobResponse;
  onExport?: (format: "txt" | "json" | "srt") => void;
}

export const TranscriptionView: React.FC<TranscriptionViewProps> = ({
  job,
  onExport,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSegmentId, setSelectedSegmentId] = useState<number | null>(null);

  if (!job.result) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">No transcription result available</p>
        </div>
      </div>
    );
  }

  const { result } = job;

  // Filter segments by search query
  const filteredSegments = searchQuery
    ? result.segments.filter((seg) =>
        seg.text.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : result.segments;

  // Format time in MM:SS format
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  // Export handlers
  const handleExportTxt = () => {
    const blob = new Blob([result.text], { type: "text/plain" });
    downloadBlob(blob, "transcription.txt");
  };

  const handleExportJson = () => {
    const blob = new Blob([JSON.stringify(result, null, 2)], {
      type: "application/json",
    });
    downloadBlob(blob, "transcription.json");
  };

  const handleExportSrt = () => {
    const srt = result.segments
      .map((seg, idx) => {
        const startTime = formatSrtTime(seg.start);
        const endTime = formatSrtTime(seg.end);
        return `${idx + 1}\n${startTime} --> ${endTime}\n${seg.text}\n`;
      })
      .join("\n");

    const blob = new Blob([srt], { type: "text/plain" });
    downloadBlob(blob, "transcription.srt");
  };

  const formatSrtTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 1000);
    return `${hours.toString().padStart(2, "0")}:${mins
      .toString()
      .padStart(2, "0")}:${secs.toString().padStart(2, "0")},${ms
      .toString()
      .padStart(3, "0")}`;
  };

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      {/* Header with metadata */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Transcription Result
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Language:</span>
            <p className="font-medium">{result.language.toUpperCase()}</p>
          </div>
          <div>
            <span className="text-gray-500">Duration:</span>
            <p className="font-medium">{formatTime(result.duration)}</p>
          </div>
          <div>
            <span className="text-gray-500">Segments:</span>
            <p className="font-medium">{result.segments.length}</p>
          </div>
          <div>
            <span className="text-gray-500">Status:</span>
            <p className="font-medium text-green-600">Completed</p>
          </div>
        </div>
      </div>

      {/* Search and Export */}
      <div className="flex gap-4 mb-6">
        <input
          type="text"
          placeholder="Search transcription..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <div className="flex gap-2">
          <button
            onClick={handleExportTxt}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            TXT
          </button>
          <button
            onClick={handleExportJson}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            JSON
          </button>
          <button
            onClick={handleExportSrt}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            SRT
          </button>
        </div>
      </div>

      {/* Full Text View */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Full Text</h3>
        <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
          {result.text}
        </p>
      </div>

      {/* Segments List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Segments ({filteredSegments.length})
        </h3>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {filteredSegments.map((segment) => (
            <div
              key={segment.id}
              onClick={() => setSelectedSegmentId(segment.id)}
              className={`
                p-4 rounded-lg border cursor-pointer transition-all
                ${
                  selectedSegmentId === segment.id
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300"
                }
              `}
            >
              <div className="flex items-start justify-between mb-2">
                <span className="text-sm font-medium text-gray-500">
                  {formatTime(segment.start)} - {formatTime(segment.end)}
                </span>
                <span className="text-xs text-gray-400">
                  Confidence: {(segment.confidence * 100).toFixed(1)}%
                </span>
              </div>
              <p className="text-gray-900">{segment.text}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
