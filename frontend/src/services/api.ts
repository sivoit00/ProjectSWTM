import axios from 'axios';
import type { Kunde, Fahrzeug, Werkstatt, Auftrag, ChatMessage, ChatResponse } from '../types';

const API_URL = 'http://localhost:8000';
const API_PREFIX = '/api/v1';

const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const kundenAPI = {
  getAll: () => axiosInstance.get<Kunde[]>(`${API_PREFIX}/kunden`),
  getById: (id: number) => axiosInstance.get<Kunde>(`${API_PREFIX}/kunden/${id}`),
  create: (kunde: Omit<Kunde, 'id'>) => axiosInstance.post<Kunde>(`${API_PREFIX}/kunden`, kunde),
  update: (id: number, kunde: Partial<Kunde>) => axiosInstance.put<Kunde>(`${API_PREFIX}/kunden/${id}`, kunde),
  delete: (id: number) => axiosInstance.delete(`${API_PREFIX}/kunden/${id}`),
};

export const fahrzeugeAPI = {
  getAll: () => axiosInstance.get<Fahrzeug[]>(`${API_PREFIX}/fahrzeuge`),
  getById: (id: number) => axiosInstance.get<Fahrzeug>(`${API_PREFIX}/fahrzeuge/${id}`),
  getByKunde: (kundeId: number) => axiosInstance.get<Fahrzeug[]>(`${API_PREFIX}/fahrzeuge/kunde/${kundeId}`),
  create: (fahrzeug: Omit<Fahrzeug, 'id'>) => axiosInstance.post<Fahrzeug>(`${API_PREFIX}/fahrzeuge`, fahrzeug),
  update: (id: number, fahrzeug: Partial<Fahrzeug>) => axiosInstance.put<Fahrzeug>(`${API_PREFIX}/fahrzeuge/${id}`, fahrzeug),
  delete: (id: number) => axiosInstance.delete(`${API_PREFIX}/fahrzeuge/${id}`),
};

export const werkstaettenAPI = {
  getAll: () => axiosInstance.get<Werkstatt[]>(`${API_PREFIX}/werkstatt`),
  getById: (id: number) => axiosInstance.get<Werkstatt>(`${API_PREFIX}/werkstatt/${id}`),
  create: (werkstatt: Omit<Werkstatt, 'id'>) => axiosInstance.post<Werkstatt>(`${API_PREFIX}/werkstatt`, werkstatt),
  update: (id: number, werkstatt: Partial<Werkstatt>) => axiosInstance.put<Werkstatt>(`${API_PREFIX}/werkstatt/${id}`, werkstatt),
  delete: (id: number) => axiosInstance.delete(`${API_PREFIX}/werkstatt/${id}`),
};

export const auftraegeAPI = {
  getAll: () => axiosInstance.get<Auftrag[]>(`${API_PREFIX}/auftraege`),
  getById: (id: number) => axiosInstance.get<Auftrag>(`${API_PREFIX}/auftraege/${id}`),
  getByFahrzeug: (fahrzeugId: number) => axiosInstance.get<Auftrag[]>(`${API_PREFIX}/auftraege/fahrzeug/${fahrzeugId}`),
  getByWerkstatt: (werkstattId: number) => axiosInstance.get<Auftrag[]>(`${API_PREFIX}/auftraege/werkstatt/${werkstattId}`),
  create: (auftrag: Omit<Auftrag, 'id'>) => axiosInstance.post<Auftrag>(`${API_PREFIX}/auftraege`, auftrag),
  update: (id: number, auftrag: Partial<Auftrag>) => axiosInstance.put<Auftrag>(`${API_PREFIX}/auftraege/${id}`, auftrag),
  delete: (id: number) => axiosInstance.delete(`${API_PREFIX}/auftraege/${id}`),
};

export const chatAPI = {
  sendMessage: (message: ChatMessage) => axiosInstance.post<ChatResponse>(`${API_PREFIX}/ai/chat`, message),
};

export const api = {
  getKunden: kundenAPI.getAll,
  createKunde: kundenAPI.create,
  getFahrzeuge: fahrzeugeAPI.getAll,
  createFahrzeug: fahrzeugeAPI.create,
  getWerkstatt: werkstaettenAPI.getAll,
  createWerkstatt: werkstaettenAPI.create,
  sendToOpenAI: chatAPI.sendMessage,
};
