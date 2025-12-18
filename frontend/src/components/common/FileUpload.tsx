import { useState } from "react";
import { api } from "../../services/api";
import { Upload, X, FileText, Image as ImageIcon } from "lucide-react";

interface FileUploadProps {
  onFilesSelected: (files: File[]) => void;
  maxFiles?: number;
  maxSizeMB?: number;
}

export default function FileUpload({ 
  onFilesSelected, 
  maxFiles = 5, 
  maxSizeMB = 10 
}: FileUploadProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string>("");

  const allowedTypes = ["image/jpeg", "image/png", "image/gif", "image/bmp", "application/pdf", "text/plain"];

  const validateFile = (file: File): boolean => {
    // Check size
    const maxSize = maxSizeMB * 1024 * 1024;
    if (file.size > maxSize) {
      setError(`File too large: ${file.name} (max ${maxSizeMB}MB)`);
      return false;
    }

    // Check type
    if (!allowedTypes.includes(file.type)) {
      setError(`File type not supported: ${file.name}`);
      return false;
    }

    return true;
  };

  const handleFiles = (files: FileList | null) => {
    if (!files) return;
    
    setError("");
    const fileArray = Array.from(files);

    // Check total number
    if (selectedFiles.length + fileArray.length > maxFiles) {
      setError(`Maximum ${maxFiles} files allowed`);
      return;
    }

    // Validate each file
    const validFiles = fileArray.filter(validateFile);
    
    if (validFiles.length > 0) {
      const newFiles = [...selectedFiles, ...validFiles];
      setSelectedFiles(newFiles);
      onFilesSelected(newFiles);
    }
    api.files.upload(validFiles)
        .then((res) => {
          const uploaded = (res.data?.files ?? []) as Array<{ stored_filename: string; filename: string }>;
          if (uploaded.length > 0) {
            const fileRefs = uploaded.map(f => `${f.stored_filename}`).join(", ");
            const message = `Dateien hochgeladen: ${fileRefs}`;
            // Persist chat message and notify orchestrator
            const userId = typeof window !== 'undefined' ? (localStorage.getItem('sessionId') || 'anonymous') : 'anonymous';
            api.chat.saveMessage({ user_id: userId, sender: 'user', message })
              .catch(() => {/* non-blocking */});

          }
        })
        .catch((err) => {
          console.error('Upload failed', err);
          setError('Upload failed. Bitte erneut versuchen.');
        });
  };

  const removeFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);
    onFilesSelected(newFiles);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  return (
    <div className="w-full">
      {/* Drag & Drop Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? "border-blue-500 bg-blue-500/10"
            : "border-gray-600 bg-gray-800/50"
        }`}
      >
        <Upload className="mx-auto mb-4 text-gray-400" size={48} />
        <p className="text-gray-300 mb-2">
          Drag and drop files here, or click to browse
        </p>
        <p className="text-sm text-gray-500 mb-4">
          PDF, JPG, PNG, GIF, BMP (max {maxSizeMB}MB per file)
        </p>
        <input
          type="file"
          multiple
          accept=".pdf,.jpg,.jpeg,.png,.gif,.bmp"
          onChange={handleFileInput}
          className="hidden"
          id="file-input"
        />
        <label
          htmlFor="file-input"
          className="inline-block px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg cursor-pointer transition"
        >
          Browse Files
        </label>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-3 p-3 bg-red-500/20 border border-red-500 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}

      {/* Selected Files List */}
      {selectedFiles.length > 0 && (
        <div className="mt-4 space-y-2">
          <p className="text-sm text-gray-400">
            Selected files ({selectedFiles.length}/{maxFiles}):
          </p>
          {selectedFiles.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-gray-800 rounded-lg border border-gray-700"
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                {file.type.startsWith("image/") ? (
                  <ImageIcon className="text-blue-400 flex-shrink-0" size={20} />
                ) : (
                  <FileText className="text-red-400 flex-shrink-0" size={20} />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white truncate">{file.name}</p>
                  <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                </div>
              </div>
              <button
                onClick={() => removeFile(index)}
                className="ml-3 p-1 hover:bg-gray-700 rounded transition flex-shrink-0"
              >
                <X size={18} className="text-gray-400" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
