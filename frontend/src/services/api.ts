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
  customers: {
    getAll: () => axios.get<Kunde[]>(`${API_URL}/kunden`),
    create: (kunde: Omit<Kunde, 'id'>) => axios.post<Kunde>(`${API_URL}/kunden`, kunde),
  },

  vehicles: {
    getAll: () => axios.get<Fahrzeug[]>(`${API_URL}/fahrzeuge`),
    create: (fahrzeug: Omit<Fahrzeug, 'id'>) => 
      axios.post<Fahrzeug>(`${API_URL}/fahrzeuge`, fahrzeug),
  },

  workshops: {
    getAll: () => axios.get<Werkstatt[]>(`${API_URL}/werkstatt`),
    create: (werkstatt: Omit<Werkstatt, 'id'>) => 
      axios.post<Werkstatt>(`${API_URL}/werkstatt`, werkstatt),
  },

  chat: {
    sendMessage: (message: { message: string }) =>
      axios.post<{ response: string }>(`${API_URL}/langchain/chat`, message),
  },

  getKunden: () => axios.get<Kunde[]>(`${API_URL}/kunden`),
  createKunde: (kunde: Omit<Kunde, 'id'>) => axios.post<Kunde>(`${API_URL}/kunden`, kunde),
  getFahrzeuge: () => axios.get<Fahrzeug[]>(`${API_URL}/fahrzeuge`),
  createFahrzeug: (fahrzeug: Omit<Fahrzeug, 'id'>) => 
    axios.post<Fahrzeug>(`${API_URL}/fahrzeuge`, fahrzeug),
  getWerkstatt: () => axios.get<Werkstatt[]>(`${API_URL}/werkstatt`),
  createWerkstatt: (werkstatt: Omit<Werkstatt, 'id'>) => 
    axios.post<Werkstatt>(`${API_URL}/werkstatt`, werkstatt),
  sendToOpenAI: (message: { message: string }) =>
    axios.post<{ response: string }>(`${API_URL}/langchain/chat`, message),
};