import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";
import Schadensmeldung from "./pages/Schadensmeldung";
import Auftraege from "./pages/Auftraege";
import Visualisierung from "./pages/Visualisierung";
import NeuerAuftragAuswahl from "./pages/NeuerAuftragAuswahl";
import SchadensmeldungForm from "./pages/SchadensmeldungForm";
import FahrzeugRegistrieren from "./pages/FahrzeugRegistrieren";
import VersicherungAktualisieren from "./pages/VersicherungAktualisieren";
import WerkstattTermin from "./pages/WerkstattTermin";
import SonstigerAuftrag from "./pages/SonstigerAuftrag";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/home" element={<Home />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/chat" element={<Chat />} />
      <Route path="/schadensmeldung" element={<Schadensmeldung />} />
      <Route path="/auftraege" element={<Auftraege />} />
      <Route path="/visualisierung" element={<Visualisierung />} />
      <Route path="/neuer-auftrag" element={<NeuerAuftragAuswahl />} />
      <Route path="/auftrag/schadensmeldung" element={<SchadensmeldungForm />} />
      <Route path="/auftrag/fahrzeug-registrieren" element={<FahrzeugRegistrieren />} />
      <Route path="/auftrag/versicherung" element={<VersicherungAktualisieren />} />
      <Route path="/auftrag/werkstatt" element={<WerkstattTermin />} />
      <Route path="/auftrag/sonstiges" element={<SonstigerAuftrag />} />
    </Routes>
  );
}
