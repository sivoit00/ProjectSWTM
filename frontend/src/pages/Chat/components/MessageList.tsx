import MessageBubble from "./MessageBubble";
import EmptyState from "./EmptyState";
import type { Message } from "../hooks/chat/chatTypes";

interface MessageListProps {
  messages: Message[];
  loading: boolean;
}

export default function MessageList({ messages}: MessageListProps) {
  return (
    <div className="flex-1 p-6 space-y-4 overflow-y-auto bg-white dark:bg-gray-900">
      {messages.length === 0 && <EmptyState />}

      {messages.map((msg, i) => (
        <div key={i} id={msg.id} className="transition-all duration-300">
          <MessageBubble message={msg} />
        </div>
      ))}
    </div>
  );
}
