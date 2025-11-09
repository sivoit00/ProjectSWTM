import Sidebar from '../components/Sidebar';

export default function Schadensmeldung() {
  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar />
      
      <div className="flex-1 overflow-auto p-8">
        <h1 className="text-white text-3xl font-bold mb-6">Schadensmeldung einreichen</h1>
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 max-w-2xl">
          <form className="space-y-4">
            <div>
              <label className="text-white block mb-2">Fahrzeug auswählen</label>
              <select className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>Bitte wählen...</option>
              </select>
            </div>
            
            <div>
              <label className="text-white block mb-2">Schadensbeschreibung</label>
              <textarea
                className="w-full bg-gray-700 border border-gray-600 text-white placeholder-gray-400 rounded-lg px-4 py-3 h-32 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Beschreiben Sie den Schaden..."
              />
            </div>
            
            <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg transition-all">
              Schadensmeldung absenden
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
