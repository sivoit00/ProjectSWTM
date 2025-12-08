import NotificationBell from "../../../components/common/NotificationBell";
import { useChatState } from "../hooks/useChatState";

export default function ChatHeader() {
  const { handleSend } = useChatState();
  
  const handleEmailNotification = (emailData: any) => {
      const systemPrompt = `SYSTEM_UPDATE: Es ist eine neue E-Mail eingegangen.
      Absender: ${emailData.sender}
      Betreff: ${emailData.subject}
      Inhalt: "${emailData.body}"
      
      Bitte analysiere diese E-Mail im Kontext unseres aktuellen Falls. Sag mir, was das bedeutet und was die nächsten Schritte sind.`;
      
      handleSend(systemPrompt, true);
    };

  return (
    <div className="p-4 border-b border-gray-700 bg-gray-800 relative">
      <h2 className="text-xl font-bold text-white">AI Chat</h2>
      <p className="text-sm text-gray-400">Chat with our AI to manage your vehicle services effortlessly</p>
      <div className="absolute top-4 right-4 z-50">
         <NotificationBell onProcessEmail={handleEmailNotification} />
      </div>
    </div>
  );
}
