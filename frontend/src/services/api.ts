import axios from 'axios';

const API_URL = 'http://localhost:8000';

export interface Kunde {
  id?: number;
  name: string;
  email: string;
  telefon: string;
}

export interface Fahrzeug {
  id?: number;
  marke: string;
  modell: string;
  baujahr: number;
  kunde_id: number;
}
export interface Werkstatt {
  id?: number;
   name: string;
   adresse: string;
   plz: string;
   ort: string; 
}

export const api = {
  // Kunden
  getKunden: () => axios.get<Kunde[]>(`${API_URL}/kunden`),
  createKunde: (kunde: Omit<Kunde, 'id'>) => axios.post<Kunde>(`${API_URL}/kunden`, kunde),

  // Fahrzeuge
  getFahrzeuge: () => axios.get<Fahrzeug[]>(`${API_URL}/fahrzeuge`),
  createFahrzeug: (fahrzeug: Omit<Fahrzeug, 'id'>) => 
    axios.post<Fahrzeug>(`${API_URL}/fahrzeuge`, fahrzeug),

  // Werkstatt
  getWerkstatt: () => axios.get<Werkstatt[]>(`${API_URL}/werkstatt`),
  createWerkstatt: (werkstatt: Omit<Werkstatt, 'id'>) => 
    axios.post<Werkstatt>(`${API_URL}/werkstatt`, werkstatt),
  // OpenAI chat
  sendToOpenAI: (message: { message: string }) =>
    axios.post<{ response: string, agent?: string }>(`${API_URL}/openai/chat`, message),
};