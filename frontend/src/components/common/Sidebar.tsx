import { Link, useLocation } from 'react-router-dom';
import { Home, Users, Car, Wrench, ClipboardList, MessageSquare, LogOut } from 'lucide-react';
import keycloak from '../../keycloak';

interface NavItem {
  path: string;
  icon: React.ReactNode;
  label: string;
}

const navItems: NavItem[] = [
  { path: '/', icon: <Home size={20} />, label: 'Dashboard' },
  { path: '/kunden', icon: <Users size={20} />, label: 'Kunden' },
  { path: '/fahrzeuge', icon: <Car size={20} />, label: 'Fahrzeuge' },
  { path: '/werkstaetten', icon: <Wrench size={20} />, label: 'Werkstätten' },
  { path: '/auftraege', icon: <ClipboardList size={20} />, label: 'Aufträge' },
  { path: '/chat', icon: <MessageSquare size={20} />, label: 'Chat' },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
      <div className="p-6 border-b border-gray-700">
        <h1 className="text-2xl font-bold text-white">🚗 FahrzeugService</h1>
        <p className="text-sm text-gray-400 mt-1">Management System</p>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              {item.icon}
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-gray-700">
        <button
          onClick={() => keycloak.logout()}
          className="w-full flex items-center gap-3 px-4 py-3 text-gray-300 hover:bg-red-600 hover:text-white rounded-lg transition-all"
        >
          <LogOut size={20} />
          <span className="font-medium">Abmelden</span>
        </button>
      </div>
    </div>
  );
}
