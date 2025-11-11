import { useEffect, useState } from 'react';
import { PageHeader, LoadingSpinner, ErrorMessage } from '../../components/common';
import { werkstaettenAPI } from '../../services/api';
import type { Werkstatt } from '../../types';
import { Plus, Edit2, Trash2 } from 'lucide-react';

export default function WerkstaettenPage() {
  const [werkstaetten, setWerkstaetten] = useState<Werkstatt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadWerkstaetten();
  }, []);

  const loadWerkstaetten = async () => {
    try {
      setLoading(true);
      const res = await werkstaettenAPI.getAll();
      setWerkstaetten(res.data);
    } catch (err) {
      setError('Fehler beim Laden der Werkstätten');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Werkstatt wirklich löschen?')) return;
    try {
      await werkstaettenAPI.delete(id);
      await loadWerkstaetten();
    } catch (err) {
      alert('Fehler beim Löschen');
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <PageHeader
        title="Werkstätten"
        description="Verwaltung aller Werkstätten"
        action={
          <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
            <Plus size={20} />
            Neue Werkstatt
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
                <th className="text-left px-6 py-4 text-gray-400 font-medium">Name</th>
                <th className="text-left px-6 py-4 text-gray-400 font-medium">Adresse</th>
                <th className="text-left px-6 py-4 text-gray-400 font-medium">PLZ</th>
                <th className="text-left px-6 py-4 text-gray-400 font-medium">Ort</th>
                <th className="text-right px-6 py-4 text-gray-400 font-medium">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {werkstaetten.map((werkstatt) => (
                <tr key={werkstatt.id} className="border-b border-gray-700 hover:bg-gray-700/50 transition-colors">
                  <td className="px-6 py-4 text-white">{werkstatt.id}</td>
                  <td className="px-6 py-4 text-white font-medium">{werkstatt.name}</td>
                  <td className="px-6 py-4 text-gray-300">{werkstatt.adresse}</td>
                  <td className="px-6 py-4 text-gray-300">{werkstatt.plz}</td>
                  <td className="px-6 py-4 text-gray-300">{werkstatt.ort}</td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-blue-400 hover:text-blue-300 mr-3">
                      <Edit2 size={18} />
                    </button>
                    <button
                      onClick={() => handleDelete(werkstatt.id!)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {werkstaetten.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              Keine Werkstätten vorhanden
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
