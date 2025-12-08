import { Send, Paperclip, X } from "lucide-react";
import FileUpload from "../../../components/common/FileUpload";

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  loading: boolean;
  showFileUpload: boolean;
  setShowFileUpload: (show: boolean) => void;
  selectedFiles: File[];
  setSelectedFiles: (files: File[]) => void;
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
  return (
    <div className="p-4 border-t border-gray-700 bg-gray-800">
      {showFileUpload && (
        <div className="mb-3 p-4 bg-gray-900 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-white">Upload Files</h3>
            <button
              onClick={() => {
                setShowFileUpload(false);
                setSelectedFiles([]);
              }}
              className="text-gray-400 hover:text-white"
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
              ? "bg-blue-600 text-white"
              : "bg-gray-700 text-gray-300 hover:bg-gray-600"
          }`}
        >
          <Paperclip size={20} />
        </button>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onSend()}
          placeholder="Type your message..."
          disabled={loading}
          className="flex-1 px-4 py-3 text-white placeholder-gray-400 rounded-xl border border-gray-600 bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        />
        <button
          onClick={onSend}
          disabled={loading || (!input.trim() && selectedFiles.length === 0)}
          className="p-3 bg-blue-600 rounded-xl shadow-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
}
