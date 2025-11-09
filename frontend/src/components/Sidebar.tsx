import { NavLink } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, FileText, ClipboardList, BarChart3, LogOut } from 'lucide-react';

export default function Sidebar() {
  const menuItems = [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
    { name: 'Chat', icon: MessageSquare, path: '/chat' },
    { name: 'Schadensmeldung', icon: FileText, path: '/schadensmeldung' },
    { name: 'Aufträge', icon: ClipboardList, path: '/auftraege' },
    { name: 'Visualisierung', icon: BarChart3, path: '/visualisierung' },
  ];

  return (
    <div className="w-64 bg-gray-800 h-screen flex flex-col border-r border-gray-700">
      {/* Logo */}
      <div className="p-6 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">🤖</span>
          </div>
          <h1 className="text-white text-2xl font-bold">MyCLONE</h1>
        </div>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    isActive
                      ? 'bg-blue-600 text-white font-semibold'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`
                }
              >
                <item.icon size={30} />
                <span>{item.name}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-gray-700">
        <button className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-red-600 hover:text-white w-full transition-all">
          <LogOut size={20} />
          <span>Logout</span>
        </button>
        <div className="text-gray-500 text-xs mt-2 px-4">localhost:5174</div>
      </div>
    </div>
  );
}
