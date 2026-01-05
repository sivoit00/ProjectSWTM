import NotificationBell from "../../../components/common/NotificationBell";

interface ChatHeaderProps {
  onNotificationClick: (emailData: any) => void;
}

export default function ChatHeader({
  onNotificationClick,
}: ChatHeaderProps) {
  return (
    <div className="p-4 border-b border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800 relative">
      <h2 className="text-xl font-bold text-gray-900 dark:text-white">AI Chat</h2>
      <p className="text-sm text-gray-600 dark:text-gray-400">Chat with our AI to manage your vehicle services effortlessly</p>
      
      <div className="absolute top-4 right-4 z-50">
         <NotificationBell onProcessEmail={onNotificationClick} />
      </div>
    </div>
  );
}