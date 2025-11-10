import { useState } from "react";
import { Send } from "lucide-react";
import { api } from "../services/api";
import keycloak from "../keycloak";

type Message = { sender: "User" | "Bot"; text: string };

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMessage = input.trim();
    setMessages((prev) => [...prev, { sender: "User", text: userMessage }]);
    setInput("");

    try {
      const res = await api.sendToOpenAI({ message: userMessage });
      const answer = res.data?.response ?? "Keine Antwort erhalten";
      setMessages((prev) => [...prev, { sender: "Bot", text: answer }]);
    } catch (err) {
      console.error("OpenAI error:", err);
      setMessages((prev) => [
        ...prev,
        { sender: "Bot", text: "Fehler beim Abrufen der Antwort" },
      ]);
    }
  };

  return (
    <div className="flex h-screen text-white bg-linear-to-br from-slate-900 via-slate-800 to-slate-900 overflow-hidden">
      {/* Linke Seite: Chat */}
      <div className="w-full md:w-1/2 flex flex-col border-r border-white/10 backdrop-blur-xl bg-white/5">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <h1 className="text-xl font-semibold">💬 Clone</h1>
          <button
            onClick={() => keycloak.logout()}
            className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded-md shadow transition"
          >
            Logout
          </button>
        </div>

        {/* Nachrichtenverlauf */}
        <div className="flex-1 p-6 space-y-3 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${
                msg.sender === "User" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`px-4 py-2 rounded-2xl max-w-[75%] shadow-md ${
                  msg.sender === "User"
                    ? "bg-blue-600 text-white rounded-br-none"
                    : "bg-white/10 text-gray-200 rounded-bl-none"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
        </div>

        {/* Eingabe */}
        <div className="flex items-center gap-3 p-4 border-t border-white/10 bg-white/5">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Nachricht eingeben..."
            className="flex-1 px-4 py-2 text-white placeholder-gray-400 rounded-xl border border-white/20 bg-white/10 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSend}
            className="p-2 bg-blue-600 rounded-xl shadow-md hover:bg-blue-700 transition"
          >
            <Send size={20} />
          </button>
        </div>
      </div>

      {/* Rechte Seite: Visualisierung */}
      <div className="hidden md:flex w-1/2 items-center justify-center border-l border-white/10 backdrop-blur-xl bg-white/5">
        <div className="relative w-[600px] h-[600px] bg-white/5 rounded-xl border border-white/10">
          <svg width="100%" height="100%" className="text-white">
            {/* --- Pfeilspitzen-Definition --- */}
            <defs>
              <marker
                id="arrow"
                markerWidth="10"
                markerHeight="10"
                refX="6"
                refY="3"
                orient="auto"
                fill="white"
              >
                <path d="M0,0 L0,6 L9,3 z" />
              </marker>
            </defs>

            {/* --- Positionen der Entitäten --- */}
            {/* Mitte */}
            <circle cx="300" cy="300" r="35" fill="#3b82f6" />
            <text
              x="300"
              y="305"
              textAnchor="middle"
              fill="white"
              fontSize="12"
            >
              AI Chatbot
            </text>

            {/* Oben */}
            <circle cx="300" cy="120" r="30" fill="#6366f1" />
            <text
              x="300"
              y="125"
              textAnchor="middle"
              fill="white"
              fontSize="12"
            >
              Versicherung
            </text>

            {/* Rechts oben */}
            <circle cx="480" cy="180" r="30" fill="#f97316" />
            <text
              x="480"
              y="185"
              textAnchor="middle"
              fill="white"
              fontSize="12"
            >
              Rechtsanwalt
            </text>

            {/* Links oben */}
            <circle cx="120" cy="180" r="30" fill="#10b981" />
            <text
              x="120"
              y="185"
              textAnchor="middle"
              fill="white"
              fontSize="12"
            >
              Server
            </text>

            {/* Rechts unten */}
            <circle cx="460" cy="420" r="30" fill="#eab308" />
            <text
              x="460"
              y="425"
              textAnchor="middle"
              fill="white"
              fontSize="12"
            >
              SQL DB
            </text>

            {/* Links unten */}
            <circle cx="140" cy="420" r="30" fill="#84cc16" />
            <text
              x="140"
              y="425"
              textAnchor="middle"
              fill="white"
              fontSize="12"
            >
              Werkstatt
            </text>

            {/* Unten Mitte (unterhalb AI Chatbot) */}
            <circle cx="300" cy="520" r="25" fill="#ef4444" />
            <text
              x="300"
              y="525"
              textAnchor="middle"
              fill="white"
              fontSize="12"
            >
              GuardRails
            </text>

            {/* --- Verbindungen --- */}
            {/* AI Chatbot zu allen */}
            <line
              x1="300"
              y1="265"
              x2="300"
              y2="150"
              stroke="white"
              strokeWidth="2"
              markerEnd="url(#arrow)"
            />
            <line
              x1="330"
              y1="280"
              x2="450"
              y2="190"
              stroke="white"
              strokeWidth="2"
              markerEnd="url(#arrow)"
            />
            <line
              x1="270"
              y1="280"
              x2="150"
              y2="190"
              stroke="white"
              strokeWidth="2"
              markerEnd="url(#arrow)"
            />
            <line
              x1="330"
              y1="320"
              x2="440"
              y2="410"
              stroke="white"
              strokeWidth="2"
              markerEnd="url(#arrow)"
            />
            <line
              x1="270"
              y1="320"
              x2="160"
              y2="410"
              stroke="white"
              strokeWidth="2"
              markerEnd="url(#arrow)"
            />
            <line
              x1="300"
              y1="335"
              x2="300"
              y2="495"
              stroke="white"
              strokeWidth="2"
              markerEnd="url(#arrow)"
            />

            {/* Versicherung → Server, Rechtsanwalt, SQL */}
            <line
              x1="280"
              y1="140"
              x2="150"
              y2="170"
              stroke="white"
              strokeWidth="1.5"
              markerEnd="url(#arrow)"
            />
            <line
              x1="320"
              y1="140"
              x2="460"
              y2="170"
              stroke="white"
              strokeWidth="1.5"
              markerEnd="url(#arrow)"
            />
            <line
              x1="310"
              y1="140"
              x2="450"
              y2="400"
              stroke="white"
              strokeWidth="1.5"
              markerEnd="url(#arrow)"
            />

            {/* Server → SQL */}
            <line
              x1="135"
              y1="200"
              x2="450"
              y2="400"
              stroke="white"
              strokeWidth="1.5"
              markerEnd="url(#arrow)"
            />

            {/* Rechtsanwalt → Werkstatt */}
            <line
              x1="470"
              y1="200"
              x2="160"
              y2="410"
              stroke="white"
              strokeWidth="1.5"
              markerEnd="url(#arrow)"
            />

            {/* SQL → Werkstatt & GuardRails */}
            <line
              x1="440"
              y1="420"
              x2="170"
              y2="420"
              stroke="white"
              strokeWidth="1.5"
              markerEnd="url(#arrow)"
            />
            <line
              x1="460"
              y1="440"
              x2="300"
              y2="510"
              stroke="white"
              strokeWidth="1.5"
              markerEnd="url(#arrow)"
            />

            {/* GuardRails → Werkstatt */}
            <line
              x1="280"
              y1="510"
              x2="150"
              y2="430"
              stroke="white"
              strokeWidth="1.5"
              markerEnd="url(#arrow)"
            />
          </svg>

          <div className="absolute bottom-3 w-full text-center text-sm text-gray-300">
            <p>Platzhalter-Diagramm: KI-Agenten & Datenflüsse (Stand Sprint 1)</p>
          </div>
        </div>
      </div>
    </div>
  );
}