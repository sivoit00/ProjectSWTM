import { useState } from "react";
import { motion } from "framer-motion";
import { Send } from "lucide-react";

export default function App() {
  const [messages, setMessages] = useState([
    { sender: "Bot", text: "👋 Willkommen!" },
    { sender: "Bot", text: "Wie kann ich dir helfen?" },
    { sender: "User", text: "Mein Auto ist kaputt!" },
  ]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages((prev) => [...prev, { sender: "User", text: input }]);
    setInput("");
  };

  return (
    <div className="flex h-screen bg-linear-to-br from-slate-900 via-slate-800 to-slate-900 text-white overflow-hidden">
      {/* Chatbereich */}
      <motion.div
        initial={{ x: -40, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="w-full md:w-1/2 flex flex-col border-r border-white/10 backdrop-blur-xl bg-white/5"
      >
        {/* Header */}
        <div className="p-4 border-b border-white/10 flex items-center justify-between">
          <h1 className="text-xl font-semibold">💬 Tom</h1>
        </div>

        {/* Nachrichtenverlauf */}
        <div className="flex-1 overflow-y-auto p-6 space-y-3 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
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
            </motion.div>
          ))}
        </div>

        {/* Eingabe */}
        <div className="p-4 border-t border-white/10 bg-white/5 flex gap-3 items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Nachricht eingeben..."
            className="flex-1 bg-white/10 text-white placeholder-gray-400 px-4 py-2 rounded-xl outline-none border border-white/20 focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSend}
            className="bg-blue-600 hover:bg-blue-700 p-2 rounded-xl shadow-md transition"
          >
            <Send size={20} />
          </button>
        </div>
      </motion.div>

      {/* Rechte Seite: Visualisierung */}
      <motion.div
        initial={{ x: 40, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="hidden md:flex w-1/2 items-center justify-center bg-white/5 backdrop-blur-xl border-l border-white/10"
      >
        <div className="text-center">
          <p className="text-4xl font-light mb-2">📊</p>
          <h2 className="text-2xl font-semibold mb-1">Visualisierung</h2>
        </div>
      </motion.div>
    </div>
  );
}
