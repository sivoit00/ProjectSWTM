import { motion } from "framer-motion";
import Sidebar from "../components/Sidebar";
import { Wrench, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function WerkstattTermin() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen bg-slate-950">
      <Sidebar />
      <div className="flex-1 ml-64 p-8">
        {/* Back Button */}
        <button
          onClick={() => navigate("/neuer-auftrag")}
          className="mb-6 flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
          <span>Zurück zur Auswahl</span>
        </button>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center gap-4 mb-4">
            <div className="bg-purple-900 p-3 rounded-lg">
              <Wrench className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-white">Werkstatttermin anfragen</h1>
              <p className="text-gray-400">
                Vereinbaren Sie einen Termin in unserer Werkstatt
              </p>
            </div>
          </div>
        </motion.div>

        {/* Placeholder Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-slate-900 border border-slate-700 rounded-lg p-8"
        >
          <div className="text-center py-12">
            <div className="mb-6">
              <div className="inline-block p-4 bg-slate-800 rounded-full mb-4">
                <Wrench className="h-16 w-16 text-gray-400" />
              </div>
            </div>
            <h2 className="text-2xl font-bold text-white mb-3">
              Formular wird geladen...
            </h2>
            <p className="text-gray-400 mb-6 max-w-md mx-auto">
              Das Werkstatttermin-Formular wird in einer zukünftigen Version
              implementiert.
            </p>
            <div className="bg-slate-800 border border-slate-600 rounded-lg p-6 max-w-2xl mx-auto text-left">
              <h3 className="text-lg font-semibold text-white mb-3">
                Geplante Features:
              </h3>
              <ul className="space-y-2 text-gray-300">
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">•</span>
                  Auswahl des Fahrzeugs
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">•</span>
                  Terminvorschläge mit Kalenderansicht
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">•</span>
                  Art der Wartung auswählen (Inspektion, Reparatur, etc.)
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">•</span>
                  Werkstatt auswählen
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">•</span>
                  Automatische Terminbestätigung per Email
                </li>
              </ul>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
