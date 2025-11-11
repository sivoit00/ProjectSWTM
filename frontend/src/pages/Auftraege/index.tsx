import { useEffect, useState } from 'react';
import { PageHeader, LoadingSpinner, ErrorMessage } from '../../components/common';
import { auftraegeAPI } from '../../services/api';
import type { Auftrag } from '../../types';
import { Plus, Edit2, Trash2 } from 'lucide-react';

export default function AuftraegePage() {
  const [auftraege, setAuftraege] = useState<Auftrag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAuftraege();
  }, []);

  const loadAuftraege = async () => {
    try {
      setLoading(true);
      const res = await auftraegeAPI.getAll();
      setAuftraege(res.data);
    } catch (err) {
      setError('Fehler beim Laden der Aufträge');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Auftrag wirklich löschen?')) return;
    try {
      await auftraegeAPI.delete(id);
      await loadAuftraege();
    } catch (err) {
      alert('Fehler beim Löschen');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'offen':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500';
      case 'in bearbeitung':
        return 'bg-blue-500/20 text-blue-400 border-blue-500';
      case 'abgeschlossen':
        return 'bg-green-500/20 text-green-400 border-green-500';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500';
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <PageHeader
        title="Aufträge"
        description="Verwaltung aller Aufträge"
        action={
          <button className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
            <Plus size={20} />
            Neuer Auftrag
          </button>
        }
      />

      <div className="p-6">
        {error && <ErrorMessage message={error} />}

        <div className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-900 border-b border-gray-700">
              <tr>
                <th className="text-left px-6 py-4 text-gray-400 font-medium">ID</th>
                <th className="text-left px-6 py-4 text-gray-400 font-medium">Beschreibung</th>
                <th className="text-left px-6 py-4 text-gray-400 font-medium">Status</th>
                <th className="text-left px-6 py-4 text-gray-400 font-medium">Fahrzeug-ID</th>
                <th className="text-left px-6 py-4 text-gray-400 font-medium">Werkstatt-ID</th>
                <th className="text-left px-6 py-4 text-gray-400 font-medium">Kosten</th>
                <th className="text-right px-6 py-4 text-gray-400 font-medium">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {auftraege.map((auftrag) => (
                <tr key={auftrag.id} className="border-b border-gray-700 hover:bg-gray-700/50 transition-colors">
                  <td className="px-6 py-4 text-white">{auftrag.id}</td>
                  <td className="px-6 py-4 text-white font-medium max-w-xs truncate">
                    {auftrag.beschreibung}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(auftrag.status)}`}>
                      {auftrag.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-300">{auftrag.fahrzeug_id}</td>
                  <td className="px-6 py-4 text-gray-300">{auftrag.werkstatt_id}</td>
                  <td className="px-6 py-4 text-gray-300">
                    {auftrag.kosten ? `${auftrag.kosten.toFixed(2)} €` : '-'}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-blue-400 hover:text-blue-300 mr-3">
                      <Edit2 size={18} />
                    </button>
                    <button
                      onClick={() => handleDelete(auftrag.id!)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {auftraege.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              Keine Aufträge vorhanden
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
