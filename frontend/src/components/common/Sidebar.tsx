import * as React from "react";
import { MessageSquare, LogOut } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import keycloak from "../../keycloak";

declare global {
  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any;
    }
  }
}

export default function Sidebar() {
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="w-64 bg-gradient-to-b from-gray-800 to-gray-900 flex flex-col h-screen border-r border-gray-700">
      {/* Logo and title */}
      <div className="p-6 border-b border-gray-700">
        <h1 className="text-2xl font-bold text-white">Tom'sClone</h1>
        <p className="text-sm text-gray-400 mt-1">AI-Powered Platform</p>
      </div>

      {/* Navigation menu */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        <Link
          to="/"
          className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
            isActive("/")
              ? "bg-blue-600 text-white"
              : "text-gray-300 hover:bg-gray-700"
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
              : "text-gray-300 hover:bg-gray-700"
          }`}
        >
          <MessageSquare size={20} />
          <span>MyClone</span>
        </Link>

        
      </nav>

      {/* Logout button at bottom */}
      <div className="p-4 border-t border-gray-700">
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
