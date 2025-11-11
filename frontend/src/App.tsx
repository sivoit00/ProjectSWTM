import { Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import KundenPage from './pages/Kunden';
import FahrzeugePage from './pages/Fahrzeuge';
import WerkstaettenPage from './pages/Werkstaetten';
import AuftraegePage from './pages/Auftraege';
import ChatPage from './pages/Chat';

export default function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/kunden" element={<KundenPage />} />
        <Route path="/fahrzeuge" element={<FahrzeugePage />} />
        <Route path="/werkstaetten" element={<WerkstaettenPage />} />
        <Route path="/auftraege" element={<AuftraegePage />} />
        <Route path="/chat" element={<ChatPage />} />
      </Route>
    </Routes>
  );
}
