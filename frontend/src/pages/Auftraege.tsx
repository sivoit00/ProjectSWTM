import Sidebar from '../components/Sidebar';
import { Clock, CheckCircle, XCircle } from 'lucide-react';

export default function Auftraege() {
  const auftraege = [
    { id: 1001, beschreibung: 'Ölwechsel', status: 'offen', fahrzeug: 'BMW 3er' },
    { id: 1002, beschreibung: 'Bremsen prüfen', status: 'in_bearbeitung', fahrzeug: 'Mercedes C-Klasse' },
    { id: 1003, beschreibung: 'Reifen wechseln', status: 'abgeschlossen', fahrzeug: 'VW Golf' },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'offen': return <Clock className="text-yellow-400" size={20} />;
      case 'in_bearbeitung': return <Clock className="text-blue-400" size={20} />;
      case 'abgeschlossen': return <CheckCircle className="text-green-400" size={20} />;
      default: return <XCircle className="text-red-400" size={20} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar />
      
      <div className="flex-1 overflow-auto p-8">
        <h1 className="text-white text-3xl font-bold mb-6">Meine Aufträge</h1>
        
        <div className="space-y-4">
          {auftraege.map((auftrag) => (
            <div key={auftrag.id} className="bg-gray-800 border border-gray-700 rounded-xl p-6 hover:bg-gray-700 transition-all">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {getStatusIcon(auftrag.status)}
                  <div>
                    <h3 className="text-white font-bold">Auftrag #{auftrag.id}</h3>
                    <p className="text-gray-300">{auftrag.beschreibung}</p>
                    <p className="text-gray-400 text-sm">{auftrag.fahrzeug}</p>
                  </div>
                </div>
                <span className="bg-gray-700 text-white px-4 py-2 rounded-full text-sm border border-gray-600">
                  {auftrag.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
