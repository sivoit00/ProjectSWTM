import { useState, useEffect } from 'react';
import { api } from './services/api';
import type { Kunde, Fahrzeug, Werkstatt } from './services/api';

function App() {
  const [kunden, setKunden] = useState<Kunde[]>([]);
  const [werkstatt, setWerkstatt] = useState<Werkstatt[]>([]);
  const [fahrzeuge, setFahrzeuge] = useState<Fahrzeug[]>([]);
  const [count, setCount] = useState(0);  // Add counter state

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [kundenRes, fahrzeugeRes, werkstattRes] = await Promise.all([
        api.getKunden(),
        api.getFahrzeuge(),
        api.getWerkstatt()
      ]);
      setKunden(kundenRes.data);
      setFahrzeuge(fahrzeugeRes.data);
      setWerkstatt(werkstattRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  return (

  /*Einfache Datenbank abfrage zum Testen der Verbindung/Frontend*/
    <div>
      <h1>Fahrzeugservice</h1>
      
      {/* Add counter button */}
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
      </div>

      <h2>Kunden</h2>
      <ul>
        {kunden.map(kunde => (
          <li key={kunde.id}>{kunde.name} - {kunde.email}</li>
        ))}
      </ul>

      <h2>Fahrzeuge</h2>
      <ul>
        {fahrzeuge.map(fahrzeug => (
          <li key={fahrzeug.id}>
            {fahrzeug.marke} {fahrzeug.modell} ({fahrzeug.baujahr})
          </li>
          
        ))}
      </ul>
       <h2>Werkstatt</h2>
      <ul>
        {werkstatt.map(werkstatt => (
          <li key={werkstatt.id}>
            {werkstatt.name} {werkstatt.adresse} {werkstatt.plz} {werkstatt.ort}
          </li>
          
        ))}
      </ul>
    </div>
  );
}

export default App;
