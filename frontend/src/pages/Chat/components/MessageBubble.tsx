import { FileText, Image as ImageIcon } from "lucide-react";
import { api } from "../../../services/api";
import type { Message } from "../hooks/chat/chatTypes";
import { getAgentColor } from "../../../components/common/timeline/timelineUtils";
import LoadingIndicator from "./LoadingIndicator";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.sender === "User";
  const agentColor = getAgentColor(message.agent);
  const isThinking = !isUser && !message.text;

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`px-4 py-3 rounded-2xl max-w-[70%] shadow-md ${
          isUser
            ? "bg-indigo-600 text-white rounded-br-none"
            : "text-gray-800 dark:text-gray-200 rounded-bl-none border"
        }`}
        style={
          isUser
            ? undefined
            : {
                backgroundColor: `${agentColor}15`,
                borderColor: `${agentColor}50`,
              }
        }
      >
        {isThinking ? (
           <LoadingIndicator />
        ) : (
           <p className="text-sm whitespace-pre-wrap leading-relaxed">
             {message.text}
           </p>
        )}
        
        {message.files && message.files.length > 0 && (
          <div className="mt-2 space-y-1">
            {message.files.map((filename, idx) => {
              const fileUrl = api.files.getFileUrl(filename);
              const isPdf = filename.toLowerCase().endsWith('.pdf');
              const isImage = /\.(jpg|jpeg|png|gif|bmp)$/i.test(filename);
              const isAudio = /\.(webm|wav|mp3|m4a|aac|ogg|mp4)$/i.test(filename);

              if (isAudio) {
                return null;
              }
              
              return (
                <a
                  key={idx}
                  href={fileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`flex items-center gap-2 p-2 rounded-lg text-xs ${
                    isUser
                      ? "bg-indigo-700 hover:bg-indigo-800"
                      : "bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600"
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