import { Send, Paperclip, X } from "lucide-react";
import FileUpload from "../../../components/common/FileUpload";
import VoiceRecorder from "./VoiceRecorder";
import { useEffect, useRef } from "react";
import type { Dispatch, SetStateAction } from "react";

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  loading: boolean;
  showFileUpload: boolean;
  setShowFileUpload: (show: boolean) => void;
  selectedFiles: File[];
  setSelectedFiles: Dispatch<SetStateAction<File[]>>;
  onSend: () => void;
}

export default function ChatInput({
  input,
  setInput,
  loading,
  showFileUpload,
  setShowFileUpload,
  selectedFiles,
  setSelectedFiles,
  onSend,
}: ChatInputProps) {
  const voicePrefixRef = useRef<string>("");
  const voiceRecordingRef = useRef(false);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    // Auto-resize to keep the message visible
    el.style.height = "0px";
    el.style.height = `${el.scrollHeight}px`;
  }, [input]);

  return (
    <div className="p-4 border-t border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-950">
      {showFileUpload && (
        <div className="mb-3 p-4 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Upload Files</h3>
            <button
              onClick={() => {
                setShowFileUpload(false);
                setSelectedFiles([]);
              }}
              className="text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
            >
              <X size={18} />
            </button>
          </div>
          <FileUpload onFilesSelected={setSelectedFiles} />
        </div>
      )}

      <div className="flex items-center gap-3">
        <button
          onClick={() => setShowFileUpload(!showFileUpload)}
          className={`p-3 rounded-xl transition-colors ${
            showFileUpload
              ? "bg-indigo-600 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
          }`}
        >
          <Paperclip size={20} />
        </button>

        <VoiceRecorder
          disabled={loading}
          onRecordingChange={(isRec) => {
            voiceRecordingRef.current = isRec;
            if (isRec) {
              voicePrefixRef.current = input ? `${input.trim()} ` : "";
            }
          }}
          onTranscript={(text) => {
            // Live-update input while recording
            if (!voiceRecordingRef.current) return;
            setInput(`${voicePrefixRef.current}${text}`.trimStart());
          }}
          onRecorded={(file) => {
            // Voice recordings are NOT added to files - only transcription is used
            // Only non-audio files (PDFs, images) should be added to selectedFiles
            const isAudio = /\.(webm|wav|mp3|m4a|aac|ogg|mp4)$/i.test(file.name);
            
            if (!isAudio) {
              setSelectedFiles((prev) => [...prev, file].slice(0, 5));
            }
            // Audio files are discarded after transcription
          }}
        />

        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
          rows={1}
          placeholder="Type your message..."
          disabled={loading}
          className="flex-1 px-4 py-3 text-gray-900 placeholder-gray-500 rounded-xl border border-gray-300 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 resize-none overflow-hidden dark:text-gray-100 dark:placeholder-gray-400 dark:border-gray-700 dark:bg-gray-900"
        />
        <button
          onClick={() => onSend()}
          disabled={loading || (!input.trim() && selectedFiles.length === 0)}
          className="p-3 bg-indigo-600 rounded-xl shadow-md hover:bg-indigo-700 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
}