import { useState, useEffect } from "react";
import { api } from "../../services/api";
import type { Kunde, Fahrzeug, Werkstatt } from "../../services/api";

export default function ApiPage() {
  const [kunden, setKunden] = useState<Kunde[]>([]);
  const [werkstatt, setWerkstatt] = useState<Werkstatt[]>([]);
  const [fahrzeuge, setFahrzeuge] = useState<Fahrzeug[]>([]);
  const [text, setText] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [kundenRes, fahrzeugeRes, werkstattRes] = await Promise.all([
        api.getKunden(),
        api.getFahrzeuge(),
        api.getWerkstatt(),
      ]);
      setKunden(kundenRes.data);
      setFahrzeuge(fahrzeugeRes.data);
      setWerkstatt(werkstattRes.data);
    } catch (error) {
      console.error("Error loading data:", error);
    }
  };

  return (
    <div>
      <h1>Vehicle Service</h1>

      <h2>Customers</h2>
      <ul>
        {kunden.map((kunde) => (
          <li key={kunde.id}>
            {kunde.name} - {kunde.email}
          </li>
        ))}
      </ul>

      <h2>Vehicles</h2>
      <ul>
        {fahrzeuge.map((fahrzeug) => (
          <li key={fahrzeug.id}>
            {fahrzeug.marke} {fahrzeug.modell} ({fahrzeug.baujahr})
          </li>
        ))}
      </ul>
      <h2>Workshops</h2>
      <ul>
        {werkstatt.map((w) => (
          <li key={w.id}>
            {w.name} {w.adresse} {w.plz} {w.ort}
          </li>
        ))}
      </ul>

      <div className="text">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type something..."
        />
        <p>You typed: {text}</p>
      </div>
    </div>
  );
}
