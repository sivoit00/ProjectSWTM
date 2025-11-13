import { useState } from "react";
import { Send, Menu, X, FileText, Upload, Trash2, Car } from "lucide-react";
import { api } from "../services/api";
import type { Rechtsanwalt, Versicherung } from "../services/api";
import keycloak from "../keycloak";
import Visualization from "../components/Visualization";


type Message = { sender: "User" | "Bot"; text: string };

type ProfileData = {
  lawyer?: Rechtsanwalt;
  insurance?: Versicherung & { files: File[] };
  workshop?: { name: string; adresse: string; plz: string; ort: string };
  vehicle?: { marke: string; modell: string; baujahr: number; files: File[] };
};

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [currentCategory, setCurrentCategory] = useState<"lawyer" | "insurance" | "workshop" | "vehicle" | null>(null);
  const [profileData, setProfileData] = useState<ProfileData>({});
  
  // Formularfelder - Generic
  const [tempFiles, setTempFiles] = useState<File[]>([]);
  
  // Rechtsanwalt
  const [lawyerForm, setLawyerForm] = useState({
    name: "",
    kanzlei: "",
    adresse: "",
    plz: "",
    ort: "",
    telefon: "",
    email: ""
  });

  // Versicherung
  const [insuranceForm, setInsuranceForm] = useState({
    versicherungsname: "",
    versicherungsnummer: "",
    art: "",
    ansprechpartner: "",
    telefon: "",
    email: ""
  });

  // Werkstatt
  const [workshopForm, setWorkshopForm] = useState({
    name: "",
    adresse: "",
    plz: "",
    ort: ""
  });

  // Fahrzeug
  const [vehicleForm, setVehicleForm] = useState({
    marke: "",
    modell: "",
    baujahr: ""
  });

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

  const openModal = (category: "lawyer" | "insurance" | "workshop" | "vehicle") => {
    setCurrentCategory(category);
    const existing = profileData[category];
    
    if (category === "lawyer" && existing) {
      setLawyerForm(existing as Rechtsanwalt);
    } else if (category === "insurance" && existing) {
      const ins = existing as Versicherung & { files: File[] };
      setInsuranceForm({
        versicherungsname: ins.versicherungsname,
        versicherungsnummer: ins.versicherungsnummer,
        art: ins.art,
        ansprechpartner: ins.ansprechpartner,
        telefon: ins.telefon,
        email: ins.email
      });
      setTempFiles(ins.files || []);
    } else if (category === "workshop" && existing) {
      setWorkshopForm(existing as any);
    } else if (category === "vehicle" && existing) {
      const veh = existing as any;
      setVehicleForm({
        marke: veh.marke || "",
        modell: veh.modell || "",
        baujahr: veh.baujahr?.toString() || ""
      });
      setTempFiles(veh.files || []);
    }
    
    setModalOpen(true);
  };

  const saveData = async () => {
    if (!currentCategory) return;
  
    try {
      if (currentCategory === "lawyer") {
        await api.createRechtsanwalt(lawyerForm);
        setProfileData((prev) => ({
          ...prev,
          lawyer: lawyerForm
        }));
        alert("Rechtsanwalt erfolgreich gespeichert!");
      } else if (currentCategory === "insurance") {
        await api.createVersicherung(insuranceForm);
        setProfileData((prev) => ({
          ...prev,
          insurance: { ...insuranceForm, files: tempFiles }
        }));
        alert("Versicherung erfolgreich gespeichert!");
      } else if (currentCategory === "workshop") {
        const werkstattData = {
          name: workshopForm.name,
          adresse: workshopForm.adresse,
          plz: workshopForm.plz,
          ort: workshopForm.ort
        };
        
        await api.createWerkstatt(werkstattData);
        
        setProfileData((prev) => ({
          ...prev,
          workshop: workshopForm
        }));
        
        alert("Werkstatt erfolgreich gespeichert!");
      } else if (currentCategory === "vehicle") {
        const fahrzeugData = {
          marke: vehicleForm.marke,
          modell: vehicleForm.modell,
          baujahr: parseInt(vehicleForm.baujahr),
          kunde_id: 1 // TODO: Echte Kunden-ID verwenden
        };
        
        await api.createFahrzeug(fahrzeugData);
        
        setProfileData((prev) => ({
          ...prev,
          vehicle: { 
            marke: vehicleForm.marke, 
            modell: vehicleForm.modell, 
            baujahr: parseInt(vehicleForm.baujahr),
            files: tempFiles 
          },
        }));
        
        alert("Fahrzeug erfolgreich gespeichert!");
      }
      
      closeModal();
    } catch (error) {
      console.error("Fehler beim Speichern:", error);
      alert("Fehler beim Speichern der Daten!");
    }
  };
  

  const closeModal = () => {
    setModalOpen(false);
    setCurrentCategory(null);
    setLawyerForm({ name: "", kanzlei: "", adresse: "", plz: "", ort: "", telefon: "", email: "" });
    setInsuranceForm({ versicherungsname: "", versicherungsnummer: "", art: "", ansprechpartner: "", telefon: "", email: "" });
    setWorkshopForm({ name: "", adresse: "", plz: "", ort: "" });
    setVehicleForm({ marke: "", modell: "", baujahr: "" });
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

  const handleFormChange = (category: string, field: string, value: string) => {
    if (category === "lawyer") {
      setLawyerForm(prev => ({ ...prev, [field]: value }));
    } else if (category === "insurance") {
      setInsuranceForm(prev => ({ ...prev, [field]: value }));
    } else if (category === "workshop") {
      setWorkshopForm(prev => ({ ...prev, [field]: value }));
    } else if (category === "vehicle") {
      setVehicleForm(prev => ({ ...prev, [field]: value }));
    }
  };

  const categoryLabels = {
    lawyer: "Bevorzugter Rechtsanwalt",
    insurance: "Abgeschlossene Versicherung",
    workshop: "Bevorzugte Werkstatt",
    vehicle: "Mein Fahrzeug",
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
          {(["lawyer", "insurance", "workshop", "vehicle"] as const).map((cat) => (
            <button
              key={cat}
              onClick={() => openModal(cat)}
              className="w-full flex items-center gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition border border-white/10"
            >
              {cat === "vehicle" ? <Car size={18} /> : <FileText size={18} />}
              <div className="flex-1 text-left">
                <p className="text-sm font-medium">{categoryLabels[cat]}</p>
                {cat === "vehicle" && profileData.vehicle ? (
                  <p className="text-xs text-gray-400 truncate">
                    {profileData.vehicle.marke} {profileData.vehicle.modell}
                  </p>
                ) : cat === "lawyer" && profileData.lawyer ? (
                  <p className="text-xs text-gray-400 truncate">{profileData.lawyer.name}</p>
                ) : cat === "insurance" && profileData.insurance ? (
                  <p className="text-xs text-gray-400 truncate">{profileData.insurance.versicherungsname}</p>
                ) : cat === "workshop" && profileData.workshop ? (
                  <p className="text-xs text-gray-400 truncate">{profileData.workshop.name}</p>
                ) : null}
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
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-xl p-6 w-full max-w-md border border-white/10 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-semibold mb-4">{categoryLabels[currentCategory]}</h3>

            {/* Rechtsanwalt Formular */}
            {currentCategory === "lawyer" && (
              <div className="space-y-3">
                <div>
                  <label className="block text-sm mb-1">Name</label>
                  <input
                    type="text"
                    value={lawyerForm.name}
                    onChange={(e) => handleFormChange("lawyer", "name", e.target.value)}
                    placeholder="z.B. Dr. Max Müller"
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1">Kanzlei</label>
                  <input
                    type="text"
                    value={lawyerForm.kanzlei}
                    onChange={(e) => handleFormChange("lawyer", "kanzlei", e.target.value)}
                    placeholder="z.B. Müller & Partner"
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1">Adresse</label>
                  <input
                    type="text"
                    value={lawyerForm.adresse}
                    onChange={(e) => handleFormChange("lawyer", "adresse", e.target.value)}
                    placeholder="z.B. Hauptstraße 123"
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm mb-1">PLZ</label>
                    <input
                      type="text"
                      value={lawyerForm.plz}
                      onChange={(e) => handleFormChange("lawyer", "plz", e.target.value)}
                      placeholder="12345"
                      className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm mb-1">Ort</label>
                    <input
                      type="text"
                      value={lawyerForm.ort}
                      onChange={(e) => handleFormChange("lawyer", "ort", e.target.value)}
                      placeholder="Berlin"
                      className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm mb-1">Telefon</label>
                  <input
                    type="tel"
                    value={lawyerForm.telefon}
                    onChange={(e) => handleFormChange("lawyer", "telefon", e.target.value)}
                    placeholder="030 12345678"
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1">E-Mail</label>
                  <input
                    type="email"
                    value={lawyerForm.email}
                    onChange={(e) => handleFormChange("lawyer", "email", e.target.value)}
                    placeholder="kanzlei@beispiel.de"
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            )}

            {/* Versicherung Formular */}
            {currentCategory === "insurance" && (
              <div className="space-y-3">
                <div>
                  <label className="block text-sm mb-1">Versicherungsname</label>
                  <input
                    type="text"
                    value={insuranceForm.versicherungsname}
                    onChange={(e) => handleFormChange("insurance", "versicherungsname", e.target.value)}
                    placeholder="z.B. Allianz"
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1">Versicherungsnummer</label>
                  <input
                    type="text"
                    value={insuranceForm.versicherungsnummer}
                    onChange={(e) => handleFormChange("insurance", "versicherungsnummer", e.target.value)}
                    placeholder="VS-123456789"
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1">Art</label>
                  <select
                    value={insuranceForm.art}
                    onChange={(e) => handleFormChange("insurance", "art", e.target.value)}
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Bitte wählen</option>
                    <option value="Haftpflicht">Haftpflicht</option>
                    <option value="Teilkasko">Teilkasko</option>
                    <option value="Vollkasko">Vollkasko</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm mb-1">Ansprechpartner</label>
                  <input
                    type="text"
                    value={insuranceForm.ansprechpartner}
                    onChange={(e) => handleFormChange("insurance", "ansprechpartner", e.target.value)}
                    placeholder="z.B. Herr Schmidt"
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1">Telefon</label>
                  <input
                    type="tel"
                    value={insuranceForm.telefon}
                    onChange={(e) => handleFormChange("insurance", "telefon", e.target.value)}
                    placeholder="0800 123456"
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1">E-Mail</label>
                  <input
                    type="email"
                    value={insuranceForm.email}
                    onChange={(e) => handleFormChange("insurance", "email", e.target.value)}
                    placeholder="service@versicherung.de"
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Datei-Upload für Versicherung */}
                <div>
                  <label className="block text-sm mb-2">Dokumente hochladen (z.B. Versicherungsschein)</label>
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
                    <div className="space-y-2 max-h-32 overflow-y-auto">
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
                </div>
              </div>
            )}

            {/* Werkstatt Formular */}
            {currentCategory === "workshop" && (
              <div className="space-y-3">
                <div>
                  <label className="block text-sm mb-1">Name</label>
                  <input
                    type="text"
                    value={workshopForm.name}
                    onChange={(e) => handleFormChange("workshop", "name", e.target.value)}
                    placeholder="z.B. Autowerkstatt Schmidt"
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1">Adresse</label>
                  <input
                    type="text"
                    value={workshopForm.adresse}
                    onChange={(e) => handleFormChange("workshop", "adresse", e.target.value)}
                    placeholder="z.B. Industriestraße 45"
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm mb-1">PLZ</label>
                    <input
                      type="text"
                      value={workshopForm.plz}
                      onChange={(e) => handleFormChange("workshop", "plz", e.target.value)}
                      placeholder="12345"
                      className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm mb-1">Ort</label>
                    <input
                      type="text"
                      value={workshopForm.ort}
                      onChange={(e) => handleFormChange("workshop", "ort", e.target.value)}
                      placeholder="München"
                      className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Fahrzeug Formular */}
            {currentCategory === "vehicle" && (
              <div className="space-y-3">
                <div>
                  <label className="block text-sm mb-1">Marke</label>
                  <input
                    type="text"
                    value={vehicleForm.marke}
                    onChange={(e) => handleFormChange("vehicle", "marke", e.target.value)}
                    placeholder="z.B. BMW"
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1">Modell</label>
                  <input
                    type="text"
                    value={vehicleForm.modell}
                    onChange={(e) => handleFormChange("vehicle", "modell", e.target.value)}
                    placeholder="z.B. 320d"
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1">Baujahr</label>
                  <input
                    type="number"
                    value={vehicleForm.baujahr}
                    onChange={(e) => handleFormChange("vehicle", "baujahr", e.target.value)}
                    placeholder="z.B. 2020"
                    className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Datei-Upload nur bei Fahrzeug */}
                <div>
                  <label className="block text-sm mb-2">Dokumente hochladen (z.B. Fahrzeugschein)</label>
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
                    <div className="space-y-2 max-h-32 overflow-y-auto">
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
                </div>
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
      <Visualization/>
    </div>
  );
}
