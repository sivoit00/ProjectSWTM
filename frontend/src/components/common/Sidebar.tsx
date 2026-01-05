import { useLocation } from "react-router-dom";
import keycloak from "../../keycloak";
import { ChatSidebarSection } from "../../features/chat/components/ChatSidebarSection";
import { useTheme } from "../../context/ThemeContext";
import { SidebarBrand } from "./sidebar/SidebarBrand";
import { SidebarNavLinks } from "./sidebar/SidebarNavLinks";
import { SidebarFooterActions } from "./sidebar/SidebarFooterActions";

interface SidebarProps {
  onClearChat?: () => void;
}

export default function Sidebar({ onClearChat }: SidebarProps) {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const tokenParsed = keycloak.tokenParsed as { sub?: string } | undefined;
  const userId = tokenParsed?.sub ?? "anonymous";
  const isChatRoute = location.pathname === "/chat";
  const isActive = (path: string) => location.pathname === path;
  const isAuthenticated = Boolean(keycloak.authenticated);

  return (
    <div className="w-64 bg-white dark:bg-gray-950 flex flex-col h-screen border-r border-gray-200 dark:border-gray-800">
      <SidebarBrand />

      <nav className="flex-1 px-4 py-6 min-h-0 flex flex-col">
        <SidebarNavLinks isActive={isActive} />

        {isChatRoute && (
          <div className="mt-4 flex-1 min-h-0 overflow-y-auto pr-1">
            <ChatSidebarSection userId={userId} onNewChat={() => {}} />
          </div>
        )}
      </nav>

      <SidebarFooterActions
        isChatRoute={isChatRoute}
        isAuthenticated={isAuthenticated}
        theme={theme}
        toggleTheme={toggleTheme}
        onClearChat={onClearChat}
      />
    </div>
  );
}
