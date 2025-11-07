import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import Sidebar from "../components/Sidebar";

interface Auftrag {
  id: number;
  beschreibung: string;
  status: string;
  erstellt_am: string;
  kosten: number;
  fahrzeug_id: number;
  werkstatt_id: number;
}

export default function Visualisierung() {
  const [auftraege, setAuftraege] = useState<Auftrag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchMyAuftraege();
  }, []);

  const fetchMyAuftraege = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Nicht angemeldet");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/auftraege/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Fehler beim Laden der Aufträge");
      }

      const data = await response.json();
      setAuftraege(data);
    } catch (err) {
      setError("Fehler beim Laden der Daten");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Status-Verteilung berechnen
  const statusCount = {
    offen: auftraege.filter((a) => a.status.toLowerCase() === "offen").length,
    "in bearbeitung": auftraege.filter((a) => a.status.toLowerCase() === "in bearbeitung").length,
    abgeschlossen: auftraege.filter((a) => a.status.toLowerCase() === "abgeschlossen").length,
  };

  const chartData = [
    { name: "Offen", value: statusCount.offen, color: "#facc15" },
    { name: "In Bearbeitung", value: statusCount["in bearbeitung"], color: "#3b82f6" },
    { name: "Abgeschlossen", value: statusCount.abgeschlossen, color: "#22c55e" },
  ].filter((item) => item.value > 0); // Nur Einträge mit Wert > 0

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
          <h1 className="text-4xl font-bold text-white mb-2">Visualisierung</h1>
          <p className="text-gray-400">Ihre Aufträge im Überblick</p>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center text-gray-400 py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4">Lädt Daten...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-500/20 border border-red-500 text-red-300 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Content */}
        {!loading && !error && (
          <div className="space-y-8">
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-slate-900 border border-slate-700 rounded-xl p-6"
              >
                <p className="text-gray-400 text-sm mb-1">Gesamt</p>
                <p className="text-3xl font-bold text-white">{auftraege.length}</p>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-slate-900 border border-yellow-500/30 rounded-xl p-6"
              >
                <p className="text-gray-400 text-sm mb-1">Offen</p>
                <p className="text-3xl font-bold text-yellow-400">{statusCount.offen}</p>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-slate-900 border border-blue-500/30 rounded-xl p-6"
              >
                <p className="text-gray-400 text-sm mb-1">In Bearbeitung</p>
                <p className="text-3xl font-bold text-blue-400">{statusCount["in bearbeitung"]}</p>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-slate-900 border border-green-500/30 rounded-xl p-6"
              >
                <p className="text-gray-400 text-sm mb-1">Abgeschlossen</p>
                <p className="text-3xl font-bold text-green-400">{statusCount.abgeschlossen}</p>
              </motion.div>
            </div>

            {/* Chart */}
            {chartData.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="bg-slate-900 border border-slate-700 rounded-xl p-8"
              >
                <h2 className="text-2xl font-bold text-white mb-6">Status-Verteilung</h2>
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </motion.div>
            )}

            {/* Aufträge Liste */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-slate-900 border border-slate-700 rounded-xl overflow-hidden"
            >
              <div className="p-6 border-b border-slate-700">
                <h2 className="text-2xl font-bold text-white">Meine Aufträge</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-800 border-b border-slate-700">
                    <tr>
                      <th className="px-6 py-4 text-left text-white font-semibold">ID</th>
                      <th className="px-6 py-4 text-left text-white font-semibold">Beschreibung</th>
                      <th className="px-6 py-4 text-left text-white font-semibold">Status</th>
                      <th className="px-6 py-4 text-left text-white font-semibold">Erstellt am</th>
                      <th className="px-6 py-4 text-left text-white font-semibold">Kosten</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700">
                    {auftraege.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-6 py-12 text-center text-gray-400">
                          Keine Aufträge vorhanden
                        </td>
                      </tr>
                    ) : (
                      auftraege.map((auftrag, index) => (
                        <motion.tr
                          key={auftrag.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="hover:bg-slate-800 transition"
                        >
                          <td className="px-6 py-4 text-gray-300">#{auftrag.id}</td>
                          <td className="px-6 py-4 text-white font-medium">{auftrag.beschreibung}</td>
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
                            {new Date(auftrag.erstellt_am).toLocaleDateString("de-DE")}
                          </td>
                          <td className="px-6 py-4 text-green-400 font-semibold">
                            {auftrag.kosten ? `${auftrag.kosten} €` : "-"}
                          </td>
                        </motion.tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
}
