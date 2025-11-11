import { useState } from 'react';
import { PageHeader } from '../../components/common';
import { chatAPI } from '../../services/api';
import { Send } from 'lucide-react';

type Message = { sender: 'User' | 'Bot'; text: string };

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setMessages((prev) => [...prev, { sender: 'User', text: userMessage }]);
    setInput('');
    setLoading(true);

    try {
      const res = await chatAPI.sendMessage({ message: userMessage });
      const answer = res.data?.response ?? 'Keine Antwort erhalten';
      setMessages((prev) => [...prev, { sender: 'Bot', text: answer }]);
    } catch (err) {
      console.error('Chat error:', err);
      setMessages((prev) => [
        ...prev,
        { sender: 'Bot', text: 'Fehler beim Abrufen der Antwort' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <PageHeader
        title="Chat Support"
        description="KI-gestützter Chat für Ihre Anfragen"
      />

      {/* Messages */}
      <div className="flex-1 p-6 space-y-4 overflow-y-auto bg-gray-900">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-12">
            <p className="text-2xl mb-2">💬</p>
            <p>Stellen Sie eine Frage, um zu beginnen</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.sender === 'User' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`px-4 py-3 rounded-2xl max-w-[70%] shadow-md ${
                msg.sender === 'User'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-gray-800 text-gray-200 rounded-bl-none border border-gray-700'
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

      {/* Input */}
      <div className="bg-gray-800 border-t border-gray-700 p-4">
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Nachricht eingeben..."
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
