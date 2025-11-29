/**
 * TranscriptionView Component - Display transcription results with speaker labels
 */
import React, { useState, useMemo } from "react";
import { save } from "@tauri-apps/api/dialog";
import { writeTextFile } from "@tauri-apps/api/fs";
import type { JobResponse } from "@/types/api";

interface TranscriptionViewProps {
  job: JobResponse;
}

// Speaker name mapping
type SpeakerNames = Record<string, string>;

export const TranscriptionView: React.FC<TranscriptionViewProps> = ({
  job,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSegmentId, setSelectedSegmentId] = useState<number | null>(null);
  const [speakerNames, setSpeakerNames] = useState<SpeakerNames>({});
  const [editingSpeaker, setEditingSpeaker] = useState<string | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);
  const [exportSuccess, setExportSuccess] = useState<string | null>(null);

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

  // Get unique speakers from segments
  const uniqueSpeakers = useMemo(() => {
    const speakers = new Set<string>();
    result.segments.forEach((seg) => {
      if (seg.speaker) {
        speakers.add(seg.speaker);
      }
    });
    return Array.from(speakers).sort();
  }, [result.segments]);

  // Get display name for a speaker
  const getSpeakerDisplayName = (speakerId: string | null | undefined): string => {
    if (!speakerId) return "";
    return speakerNames[speakerId] || speakerId;
  };

  // Filter segments by search query
  const filteredSegments = searchQuery
    ? result.segments.filter((seg) =>
        seg.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
        getSpeakerDisplayName(seg.speaker).toLowerCase().includes(searchQuery.toLowerCase())
      )
    : result.segments;

  // Format time in MM:SS format
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
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

  // Generate text content with speaker labels
  const generateTextContent = (): string => {
    if (uniqueSpeakers.length === 0) {
      return result.text;
    }
    
    // Format with speaker labels
    return result.segments
      .map((seg) => {
        const speaker = getSpeakerDisplayName(seg.speaker);
        const prefix = speaker ? `[${speaker}]: ` : "";
        return `${prefix}${seg.text}`;
      })
      .join("\n\n");
  };

  // Generate JSON content with speaker names
  const generateJsonContent = (): string => {
    const exportData = {
      ...result,
      speaker_names: speakerNames,
      segments: result.segments.map((seg) => ({
        ...seg,
        speaker_name: seg.speaker ? getSpeakerDisplayName(seg.speaker) : null,
      })),
    };
    return JSON.stringify(exportData, null, 2);
  };

  // Generate SRT content with speaker labels
  const generateSrtContent = (): string => {
    return result.segments
      .map((seg, idx) => {
        const startTime = formatSrtTime(seg.start);
        const endTime = formatSrtTime(seg.end);
        const speaker = getSpeakerDisplayName(seg.speaker);
        const prefix = speaker ? `[${speaker}] ` : "";
        return `${idx + 1}\n${startTime} --> ${endTime}\n${prefix}${seg.text}\n`;
      })
      .join("\n");
  };

  // Save file using Tauri's save dialog
  const saveFile = async (content: string, defaultName: string, filters: { name: string; extensions: string[] }[]) => {
    try {
      setExportError(null);
      setExportSuccess(null);
      
      const filePath = await save({
        defaultPath: defaultName,
        filters,
      });

      if (filePath) {
        await writeTextFile(filePath, content);
        setExportSuccess(`Saved to ${filePath}`);
        setTimeout(() => setExportSuccess(null), 3000);
      }
    } catch (err) {
      console.error("Export error:", err);
      setExportError(`Failed to save file: ${err}`);
      setTimeout(() => setExportError(null), 5000);
    }
  };

  // Export handlers
  const handleExportTxt = () => {
    const content = generateTextContent();
    saveFile(content, "transcription.txt", [{ name: "Text", extensions: ["txt"] }]);
  };

  const handleExportJson = () => {
    const content = generateJsonContent();
    saveFile(content, "transcription.json", [{ name: "JSON", extensions: ["json"] }]);
  };

  const handleExportSrt = () => {
    const content = generateSrtContent();
    saveFile(content, "transcription.srt", [{ name: "SubRip Subtitle", extensions: ["srt"] }]);
  };

  // Handle speaker name change
  const handleSpeakerNameChange = (speakerId: string, newName: string) => {
    setSpeakerNames((prev) => ({
      ...prev,
      [speakerId]: newName,
    }));
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      {/* Export Status Messages */}
      {exportSuccess && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800">{exportSuccess}</p>
        </div>
      )}
      {exportError && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{exportError}</p>
        </div>
      )}

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
            <span className="text-gray-500">Speakers:</span>
            <p className="font-medium">{uniqueSpeakers.length || "N/A"}</p>
          </div>
        </div>
      </div>

      {/* Speaker Names Editor (only show if diarization was enabled) */}
      {uniqueSpeakers.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Speaker Names
          </h3>
          <p className="text-sm text-gray-500 mb-4">
            Edit speaker names to personalize the transcription. Names will be used in exports.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {uniqueSpeakers.map((speakerId) => (
              <div key={speakerId} className="flex items-center gap-2">
                <span className="text-sm text-gray-500 w-20">{speakerId}:</span>
                {editingSpeaker === speakerId ? (
                  <input
                    type="text"
                    value={speakerNames[speakerId] || ""}
                    onChange={(e) => handleSpeakerNameChange(speakerId, e.target.value)}
                    onBlur={() => setEditingSpeaker(null)}
                    onKeyDown={(e) => e.key === "Enter" && setEditingSpeaker(null)}
                    autoFocus
                    placeholder={speakerId}
                    className="flex-1 px-2 py-1 text-sm border border-blue-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                ) : (
                  <button
                    onClick={() => setEditingSpeaker(speakerId)}
                    className="flex-1 px-2 py-1 text-sm text-left border border-gray-200 rounded hover:border-gray-300 hover:bg-gray-50"
                  >
                    {speakerNames[speakerId] || <span className="text-gray-400">Click to name...</span>}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Search and Export */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
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
            title="Export as plain text"
          >
            TXT
          </button>
          <button
            onClick={handleExportJson}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            title="Export as JSON with full metadata"
          >
            JSON
          </button>
          <button
            onClick={handleExportSrt}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            title="Export as SubRip subtitle file"
          >
            SRT
          </button>
        </div>
      </div>

      {/* Full Text View */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Full Text</h3>
        <div className="text-gray-700 leading-relaxed whitespace-pre-wrap max-h-64 overflow-y-auto">
          {uniqueSpeakers.length > 0 ? (
            // Show with speaker labels
            result.segments.map((seg, idx) => (
              <p key={idx} className="mb-2">
                {seg.speaker && (
                  <span className="font-semibold text-blue-600">
                    [{getSpeakerDisplayName(seg.speaker)}]:{" "}
                  </span>
                )}
                {seg.text}
              </p>
            ))
          ) : (
            <p>{result.text}</p>
          )}
        </div>
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
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-500">
                    {formatTime(segment.start)} - {formatTime(segment.end)}
                  </span>
                  {segment.speaker && (
                    <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">
                      {getSpeakerDisplayName(segment.speaker)}
                    </span>
                  )}
                </div>
                <span className="text-xs text-gray-400">
                  {(segment.confidence * 100).toFixed(0)}%
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
