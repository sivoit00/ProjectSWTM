import React from "react";
import CustomerTimeline from "../../../../components/common/CustomerTimeline";
import ChatHeader from "../ChatHeader";
import MessageList from "../MessageList";
import ChatInput from "../ChatInput";
import type { Message } from "../../hooks/chat/chatTypes";
import type { TimelineEvent } from "../../../../components/common/CustomerTimeline";

export interface EmailData {
  sender?: string;
  subject?: string;
  body?: string;
}

interface ChatSplitLayoutProps {
  messages: Message[];
  loading: boolean;
  input: string;
  setInput: (value: string) => void;
  showFileUpload: boolean;
  setShowFileUpload: (show: boolean) => void;
  selectedFiles: File[];
  setSelectedFiles: React.Dispatch<React.SetStateAction<File[]>>;
  onSend: () => void;
  allAgentSteps: TimelineEvent[];
  userName?: string;
  onNotificationClick: (emailData: EmailData) => void;
  onTimelineEventClick: (messageId: string) => void;
}

export function ChatSplitLayout({
  messages,
  loading,
  input,
  setInput,
  showFileUpload,
  setShowFileUpload,
  selectedFiles,
  setSelectedFiles,
  onSend,
  allAgentSteps,
  userName,
  onNotificationClick,
  onTimelineEventClick,
}: ChatSplitLayoutProps) {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950">
      <div className="w-3/5 flex flex-col border-r border-gray-200 dark:border-gray-800">
        <ChatHeader onNotificationClick={onNotificationClick} />
        <MessageList messages={messages} loading={loading} />
        <ChatInput
          input={input}
          setInput={setInput}
          loading={loading}
          showFileUpload={showFileUpload}
          setShowFileUpload={setShowFileUpload}
          selectedFiles={selectedFiles}
          setSelectedFiles={setSelectedFiles}
          onSend={onSend}
        />
      </div>

      <div className="w-2/5 bg-gray-50 dark:bg-gray-950">
        <CustomerTimeline events={allAgentSteps} onEventClick={onTimelineEventClick} userName={userName} />
      </div>
    </div>
  );
}
