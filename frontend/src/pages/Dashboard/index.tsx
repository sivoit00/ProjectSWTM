import { useEffect, useState } from 'react';
import { PageHeader, LoadingSpinner, ErrorMessage } from '../../components/common';
import { kundenAPI, fahrzeugeAPI, werkstaettenAPI, auftraegeAPI } from '../../services/api';
import { Users, Car, Wrench, ClipboardList } from 'lucide-react';

interface Stats {
  kunden: number;
  fahrzeuge: number;
  werkstaetten: number;
  auftraege: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const [kundenRes, fahrzeugeRes, werkstaettenRes, auftraegeRes] = await Promise.all([
        kundenAPI.getAll(),
        fahrzeugeAPI.getAll(),
        werkstaettenAPI.getAll(),
        auftraegeAPI.getAll(),
      ]);

      setStats({
        kunden: kundenRes.data.length,
        fahrzeuge: fahrzeugeRes.data.length,
        werkstaetten: werkstaettenRes.data.length,
        auftraege: auftraegeRes.data.length,
      });
    } catch (err) {
      setError('Fehler beim Laden der Dashboard-Daten');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="p-6"><ErrorMessage message={error} /></div>;

  const statCards = [
    { label: 'Kunden', value: stats?.kunden || 0, icon: <Users size={32} />, color: 'blue' },
    { label: 'Fahrzeuge', value: stats?.fahrzeuge || 0, icon: <Car size={32} />, color: 'green' },
    { label: 'Werkstätten', value: stats?.werkstaetten || 0, icon: <Wrench size={32} />, color: 'purple' },
    { label: 'Aufträge', value: stats?.auftraege || 0, icon: <ClipboardList size={32} />, color: 'orange' },
  ];

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Übersicht über Ihr Fahrzeugservice-System"
      />

      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((card) => (
            <div
              key={card.label}
              className="bg-gray-800 border border-gray-700 rounded-lg p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm font-medium">{card.label}</p>
                  <p className="text-4xl font-bold text-white mt-2">{card.value}</p>
                </div>
                <div className={`text-${card.color}-500 opacity-80`}>{card.icon}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Willkommen! 👋</h2>
          <p className="text-gray-400">
            Dies ist Ihr Fahrzeugservice-Management-System. Nutzen Sie die Navigation links, um
            Kunden, Fahrzeuge, Werkstätten und Aufträge zu verwalten.
          </p>
        </div>
      </div>
    </div>
  );
}
