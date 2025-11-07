import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Users, Car, Wrench, ClipboardCheck } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";

interface UserInfo {
  user: {
    id: number;
    email: string;
    name: string | null;
  };
  kunde: {
    id: number;
    name: string;
    email: string;
    telefon: string | null;
  } | null;
  stats: {
    fahrzeuge: number;
    auftraege: number;
  };
}

export default function Dashboard() {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserInfo();
  }, []);

  const fetchUserInfo = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
      const response = await fetch("http://localhost:8000/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUserInfo(data);
      }
    } catch (error) {
      console.error("Fehler beim Laden der User-Info:", error);
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    { 
      icon: Users, 
      label: "Mein Konto", 
      value: userInfo?.kunde ? "Aktiv" : "Neu", 
      color: "bg-blue-500" 
    },
    { 
      icon: Car, 
      label: "Meine Fahrzeuge", 
      value: userInfo?.stats.fahrzeuge.toString() || "0", 
      color: "bg-green-500" 
    },
    { 
      icon: ClipboardCheck, 
      label: "Meine Aufträge", 
      value: userInfo?.stats.auftraege.toString() || "0", 
      color: "bg-purple-500" 
    },
    { 
      icon: Wrench, 
      label: "Status", 
      value: userInfo?.stats.auftraege > 0 ? "Aktiv" : "-", 
      color: "bg-yellow-500" 
    },
  ];

  return (
    <div className="flex min-h-screen bg-slate-950">
      <Sidebar />
      
      <div className="flex-1 ml-64 p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Willkommen zurück{userInfo?.user.name ? `, ${userInfo.user.name}` : ""}!
          </h1>
          <p className="text-gray-400">
            {userInfo?.user.email || "Hier ist ein Überblick über Ihr Fahrzeugservice-Management"}
          </p>
        </div>

        {/* Loading */}
        {loading && (
          <div className="text-center text-gray-400 py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          </div>
        )}

        {/* Stats Grid */}
        {!loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-slate-900 border border-slate-700 rounded-xl p-6 hover:border-slate-600 transition-all"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon size={24} className="text-white" />
                  </div>
                  <span className="text-3xl font-bold text-white">{stat.value}</span>
                </div>
                <p className="text-gray-400 font-medium">{stat.label}</p>
              </motion.div>
            );
          })}
        </div>
        )}

        {/* Quick Actions */}
        {!loading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-slate-900 border border-slate-700 rounded-xl p-6"
          >
            <h2 className="text-xl font-bold text-white mb-4">Letzte Aktivitäten</h2>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-3 p-3 bg-slate-800 rounded-lg">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-white text-sm">Auftrag #{1000 + i} aktualisiert</p>
                    <p className="text-gray-500 text-xs">vor {i} Stunden</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-slate-900 border border-slate-700 rounded-xl p-6"
          >
            <h2 className="text-xl font-bold text-white mb-4">Schnellzugriff</h2>
            <div className="space-y-3">
              <button 
                onClick={() => navigate("/neuer-auftrag")}
                className="w-full text-left p-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition text-white font-medium"
              >
                + Neuen Auftrag erstellen
              </button>
              <button 
                onClick={() => navigate("/auftrag/schadensmeldung")}
                className="w-full text-left p-3 bg-slate-800 hover:bg-slate-700 rounded-lg transition text-white font-medium"
              >
                Schadensmeldung einreichen
              </button>
              <button 
                onClick={() => navigate("/chat")}
                className="w-full text-left p-3 bg-slate-800 hover:bg-slate-700 rounded-lg transition text-white font-medium"
              >
                Chat öffnen
              </button>
            </div>
          </motion.div>
        </div>
        )}
      </div>
    </div>
  );
}
