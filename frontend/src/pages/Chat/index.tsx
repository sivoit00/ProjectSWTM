import { useState, useEffect } from "react";
import { Send, Paperclip, X, FileText, Image as ImageIcon } from "lucide-react";
import { api } from "../../services/api";
import Visualization from "../../components/common/Visualization";
import FileUpload from "../../components/common/FileUpload";
import keycloak from "../../keycloak";

type Message = { sender: "User" | "Bot"; text: string; files?: string[] };

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const userId = keycloak.tokenParsed?.sub || "anonymous";

  // Load chat history on mount
  useEffect(() => {
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    try {
      const response = await api.chat.getHistory(userId);
      const history = response.data.messages.map((msg: any) => ({
        sender: msg.sender as "User" | "Bot",
        text: msg.message,
      }));
      setMessages(history);
    } catch (error) {
      console.error("Failed to load chat history:", error);
    }
  };

  const saveMessageToHistory = async (sender: "User" | "Bot", message: string) => {
    try {
      await api.chat.saveMessage({
        user_id: userId,
        sender,
        message,
      });
    } catch (error) {
      console.error("Failed to save message:", error);
    }
  };

  const handleSend = async () => {
    if ((!input.trim() && selectedFiles.length === 0) || loading) return;

    const userMessage = input.trim();
    let uploadedFileNames: string[] = [];

    setLoading(true);

    try {
      // Upload files first if any
      if (selectedFiles.length > 0) {
        const uploadResponse = await api.files.upload(selectedFiles);
        uploadedFileNames = uploadResponse.data.files.map((f: any) => f.stored_filename);
        setSelectedFiles([]);
        setShowFileUpload(false);
      }

      // Add user message to UI
      const messageText = userMessage || `[${selectedFiles.length} file(s) uploaded]`;
      setMessages((prev) => [...prev, { sender: "User", text: messageText, files: uploadedFileNames }]);
      setInput("");

      // Save user message to history
      await saveMessageToHistory("User", messageText);

      // Send message to AI
      const res = await api.chat.sendMessage({ message: userMessage });
      const answer = res.data?.response ?? "No response received";
      
      // Add bot response to UI
      setMessages((prev) => [...prev, { sender: "Bot", text: answer }]);
      
      // Save bot response to history
      await saveMessageToHistory("Bot", answer);
    } catch (err) {
      console.error("Chat error:", err);
      const errorMsg = "Sorry, I encountered an error. Please try again.";
      setMessages((prev) => [...prev, { sender: "Bot", text: errorMsg }]);
      await saveMessageToHistory("Bot", errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen">
      {/* Chat Area - 60% width */}
      <div className="w-3/5 flex flex-col border-r border-gray-700">
        {/* Header */}
        <div className="p-4 border-b border-gray-700 bg-gray-800">
          <h2 className="text-xl font-bold text-white">AI Chat</h2>
          <p className="text-sm text-gray-400">Chat with our AI to manage your vehicle services effortlessly</p>
        </div>

        {/* Messages */}
        <div className="flex-1 p-6 space-y-4 overflow-y-auto bg-gray-900">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
              <p className="text-6xl mb-4">💬</p>
              <h3 className="text-2xl font-bold text-white mb-2">Welcome to AI Assistant</h3>
              <p className="text-lg">Ask me anything about vehicle services, and I'll help you!</p>
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
                
                {/* Display uploaded files */}
                {msg.files && msg.files.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {msg.files.map((filename, idx) => {
                      const fileUrl = api.files.getFileUrl(filename);
                      const isPdf = filename.toLowerCase().endsWith('.pdf');
                      const isImage = /\.(jpg|jpeg|png|gif|bmp)$/i.test(filename);
                      
                      return (
                        <a
                          key={idx}
                          href={fileUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={`flex items-center gap-2 p-2 rounded-lg text-xs ${
                            msg.sender === "User"
                              ? "bg-blue-700 hover:bg-blue-800"
                              : "bg-gray-700 hover:bg-gray-600"
                          }`}
                        >
                          {isPdf && <FileText size={16} />}
                          {isImage && <ImageIcon size={16} />}
                          <span className="truncate">{filename}</span>
                        </a>
                      );
                    })}
                  </div>
                )}
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

        {/* Input Area */}
        <div className="p-4 border-t border-gray-700 bg-gray-800">
          <div className="flex gap-2 mb-3 flex-wrap">
            <button
              onClick={() => setInput("Schedule a service appointment")}
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg hover:border-blue-500 hover:bg-gray-600 transition-all text-sm text-gray-300"
            >
              <span className="text-lg">📅</span> Schedule Service
            </button>
            <button
              onClick={() => setInput("Check service history")}
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg hover:border-blue-500 hover:bg-gray-600 transition-all text-sm text-gray-300"
            >
              <span className="text-lg">📋</span> Service History
            </button>
            <button
              onClick={() => setInput("Find nearby workshops")}
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg hover:border-blue-500 hover:bg-gray-600 transition-all text-sm text-gray-300"
            >
              <span className="text-lg">🔍</span> Find Workshops
            </button>
          </div>

          {/* File Upload Area */}
          {showFileUpload && (
            <div className="mb-3 p-4 bg-gray-900 rounded-lg border border-gray-700">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-white">Upload Files</h3>
                <button
                  onClick={() => {
                    setShowFileUpload(false);
                    setSelectedFiles([]);
                  }}
                  className="text-gray-400 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>
              <FileUpload onFilesSelected={setSelectedFiles} />
            </div>
          )}

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowFileUpload(!showFileUpload)}
              className={`p-3 rounded-xl transition-colors ${
                showFileUpload
                  ? "bg-blue-600 text-white"
                  : "bg-gray-700 text-gray-300 hover:bg-gray-600"
              }`}
            >
              <Paperclip size={20} />
            </button>
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
              disabled={loading || (!input.trim() && selectedFiles.length === 0)}
              className="p-3 bg-blue-600 rounded-xl shadow-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Visualization - 40% width */}
      <div className="w-2/5">
        <Visualization />
      </div>
    </div>
  );
}
