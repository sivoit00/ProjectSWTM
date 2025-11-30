import MessageBubble from "./MessageBubble";
import EmptyState from "./EmptyState";
import LoadingIndicator from "./LoadingIndicator";
import type { Message } from "../hooks/useChatState";

interface MessageListProps {
  messages: Message[];
  loading: boolean;
}

export default function MessageList({ messages, loading }: MessageListProps) {
  return (
    <div className="flex-1 p-6 space-y-4 overflow-y-auto bg-gray-900">
      {messages.length === 0 && <EmptyState />}

      {messages.map((msg, i) => (
        <div key={i} id={msg.id} className="transition-all duration-300">
          <MessageBubble message={msg} />
        </div>
      ))}

      {loading && <LoadingIndicator />}
    </div>
  );
}
