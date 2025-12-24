import { MessageSquare, LogOut, Trash2, Plus, LogIn, Moon, Sun } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import keycloak from "../../keycloak";
import { ChatSidebarSection } from "../../features/chat/components/ChatSidebarSection";
import { useTheme } from "../../context/ThemeContext";

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
  const { theme, toggleTheme } = useTheme();
  const userId = (keycloak.tokenParsed as any)?.sub || "anonymous";
  const isChatRoute = location.pathname === "/chat";
  const isActive = (path: string) => location.pathname === path;
  const isAuthenticated = Boolean(keycloak.authenticated);

  return (
    <div className="w-64 bg-gradient-to-b from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 flex flex-col h-screen border-r border-gray-200 dark:border-gray-700">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">MyClone</h1>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">AI-Powered Platform</p>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-2">
        <Link
          to="/"
          className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
            isActive("/")
              ? "bg-blue-600 text-white"
              : "text-gray-700 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-700"
          }`}
        >
          <MessageSquare size={20} />
          <span>Home</span>
        </Link>

        <Link
          to="/chat"
          className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
            isActive("/chat")
              ? "bg-blue-600 text-white"
              : "text-gray-700 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-700"
          }`}
        >
          <MessageSquare size={20} />
          <span>MyClone</span>
        </Link>

        {isChatRoute && <ChatSidebarSection userId={userId} onNewChat={() => {}} />}
      </nav>

      <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
        {isChatRoute && (
          <button
            onClick={() => {
              if ((window as any).__handleNewChat) {
                (window as any).__handleNewChat();
              }
            }}
            className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors w-full"
          >
            <Plus size={20} />
            <span>Neuer Chat</span>
          </button>
        )}

        {isChatRoute && onClearChat && (
          <button
            onClick={onClearChat}
            className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-red-50 hover:text-red-600 dark:text-gray-300 dark:hover:bg-red-600/20 dark:hover:text-red-400 transition-colors w-full"
          >
            <Trash2 size={20} />
            <span>Clear Chat</span>
          </button>
        )}

        <button
          onClick={toggleTheme}
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors w-full"
        >
          {theme === "dark" ? <Moon size={20} /> : <Sun size={20} />}
          <span>{theme === "dark" ? "Dark Mode" : "Light Mode"}</span>
        </button>

        {isChatRoute ? (
          <button
            onClick={() => keycloak.logout()}
            className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-red-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-red-600/20 dark:hover:text-white transition-colors w-full"
          >
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        ) : (
          <button
            onClick={() => {
              if (!isAuthenticated) keycloak.login();
            }}
            className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors w-full"
          >
            <LogIn size={20} />
            <span>Login</span>
          </button>
        )}
      </div>
    </div>
  );
}
