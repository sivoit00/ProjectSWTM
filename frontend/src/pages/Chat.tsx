import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import { Send } from 'lucide-react';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'support';
  time: string;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: 'Hallo! Wie kann ich Ihnen heute helfen?',
      sender: 'support',
        time: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');

  const sendMessage = () => {
    if (inputMessage.trim()) {
      const newMessage: Message = {
        id: messages.length + 1,
        text: inputMessage,
        sender: 'user',
        time: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
      };
      setMessages([...messages, newMessage]);
      setInputMessage('');
      
      // Simulate support response
      setTimeout(() => {
        const supportMessage: Message = {
          id: messages.length + 2,
          text: 'Danke für Ihre Nachricht. Unser Support-Team wird sich in Kürze bei Ihnen melden.',
          sender: 'support',
          time: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
        };
        setMessages(prev => [...prev, supportMessage]);
      }, 1000);
    }
  };

  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar />
      
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="bg-gray-800 border-b border-gray-700 p-6">
          <h1 className="text-white text-3xl font-bold">Chat Support</h1>
          <p className="text-gray-400">Stellen Sie Ihre Fragen zum Fahrzeugservice</p>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-900">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-md px-6 py-4 rounded-2xl ${
                  message.sender === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-white border border-gray-700'
                }`}
              >
                <p className="text-sm">{message.text}</p>
                <p className="text-xs mt-2 opacity-70">{message.time}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Input Area */}
        <div className="bg-gray-800 border-t border-gray-700 p-6">
          <div className="flex gap-3">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Schreiben Sie eine Nachricht..."
              className="flex-1 bg-gray-700 border border-gray-600 text-white placeholder-gray-400 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={sendMessage}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg transition-all flex items-center gap-2"
            >
              <Send size={20} />
              Senden
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
