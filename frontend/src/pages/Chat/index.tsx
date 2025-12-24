import { useChatState } from "./hooks/useChatState";
import keycloak from "../../keycloak";
import { ChatSplitLayout, type EmailData } from "./components/layout/ChatSplitLayout";

export default function Chat() {
  const {
    messages,
    input,
    setInput,
    loading,
    showFileUpload,
    setShowFileUpload,
    selectedFiles,
    setSelectedFiles,
    allAgentSteps,
    handleSend,
  } = useChatState();

  const userName = keycloak.tokenParsed?.preferred_username || keycloak.tokenParsed?.name;

  const handleEmailNotification = (emailData: EmailData) => {
    const systemPrompt = `SYSTEM_UPDATE: Es ist eine neue E-Mail eingegangen.
Absender: ${emailData.sender}
Betreff: ${emailData.subject}
Inhalt: "${emailData.body}"

Bitte analysiere diese E-Mail im Kontext unseres aktuellen Falls. Sag mir, was das bedeutet und was die nächsten Schritte sind.`;

    handleSend(systemPrompt, true);
  };

  const handleTimelineEventClick = (messageId: string) => {
    const element = document.getElementById(messageId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      element.classList.add('ring-2', 'ring-indigo-500', 'rounded-lg');
      setTimeout(() => {
        element.classList.remove('ring-2', 'ring-indigo-500', 'rounded-lg');
      }, 2000);
    }
  };

  return (
    <ChatSplitLayout
      messages={messages}
      loading={loading}
      input={input}
      setInput={setInput}
      showFileUpload={showFileUpload}
      setShowFileUpload={setShowFileUpload}
      selectedFiles={selectedFiles}
      setSelectedFiles={setSelectedFiles}
      onSend={handleSend}
      allAgentSteps={allAgentSteps}
      userName={userName}
      onNotificationClick={handleEmailNotification}
      onTimelineEventClick={handleTimelineEventClick}
    />
  );
}