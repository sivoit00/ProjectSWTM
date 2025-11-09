import { useState } from "react";
import { Send, Menu, X, FileText, Upload, Trash2 } from "lucide-react";
import { api } from "../services/api";
import keycloak from "../keycloak";

type Message = { sender: "User" | "Bot"; text: string };

type ProfileData = {
  lawyer?: { name: string; files: File[] };
  insurance?: { name: string; files: File[] };
  workshop?: { name: string; files: File[] };
};

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [currentCategory, setCurrentCategory] = useState<"lawyer" | "insurance" | "workshop" | null>(null);
  const [profileData, setProfileData] = useState<ProfileData>({});
  const [tempName, setTempName] = useState("");
  const [tempFiles, setTempFiles] = useState<File[]>([]);

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

  const openModal = (category: "lawyer" | "insurance" | "workshop") => {
    setCurrentCategory(category);
    const existing = profileData[category];
    setTempName(existing?.name || "");
    setTempFiles(existing?.files || []);
    setModalOpen(true);
  };

  const saveData = () => {
    if (currentCategory) {
      setProfileData((prev) => ({
        ...prev,
        [currentCategory]: { name: tempName, files: tempFiles },
      }));
    }
    closeModal();
  };

  const closeModal = () => {
    setModalOpen(false);
    setCurrentCategory(null);
    setTempName("");
    setTempFiles([]);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setTempFiles([...tempFiles, ...Array.from(e.target.files)]);
    }
  };

  const removeFile = (index: number) => {
    setTempFiles(tempFiles.filter((_, i) => i !== index));
  };

  const categoryLabels = {
    lawyer: "Bevorzugter Rechtsanwalt",
    insurance: "Abgeschlossene Versicherung",
    workshop: "Bevorzugte Werkstatt",
  };

  return (
    <div className="flex h-screen text-white bg-linear-to-br from-slate-900 via-slate-800 to-slate-900 overflow-hidden">
      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 h-full bg-slate-800/95 backdrop-blur-xl border-r border-white/10 z-50 transition-transform duration-300 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } w-64`}
      >
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <h2 className="text-lg font-semibold">📋 Mein Profil</h2>
          <button onClick={() => setSidebarOpen(false)} className="p-1 hover:bg-white/10 rounded">
            <X size={20} />
          </button>
        </div>

        <div className="p-4 space-y-3">
          {(["lawyer", "insurance", "workshop"] as const).map((cat) => (
            <button
              key={cat}
              onClick={() => openModal(cat)}
              className="w-full flex items-center gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition border border-white/10"
            >
              <FileText size={18} />
              <div className="flex-1 text-left">
                <p className="text-sm font-medium">{categoryLabels[cat]}</p>
                {profileData[cat]?.name && (
                  <p className="text-xs text-gray-400 truncate">{profileData[cat]?.name}</p>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Modal */}
      {modalOpen && currentCategory && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-xl p-6 w-11/12 max-w-md border border-white/10 shadow-2xl">
            <h3 className="text-xl font-semibold mb-4">{categoryLabels[currentCategory]}</h3>

            <label className="block text-sm mb-2">Name / Bezeichnung</label>
            <input
              type="text"
              value={tempName}
              onChange={(e) => setTempName(e.target.value)}
              placeholder="z.B. Müller & Partner"
              className="w-full px-4 py-2 mb-4 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <label className="block text-sm mb-2">Dokumente hochladen</label>
            <label className="flex items-center justify-center gap-2 px-4 py-2 mb-3 bg-blue-600 hover:bg-blue-700 rounded-lg cursor-pointer transition">
              <Upload size={18} />
              <span>Datei auswählen</span>
              <input
                type="file"
                multiple
                onChange={handleFileChange}
                className="hidden"
              />
            </label>

            {tempFiles.length > 0 && (
              <div className="mb-4 space-y-2 max-h-32 overflow-y-auto">
                {tempFiles.map((file, i) => (
                  <div key={i} className="flex items-center justify-between bg-white/5 p-2 rounded">
                    <span className="text-sm truncate flex-1">{file.name}</span>
                    <button onClick={() => removeFile(i)} className="p-1 hover:bg-red-600 rounded">
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="flex gap-3 mt-6">
              <button
                onClick={closeModal}
                className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg transition"
              >
                Abbrechen
              </button>
              <button
                onClick={saveData}
                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition"
              >
                Speichern
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Linke Seite: Chat */}
      <div className="w-full md:w-1/2 flex flex-col border-r border-white/10 backdrop-blur-xl bg-white/5">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 hover:bg-white/10 rounded-lg transition"
            >
              <Menu size={20} />
            </button>
            <h1 className="text-xl font-semibold">💬 Clone</h1>
          </div>
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
        <div className="text-center">
          <p className="text-4xl font-light mb-2">📊</p>
          <h2 className="text-2xl font-semibold mb-1">Visualisierung</h2>
        </div>
      </div>
    </div>
  );
}
