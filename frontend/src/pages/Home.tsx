import { useState } from "react";
import { Send } from "lucide-react";
import { api } from "../services/api";
import keycloak from "../keycloak";
import Visualization from "../components/Visualization";


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
      <Visualization/>
    </div>
  );
}
