import { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "../components/common/Sidebar";

export default function MainLayout() {
  const location = useLocation();
  const [clearChatTrigger, setClearChatTrigger] = useState(0);
  
  const handleClearChat = () => {
    setClearChatTrigger(prev => prev + 1);
  };
  
  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar onClearChat={location.pathname === '/chat' ? handleClearChat : undefined} />
      <div className="flex-1 overflow-hidden">
        <Outlet context={{ clearChatTrigger }} />
      </div>
    </div>
  );
}
