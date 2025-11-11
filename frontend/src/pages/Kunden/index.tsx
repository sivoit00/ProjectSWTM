import { useEffect, useState } from 'react';
import { PageHeader, LoadingSpinner, ErrorMessage } from '../../components/common';
import { kundenAPI } from '../../services/api';
import type { Kunde } from '../../types';
import { Plus, Edit2, Trash2 } from 'lucide-react';

export default function KundenPage() {
  const [kunden, setKunden] = useState<Kunde[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadKunden();
  }, []);

  const loadKunden = async () => {
    try {
      setLoading(true);
      const res = await kundenAPI.getAll();
      setKunden(res.data);
    } catch (err) {
      setError('Fehler beim Laden der Kunden');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Kunde wirklich löschen?')) return;
    try {
      await kundenAPI.delete(id);
      await loadKunden();
    } catch (err) {
      alert('Fehler beim Löschen');
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <PageHeader
        title="Kunden"
        description="Verwaltung aller Kunden"
        action={
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
            <Plus size={20} />
            Neuer Kunde
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
                <th className="text-left px-6 py-4 text-gray-400 font-medium">E-Mail</th>
                <th className="text-left px-6 py-4 text-gray-400 font-medium">Telefon</th>
                <th className="text-right px-6 py-4 text-gray-400 font-medium">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {kunden.map((kunde) => (
                <tr key={kunde.id} className="border-b border-gray-700 hover:bg-gray-700/50 transition-colors">
                  <td className="px-6 py-4 text-white">{kunde.id}</td>
                  <td className="px-6 py-4 text-white font-medium">{kunde.name}</td>
                  <td className="px-6 py-4 text-gray-300">{kunde.email}</td>
                  <td className="px-6 py-4 text-gray-300">{kunde.telefon}</td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-blue-400 hover:text-blue-300 mr-3">
                      <Edit2 size={18} />
                    </button>
                    <button
                      onClick={() => handleDelete(kunde.id!)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {kunden.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              Keine Kunden vorhanden
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
