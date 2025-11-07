import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Search, Filter } from "lucide-react";
import Sidebar from "../components/Sidebar";

interface Auftrag {
  id: number;
  fahrzeug_id: number;
  werkstatt_id: number;
  beschreibung: string;
  status: string;
  startdatum: string;
  enddatum: string | null;
  kosten: number;
}

export default function Auftraege() {
  const [auftraege, setAuftraege] = useState<Auftrag[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");

  useEffect(() => {
    fetchAuftraege();
  }, []);

  const fetchAuftraege = async () => {
    try {
      const response = await fetch("http://localhost:8000/auftraege");
      const data = await response.json();
      setAuftraege(data);
    } catch (error) {
      console.error("Fehler beim Laden der Aufträge:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredAuftraege = auftraege.filter((auftrag) => {
    const matchesSearch = auftrag.beschreibung.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === "all" || auftrag.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "offen":
        return "bg-yellow-500/20 text-yellow-300 border-yellow-500/50";
      case "in bearbeitung":
        return "bg-blue-500/20 text-blue-300 border-blue-500/50";
      case "abgeschlossen":
        return "bg-green-500/20 text-green-300 border-green-500/50";
      default:
        return "bg-gray-500/20 text-gray-300 border-gray-500/50";
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950">
      <Sidebar />

      <div className="flex-1 ml-64 p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Auftragsübersicht</h1>
          <p className="text-gray-400">Verwalten Sie alle Werkstattaufträge</p>
        </div>

        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Aufträge durchsuchen..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-slate-900 text-white border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Status Filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-3 text-gray-400" size={20} />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="pl-10 pr-8 py-3 bg-slate-900 text-white border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none cursor-pointer"
            >
              <option value="all">Alle Status</option>
              <option value="Offen">Offen</option>
              <option value="In Bearbeitung">In Bearbeitung</option>
              <option value="Abgeschlossen">Abgeschlossen</option>
            </select>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center text-gray-400 py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4">Lädt Aufträge...</p>
          </div>
        )}

        {/* Aufträge Table */}
        {!loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-slate-900 border border-slate-700 rounded-xl overflow-hidden"
          >
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-800 border-b border-slate-700">
                  <tr>
                    <th className="px-6 py-4 text-left text-white font-semibold">ID</th>
                    <th className="px-6 py-4 text-left text-white font-semibold">Beschreibung</th>
                    <th className="px-6 py-4 text-left text-white font-semibold">Status</th>
                    <th className="px-6 py-4 text-left text-white font-semibold">Startdatum</th>
                    <th className="px-6 py-4 text-left text-white font-semibold">Kosten</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {filteredAuftraege.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-12 text-center text-gray-400">
                        Keine Aufträge gefunden
                      </td>
                    </tr>
                  ) : (
                    filteredAuftraege.map((auftrag, index) => (
                      <motion.tr
                        key={auftrag.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="hover:bg-slate-800 transition"
                      >
                        <td className="px-6 py-4 text-gray-300">#{auftrag.id}</td>
                        <td className="px-6 py-4 text-white font-medium">
                          {auftrag.beschreibung}
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(
                              auftrag.status
                            )}`}
                          >
                            {auftrag.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-gray-300">
                          {new Date(auftrag.startdatum).toLocaleDateString("de-DE")}
                        </td>
                        <td className="px-6 py-4 text-green-400 font-semibold">
                          {auftrag.kosten.toFixed(2)} €
                        </td>
                      </motion.tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {/* Summary Stats */}
        {!loading && filteredAuftraege.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="mt-6 flex gap-6 text-gray-400"
          >
            <div>
              <span className="font-medium">Gesamt: </span>
              <span className="text-white">{filteredAuftraege.length} Aufträge</span>
            </div>
            <div>
              <span className="font-medium">Gesamtkosten: </span>
              <span className="text-green-400">
                {filteredAuftraege.reduce((sum, a) => sum + a.kosten, 0).toFixed(2)} €
              </span>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
