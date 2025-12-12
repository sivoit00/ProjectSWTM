import { FileText, Image as ImageIcon } from "lucide-react";
import { api } from "../../../services/api";
import type { Message } from "../hooks/useChatState";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.sender === "User";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`px-4 py-3 rounded-2xl max-w-[70%] shadow-md ${
          isUser
            ? "bg-blue-600 text-white rounded-br-none"
            : "bg-gray-800 text-gray-200 rounded-bl-none border border-gray-700"
        }`}
      >
        <p className="text-sm whitespace-pre-wrap">{message.text}</p>
        
        {message.files && message.files.length > 0 && (
          <div className="mt-2 space-y-1">
            {message.files.map((filename, idx) => {
              const fileUrl = api.files.getFileUrl(filename);
              const isPdf = filename.toLowerCase().endsWith('.pdf');
              const isImage = /\.(jpg|jpeg|png|gif|bmp)$/i.test(filename);
              
              return (
                <a
                  key={idx}
                  href={fileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`flex items-center gap-2 p-2 rounded-lg text-xs ${
                    isUser
                      ? "bg-blue-700 hover:bg-blue-800"
                      : "bg-gray-700 hover:bg-gray-600"
                  }`}
                >
                  {isPdf && <FileText size={16} />}
                  {isImage && <ImageIcon size={16} />}
                  <span className="truncate">{filename}</span>
                </a>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}