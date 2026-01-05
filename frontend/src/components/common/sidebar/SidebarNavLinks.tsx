import { MessageSquare } from "lucide-react";
import { Link } from "react-router-dom";

interface SidebarNavLinksProps {
  isActive: (path: string) => boolean;
}

export function SidebarNavLinks({ isActive }: SidebarNavLinksProps) {
  return (
    <div className="space-y-2">
      <Link
        to="/"
        className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
          isActive("/")
            ? "bg-indigo-600 text-white"
            : "text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-900"
        }`}
      >
        <MessageSquare size={20} />
        <span>Home</span>
      </Link>

      <Link
        to="/chat"
        className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
          isActive("/chat")
            ? "bg-indigo-600 text-white"
            : "text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-900"
        }`}
      >
        <MessageSquare size={20} />
        <span>MyClone</span>
      </Link>

      <Link
        to="/profile"
        className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
          isActive("/profile")
            ? "bg-indigo-600 text-white"
            : "text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-900"
        }`}
      >
        <MessageSquare size={20} />
        <span>MyProfile</span>
      </Link>
    </div>
  );
}
