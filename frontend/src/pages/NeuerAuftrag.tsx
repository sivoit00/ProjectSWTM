import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { FileText, Car, Wrench, ClipboardList } from 'lucide-react';

export default function NeuerAuftrag() {
  const navigate = useNavigate();

  const auftragsTypen = [
    {
      icon: FileText,
      title: 'Schaden melden',
      description: 'Einen Schaden an Ihrem Fahrzeug melden',
      path: '/schadensmeldung',
      color: 'bg-red-500'
    },
    {
      icon: Car,
      title: 'Neues Fahrzeug registrieren',
      description: 'Ein neues Fahrzeug zur Verwaltung hinzufügen',
      path: '/neues-fahrzeug',
      color: 'bg-green-500'
    },
    {
      icon: Wrench,
      title: 'Service / Inspektion anfragen',
      description: 'Reguläre Wartung oder Inspektion beauftragen',
      path: '/service-inspektion',
      color: 'bg-blue-500'
    },
    {
      icon: ClipboardList,
      title: 'Versicherung oder Kundendaten ändern',
      description: 'Ihre persönlichen Daten oder Versicherungsinformationen aktualisieren',
      path: '/kundendaten',
      color: 'bg-purple-500'
    }
  ];

  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar />
      
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">Neuen Auftrag erstellen</h1>
            <p className="text-gray-400">Wählen Sie den Typ des Auftrags aus</p>
          </div>

          {/* Auftragstypen Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {auftragsTypen.map((typ, index) => (
              <button
                key={index}
                onClick={() => navigate(typ.path)}
                className="bg-gray-800 border border-gray-700 rounded-xl p-6 hover:bg-gray-700 transition-all transform hover:scale-105 text-left group"
              >
                <div className={`${typ.color} w-16 h-16 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <typ.icon className="text-white" size={32} />
                </div>
                <h3 className="text-white text-xl font-bold mb-2">{typ.title}</h3>
                <p className="text-gray-400 text-sm">{typ.description}</p>
              </button>
            ))}
          </div>

          {/* Zurück Button */}
          <div className="mt-8">
            <button
              onClick={() => navigate('/dashboard')}
              className="bg-gray-700 hover:bg-gray-600 text-white font-semibold px-6 py-3 rounded-lg transition-all border border-gray-600"
            >
              ← Zurück zum Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
