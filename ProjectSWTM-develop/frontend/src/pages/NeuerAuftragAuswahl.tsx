import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import Sidebar from "../components/Sidebar";
import {
  FileText,
  Car,
  Shield,
  Wrench,
  Plus,
} from "lucide-react";

interface AuftragOption {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  route: string;
  color: string;
}

export default function NeuerAuftragAuswahl() {
  const navigate = useNavigate();

  const auftragOptionen: AuftragOption[] = [
    {
      id: "schadensmeldung",
      title: "Schadensmeldung einreichen",
      description: "Melden Sie einen Schaden an Ihrem Fahrzeug",
      icon: <FileText className="h-12 w-12" />,
      route: "/auftrag/schadensmeldung",
      color: "from-red-900 to-red-800",
    },
    {
      id: "fahrzeug",
      title: "Neues Fahrzeug registrieren",
      description: "Fügen Sie ein neues Fahrzeug zu Ihrem Account hinzu",
      icon: <Car className="h-12 w-12" />,
      route: "/auftrag/fahrzeug-registrieren",
      color: "from-blue-900 to-blue-800",
    },
    {
      id: "versicherung",
      title: "Versicherung aktualisieren",
      description: "Ändern oder aktualisieren Sie Ihre Versicherungsdaten",
      icon: <Shield className="h-12 w-12" />,
      route: "/auftrag/versicherung",
      color: "from-green-900 to-green-800",
    },
    {
      id: "werkstatt",
      title: "Werkstatttermin anfragen",
      description: "Vereinbaren Sie einen Termin in unserer Werkstatt",
      icon: <Wrench className="h-12 w-12" />,
      route: "/auftrag/werkstatt",
      color: "from-purple-900 to-purple-800",
    },
    {
      id: "sonstiges",
      title: "Sonstigen Auftrag erstellen",
      description: "Erstellen Sie einen individuellen Auftrag",
      icon: <Plus className="h-12 w-12" />,
      route: "/auftrag/sonstiges",
      color: "from-gray-900 to-gray-800",
    },
  ];

  const handleSelectOption = (route: string) => {
    navigate(route);
  };

  return (
    <div className="flex min-h-screen bg-slate-950">
      <Sidebar />
      <div className="flex-1 ml-64 p-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2">
            Welchen Auftrag möchten Sie erstellen?
          </h1>
          <p className="text-gray-400">
            Wählen Sie eine der folgenden Optionen, um fortzufahren
          </p>
        </motion.div>

        {/* Auftrags-Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {auftragOptionen.map((option, index) => (
            <motion.div
              key={option.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => handleSelectOption(option.route)}
              className="group cursor-pointer"
            >
              <div
                className={`h-full bg-gradient-to-br ${option.color} rounded-lg p-6 border border-slate-700 hover:border-slate-500 transition-all duration-300 transform hover:scale-105 hover:shadow-xl`}
              >
                {/* Icon */}
                <div className="mb-4 text-white opacity-80 group-hover:opacity-100 transition-opacity">
                  {option.icon}
                </div>

                {/* Titel */}
                <h3 className="text-xl font-bold text-white mb-2">
                  {option.title}
                </h3>

                {/* Beschreibung */}
                <p className="text-gray-300 text-sm leading-relaxed">
                  {option.description}
                </p>

                {/* Hover-Indikator */}
                <div className="mt-4 flex items-center text-sm text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity">
                  <span>Klicken zum Fortfahren</span>
                  <svg
                    className="ml-2 h-4 w-4 transform group-hover:translate-x-1 transition-transform"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Info-Box */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-8 bg-slate-900 border border-slate-700 rounded-lg p-6"
        >
          <h3 className="text-lg font-semibold text-white mb-2">
            💡 Hinweis
          </h3>
          <p className="text-gray-400 text-sm">
            Nach Auswahl der Auftragsart werden Sie zum entsprechenden Formular
            weitergeleitet. Alle Ihre Daten werden sicher verschlüsselt
            übertragen.
          </p>
        </motion.div>
      </div>
    </div>
  );
}
