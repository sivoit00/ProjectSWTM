import axios from 'axios';
import keycloak from '../keycloak';

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

function authHeader() {
  const token = keycloak.token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const api = {
  getKunden: () => axios.get<Kunde[]>(`${API_URL}/kunden`, { headers: authHeader() }),
  createKunde: (kunde: Omit<Kunde, 'id'>) =>
    axios.post<Kunde>(`${API_URL}/kunden`, kunde, { headers: authHeader() }),

  getFahrzeuge: () => axios.get<Fahrzeug[]>(`${API_URL}/fahrzeuge`, { headers: authHeader() }),
  createFahrzeug: (fahrzeug: Omit<Fahrzeug, 'id'>) =>
    axios.post<Fahrzeug>(`${API_URL}/fahrzeuge`, fahrzeug, { headers: authHeader() }),

  getWerkstatt: () => axios.get<Werkstatt[]>(`${API_URL}/werkstatt`, { headers: authHeader() }),
  createWerkstatt: (werkstatt: Omit<Werkstatt, 'id'>) =>
    axios.post<Werkstatt>(`${API_URL}/werkstatt`, werkstatt, { headers: authHeader() }),

  sendToOpenAI: (message: { message: string }) =>
    axios.post<{ response: string }>(`${API_URL}/openai/chat`, message, { headers: authHeader() }),
};
