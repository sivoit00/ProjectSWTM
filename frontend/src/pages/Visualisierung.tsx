import Sidebar from '../components/Sidebar';
import { BarChart3 } from 'lucide-react';

export default function Visualisierung() {
  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar />
      
      <div className="flex-1 overflow-auto p-8">
        <h1 className="text-white text-3xl font-bold mb-6">Visualisierung</h1>
        
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 text-center">
          <BarChart3 className="text-blue-500 mx-auto mb-4" size={64} />
          <h2 className="text-white text-xl mb-2">Statistiken & Berichte</h2>
          <p className="text-gray-400">Hier werden bald Ihre Statistiken angezeigt</p>
        </div>
      </div>
    </div>
  );
}
