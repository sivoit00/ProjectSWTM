import { LogIn, LogOut, Moon, Plus, Sun, Trash2 } from "lucide-react";
import keycloak from "../../../keycloak";

interface SidebarFooterActionsProps {
  isChatRoute: boolean;
  isAuthenticated: boolean;
  theme: "light" | "dark";
  toggleTheme: () => void;
  onClearChat?: () => void;
}

export function SidebarFooterActions({
  isChatRoute,
  isAuthenticated,
  theme,
  toggleTheme,
  onClearChat,
}: SidebarFooterActionsProps) {
  return (
    <div className="p-4 border-t border-gray-200 dark:border-gray-800 space-y-2">
      {isChatRoute && (
        <button
          onClick={() => {
            const w = window as unknown as { __handleNewChat?: () => void };
            w.__handleNewChat?.();
          }}
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-900 transition-colors w-full"
        >
          <Plus size={20} />
          <span>Neuer Chat</span>
        </button>
      )}

      {isChatRoute && onClearChat && (
        <button
          onClick={onClearChat}
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-red-50 hover:text-red-700 dark:text-gray-200 dark:hover:bg-red-500/20 dark:hover:text-red-300 transition-colors w-full"
        >
          <Trash2 size={20} />
          <span>Clear Chat</span>
        </button>
      )}

      <button
        onClick={toggleTheme}
        className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-900 transition-colors w-full"
      >
        {theme === "dark" ? <Moon size={20} /> : <Sun size={20} />}
        <span>{theme === "dark" ? "Dark Mode" : "Light Mode"}</span>
      </button>

      {isChatRoute ? (
        <button
          onClick={() => keycloak.logout()}
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-red-50 hover:text-gray-900 dark:text-gray-200 dark:hover:bg-red-500/20 dark:hover:text-gray-100 transition-colors w-full"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      ) : isAuthenticated ? (
        <button
          onClick={() => keycloak.logout()}
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-red-50 hover:text-gray-900 dark:text-gray-200 dark:hover:bg-red-500/20 dark:hover:text-gray-100 transition-colors w-full"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      ) : (
        <button
          onClick={() => keycloak.login()}
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-900 transition-colors w-full"
        >
          <LogIn size={20} />
          <span>Login</span>
        </button>
      )}
    </div>
  );
}
