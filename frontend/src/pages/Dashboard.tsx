import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { User, Car, FileText, Lightbulb, Activity } from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();
  const stats = [
    { icon: User, label: 'Mein Konto', value: 'Aktiv', color: 'bg-blue-500' },
    { icon: Car, label: 'Meine Fahrzeuge', value: '0', color: 'bg-green-500' },
    { icon: FileText, label: 'Meine Aufträge', value: '0', color: 'bg-purple-500' },
    { icon: Lightbulb, label: 'Status', value: '-', color: 'bg-yellow-500' },
  ];

  const recentActivities = [
    { id: 1001, title: 'Auftrag #1001 aktualisiert', time: 'vor 1 Stunden' },
    { id: 1002, title: 'Auftrag #1002 aktualisiert', time: 'vor 2 Stunden' },
    { id: 1003, title: 'Auftrag #1003 aktualisiert', time: 'vor 3 Stunden' },
  ];

  const quickActions = [
    { label: '+ Neuen Auftrag erstellen', color: 'bg-cyan-400', action: () => navigate('/neuer-auftrag') },
    { label: 'Schadensmeldung einreichen', color: 'bg-blue-600', action: () => navigate('/schadensmeldung') },
    { label: 'Chat öffnen', color: 'bg-blue-600', action: () => navigate('/chat') },
  ];

  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar />
      
      <div className="flex-1 overflow-auto bg-gray-900">
        <div className="p-8">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat, index) => (
              <div
                key={index}
                className="bg-gray-800 border border-gray-700 rounded-xl p-6 hover:bg-gray-750 transition-all"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
                    <p className="text-white text-3xl font-bold">{stat.value}</p>
                  </div>
                  <div className={`${stat.color} p-4 rounded-lg`}>
                    <stat.icon className="text-white" size={32} />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Activities */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
              <h2 className="text-white text-xl font-bold mb-4 flex items-center gap-2">
                <Activity size={24} />
                Letzte Aktivitäten
              </h2>
              <div className="space-y-3">
                {recentActivities.map((activity) => (
                  <div
                    key={activity.id}
                    className="bg-gray-700 p-4 rounded-lg hover:bg-gray-600 transition-all cursor-pointer"
                  >
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      <p className="text-white font-medium">{activity.title}</p>
                    </div>
                    <p className="text-gray-400 text-sm ml-4 mt-1">{activity.time}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
              <h2 className="text-white text-xl font-bold mb-4">Schnellzugriff</h2>
              <div className="space-y-3">
                {quickActions.map((action, index) => (
                  <button
                    key={index}
                    onClick={action.action}
                    className={`${action.color} hover:opacity-90 text-white font-semibold py-4 px-6 rounded-lg w-full text-left transition-all transform hover:scale-105`}
                  >
                    {action.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
