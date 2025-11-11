import { useEffect, useState } from 'react';
import { PageHeader, LoadingSpinner, ErrorMessage } from '../../components/common';
import { fahrzeugeAPI } from '../../services/api';
import type { Fahrzeug } from '../../types';
import { Plus, Edit2, Trash2 } from 'lucide-react';

export default function FahrzeugePage() {
  const [fahrzeuge, setFahrzeuge] = useState<Fahrzeug[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadFahrzeuge();
  }, []);

  const loadFahrzeuge = async () => {
    try {
      setLoading(true);
      const res = await fahrzeugeAPI.getAll();
      setFahrzeuge(res.data);
    } catch (err) {
      setError('Fehler beim Laden der Fahrzeuge');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Fahrzeug wirklich löschen?')) return;
    try {
      await fahrzeugeAPI.delete(id);
      await loadFahrzeuge();
    } catch (err) {
      alert('Fehler beim Löschen');
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <PageHeader
        title="Fahrzeuge"
        description="Verwaltung aller Fahrzeuge"
        action={
          <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
            <Plus size={20} />
            Neues Fahrzeug
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
                <th className="text-left px-6 py-4 text-gray-400 font-medium">Marke</th>
                <th className="text-left px-6 py-4 text-gray-400 font-medium">Modell</th>
                <th className="text-left px-6 py-4 text-gray-400 font-medium">Baujahr</th>
                <th className="text-left px-6 py-4 text-gray-400 font-medium">Kunden-ID</th>
                <th className="text-right px-6 py-4 text-gray-400 font-medium">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {fahrzeuge.map((fahrzeug) => (
                <tr key={fahrzeug.id} className="border-b border-gray-700 hover:bg-gray-700/50 transition-colors">
                  <td className="px-6 py-4 text-white">{fahrzeug.id}</td>
                  <td className="px-6 py-4 text-white font-medium">{fahrzeug.marke}</td>
                  <td className="px-6 py-4 text-gray-300">{fahrzeug.modell}</td>
                  <td className="px-6 py-4 text-gray-300">{fahrzeug.baujahr}</td>
                  <td className="px-6 py-4 text-gray-300">{fahrzeug.kunde_id}</td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-blue-400 hover:text-blue-300 mr-3">
                      <Edit2 size={18} />
                    </button>
                    <button
                      onClick={() => handleDelete(fahrzeug.id!)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {fahrzeuge.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              Keine Fahrzeuge vorhanden
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
