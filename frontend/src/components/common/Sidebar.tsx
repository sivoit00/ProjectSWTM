import { MessageSquare, LogOut, Trash2 } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import keycloak from "../../keycloak";
import { ChatSidebarSection } from "../../features/chat/components/ChatSidebarSection";

declare global {
  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any;
    }
  }
}

interface SidebarProps {
  onClearChat?: () => void;
}

export default function Sidebar({ onClearChat }: SidebarProps) {
  const location = useLocation();
  const userId = (keycloak.tokenParsed as any)?.sub || "anonymous";
  const isChatRoute = location.pathname === "/chat";
  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="w-64 bg-gradient-to-b from-gray-800 to-gray-900 flex flex-col h-screen border-r border-gray-700">
      <div className="p-6 border-b border-gray-700">
        <h1 className="text-2xl font-bold text-white">MyClone</h1>
        <p className="text-sm text-gray-400 mt-1">AI-Powered Platform</p>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-2">
        <Link
          to="/"
          className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
            isActive("/") ? "bg-blue-600 text-white" : "text-gray-300 hover:bg-gray-700"
          }`}
        >
          <MessageSquare size={20} />
          <span>Home</span>
        </Link>

        <Link
          to="/chat"
          className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
            isActive("/chat") ? "bg-blue-600 text-white" : "text-gray-300 hover:bg-gray-700"
          }`}
        >
          <MessageSquare size={20} />
          <span>MyClone</span>
        </Link>

        {isChatRoute && <ChatSidebarSection userId={userId} />}
      </nav>

      <div className="p-4 border-t border-gray-700 space-y-2">
        {onClearChat && (
          <button
            onClick={onClearChat}
            className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-red-600/20 hover:text-red-400 transition-colors w-full"
          >
            <Trash2 size={20} />
            <span>Clear Chat</span>
          </button>
        )}

        <button
          onClick={() => keycloak.logout()}
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-red-600/20 hover:text-white transition-colors w-full"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
}
