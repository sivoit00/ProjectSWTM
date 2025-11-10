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

          {(() => {
            type Node = {
              x: number;
              y: number;
              w: number;
              h: number;
              color: string;
              label: string;
            };

            const nodes = {
              versicherung: { x: 300, y: 120, w: 140, h: 50, color: "#D46A29", label: "Versicherung" },
              chatbot:      { x: 300, y: 300, w: 140, h: 50, color: "#D22DD8", label: "AI Chatbot" },
              guard:        { x: 300, y: 520, w: 140, h: 50, color: "#0A4BFF", label: "GuardRails" },
              server:       { x: 120, y: 200, w: 140, h: 50, color: "#26B6C6", label: "Server" },
              sql:          { x: 140, y: 420, w: 140, h: 50, color: "#E6C62F", label: "SQL Datenbank" },
              anwalt:       { x: 480, y: 200, w: 140, h: 50, color: "#3EC764", label: "Rechtsanwalt" },
              werkstatt:    { x: 460, y: 420, w: 140, h: 50, color: "#A237E0", label: "Werkstatt" },
            };

            type NodeKey = keyof typeof nodes;

            const edges: [NodeKey, NodeKey][] = [
              ["versicherung", "chatbot"],
              ["chatbot", "guard"],
              ["chatbot", "server"],
              ["chatbot", "anwalt"],
              ["chatbot", "werkstatt"],
              ["chatbot", "sql"],
              ["versicherung", "server"],
              ["versicherung", "anwalt"],
              ["versicherung", "sql"],
              ["server", "sql"],
              ["sql", "werkstatt"],
              ["sql", "guard"],
              ["guard", "werkstatt"],
              ["werkstatt", "anwalt"],
            ];

            function edgePoint(a: Node, b: Node) {
              const dx = b.x - a.x;
              const dy = b.y - a.y;
              const w = a.w / 2;
              const h = a.h / 2;
              const scale = Math.max(Math.abs(dx) / w, Math.abs(dy) / h);
              return { x: a.x + dx / scale, y: a.y + dy / scale };
            }

            return (
              <svg width="100%" height="100%">
                {edges.map(([a, b], i) => {
                  const A = nodes[a];
                  const B = nodes[b];
                  const p1 = edgePoint(A, B);
                  const p2 = edgePoint(B, A);
                  return (
                    <line
                      key={i}
                      x1={p1.x}
                      y1={p1.y}
                      x2={p2.x}
                      y2={p2.y}
                      stroke="#85D4E6"
                      strokeWidth="3"
                      strokeDasharray="6 6"
                    />
                  );
                })}

                {Object.values(nodes).map((n, i) => (
                  <g key={i}>
                    <rect
                      x={n.x - n.w / 2}
                      y={n.y - n.h / 2}
                      width={n.w}
                      height={n.h}
                      rx="12"
                      fill={n.color}
                    />
                    <text x={n.x} y={n.y + 4} textAnchor="middle" fontSize="14" fill="white">
                      {n.label}
                    </text>
                  </g>
                ))}
              </svg>
            );
          })()}

          <div className="absolute bottom-3 w-full text-center text-sm text-gray-300">
            KI-System-Modulübersicht (Sprint 1)
          </div>
        </div>
      </div>

    </div>
  );
}
