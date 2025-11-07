import { useState } from "react";
import { motion } from "framer-motion";
import { Upload, Send } from "lucide-react";
import Sidebar from "../components/Sidebar";

export default function Schadensmeldung() {
  const [formData, setFormData] = useState({
    fahrzeugKennzeichen: "",
    beschreibung: "",
    schadensort: "",
    datum: "",
  });
  const [files, setFiles] = useState<File[]>([]);
  const [submitted, setSubmitted] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // TODO: API Call zum Backend
    console.log("Schadensmeldung:", formData, files);
    
    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      setFormData({
        fahrzeugKennzeichen: "",
        beschreibung: "",
        schadensort: "",
        datum: "",
      });
      setFiles([]);
    }, 3000);
  };

  return (
    <div className="flex min-h-screen bg-slate-950">
      <Sidebar />

      <div className="flex-1 ml-64 p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Schadensmeldung</h1>
          <p className="text-gray-400">Melden Sie Fahrzeugschäden schnell und einfach</p>
        </div>

        {/* Success Message */}
        {submitted && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-green-500/20 border border-green-500 rounded-lg text-green-300"
          >
            ✓ Schadensmeldung erfolgreich eingereicht!
          </motion.div>
        )}

        {/* Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-slate-900 border border-slate-700 rounded-xl p-8"
        >
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Fahrzeug Kennzeichen */}
            <div>
              <label className="block text-white font-medium mb-2">
                Fahrzeugkennzeichen *
              </label>
              <input
                type="text"
                name="fahrzeugKennzeichen"
                value={formData.fahrzeugKennzeichen}
                onChange={handleInputChange}
                required
                placeholder="z.B. B-AB 1234"
                className="w-full px-4 py-3 bg-slate-800 text-white border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Schadensort */}
            <div>
              <label className="block text-white font-medium mb-2">
                Schadensort *
              </label>
              <input
                type="text"
                name="schadensort"
                value={formData.schadensort}
                onChange={handleInputChange}
                required
                placeholder="z.B. Parkplatz Hauptstraße 5"
                className="w-full px-4 py-3 bg-slate-800 text-white border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Datum */}
            <div>
              <label className="block text-white font-medium mb-2">
                Schadendatum *
              </label>
              <input
                type="date"
                name="datum"
                value={formData.datum}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-3 bg-slate-800 text-white border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Beschreibung */}
            <div>
              <label className="block text-white font-medium mb-2">
                Schadensbeschreibung *
              </label>
              <textarea
                name="beschreibung"
                value={formData.beschreibung}
                onChange={handleInputChange}
                required
                rows={6}
                placeholder="Beschreiben Sie den Schaden ausführlich..."
                className="w-full px-4 py-3 bg-slate-800 text-white border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              />
            </div>

            {/* File Upload */}
            <div>
              <label className="block text-white font-medium mb-2">
                Fotos hochladen (optional)
              </label>
              <div className="border-2 border-dashed border-slate-700 rounded-lg p-6 text-center hover:border-blue-500 transition">
                <Upload size={40} className="mx-auto text-gray-400 mb-2" />
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="text-blue-400 hover:text-blue-300 cursor-pointer font-medium"
                >
                  Dateien auswählen
                </label>
                <p className="text-gray-500 text-sm mt-1">oder per Drag & Drop</p>
              </div>
              {files.length > 0 && (
                <div className="mt-3 space-y-2">
                  {files.map((file, index) => (
                    <div key={index} className="flex items-center gap-2 text-gray-300 text-sm">
                      <span>📷</span>
                      <span>{file.name}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Submit Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg flex items-center justify-center gap-2 transition"
            >
              <Send size={20} />
              Schadensmeldung einreichen
            </motion.button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
