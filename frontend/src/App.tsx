import { Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";
import Schadensmeldung from "./pages/Schadensmeldung";
import Auftraege from "./pages/Auftraege";
import Visualisierung from "./pages/Visualisierung";
import NeuerAuftrag from "./pages/NeuerAuftrag";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/chat" element={<Chat />} />
      <Route path="/schadensmeldung" element={<Schadensmeldung />} />
      <Route path="/auftraege" element={<Auftraege />} />
      <Route path="/visualisierung" element={<Visualisierung />} />
      <Route path="/neuer-auftrag" element={<NeuerAuftrag />} />
    </Routes>
  );
}
