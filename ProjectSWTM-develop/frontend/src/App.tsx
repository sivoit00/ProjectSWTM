import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";
import Schadensmeldung from "./pages/Schadensmeldung";
import Auftraege from "./pages/Auftraege";
import Visualisierung from "./pages/Visualisierung";

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
    </Routes>
  );
}
