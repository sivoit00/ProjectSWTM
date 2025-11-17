import { useState } from "react";
import { Send } from "lucide-react";
import { api } from "../../services/api";

type Message = { sender: "User" | "Bot"; text: string };

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setMessages((prev) => [...prev, { sender: "User", text: userMessage }]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.chat.sendMessage({ message: userMessage });
      const answer = res.data?.response ?? "No response received";
      setMessages((prev) => [...prev, { sender: "Bot", text: answer }]);
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [
        ...prev,
        { sender: "Bot", text: "Sorry, I encountered an error. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      <div className="flex items-center justify-between p-4 bg-gray-800 border-b border-gray-700">
        <div>
          <h1 className="text-xl font-bold">Tom's Clone</h1>
          <p className="text-sm text-gray-400">Chat with our AI to manage your vehicle services</p>
        </div>
      </div>

      <div className="flex-1 p-6 space-y-4 overflow-y-auto bg-gray-900">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-12">
            <p className="text-6xl mb-4">💬</p>
            <h3 className="text-2xl font-bold text-white mb-2">Welcome to AI Assistant</h3>
            <p className="text-lg mb-8">Ask me anything about vehicle services, and I'll help you!</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.sender === "User" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`px-4 py-3 rounded-2xl max-w-[70%] shadow-md ${
                msg.sender === "User"
                  ? "bg-blue-600 text-white rounded-br-none"
                  : "bg-gray-800 text-gray-200 rounded-bl-none border border-gray-700"
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 border border-gray-700 px-4 py-3 rounded-2xl rounded-bl-none">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 bg-gray-800 border-t border-gray-700">
        <div className="flex gap-2 mb-3">
          <button
            onClick={() => setInput("Schedule a service appointment")}
            className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg hover:border-blue-500 hover:bg-gray-600 transition-all text-sm text-gray-300"
          >
            📅 Schedule Service
          </button>
          <button
            onClick={() => setInput("Check service history")}
            className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg hover:border-blue-500 hover:bg-gray-600 transition-all text-sm text-gray-300"
          >
            📋 Service History
          </button>
          <button
            onClick={() => setInput("Find nearby workshops")}
            className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg hover:border-blue-500 hover:bg-gray-600 transition-all text-sm text-gray-300"
          >
            🔍 Find Workshops
          </button>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Type your message..."
            disabled={loading}
            className="flex-1 px-4 py-3 text-white placeholder-gray-400 rounded-xl border border-gray-600 bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="p-3 bg-blue-600 rounded-xl shadow-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}
