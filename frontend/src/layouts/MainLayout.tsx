import { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "../components/common/Sidebar";

export default function MainLayout() {
  const [clearChatTrigger, setClearChatTrigger] = useState(0);
  const location = useLocation();
  const isChatRoute = location.pathname === "/chat";

  const handleClearChat = () => {
    setClearChatTrigger((prev) => prev + 1);
  };

  return (
    <div className="flex h-screen bg-gray-50 text-gray-900 dark:bg-gray-950 dark:text-gray-100">
      <Sidebar onClearChat={handleClearChat} />
      <div
        className={`flex-1 min-h-0 ${
          isChatRoute ? "overflow-hidden" : "overflow-y-auto overflow-x-hidden"
        }`}
      >
        <Outlet context={{ clearChatTrigger, setClearChatTrigger }} />
      </div>
    </div>
  );
}
