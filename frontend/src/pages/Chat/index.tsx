import CustomerTimeline from "../../components/common/CustomerTimeline";
import ChatHeader from "./components/ChatHeader";
import MessageList from "./components/MessageList";
import ChatInput from "./components/ChatInput";
import { useChatState } from "./hooks/useChatState";
import keycloak from "../../keycloak";


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

  const handleEmailNotification = (emailData: any) => {
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
      element.classList.add('ring-2', 'ring-blue-500', 'rounded-lg');
      setTimeout(() => {
        element.classList.remove('ring-2', 'ring-blue-500', 'rounded-lg');
      }, 2000);
    }
  };

  return (
    <div className="flex h-screen bg-gray-800">
      {/* Linke Spalte: Chat */}
      <div className="w-3/5 flex flex-col border-r border-gray-700">
        <ChatHeader onNotificationClick={handleEmailNotification} />
        <MessageList messages={messages} loading={loading} />
        <ChatInput
          input={input}
          setInput={setInput}
          loading={loading}
          showFileUpload={showFileUpload}
          setShowFileUpload={setShowFileUpload}
          selectedFiles={selectedFiles}
          setSelectedFiles={setSelectedFiles}
          onSend={handleSend}
        />
      </div>

      {/* Rechte Spalte: Timeline */}
      <div className="w-2/5 bg-gray-900">
        <CustomerTimeline events={allAgentSteps} onEventClick={handleTimelineEventClick} userName={userName} />
      </div>
    </div>
  );
}