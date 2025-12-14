import axios, { type InternalAxiosRequestConfig } from 'axios';
import keycloak from '../keycloak';

export const API_URL = ((import.meta as any).env?.VITE_API_URL as string) || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000,
});

apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    if (keycloak.token) {
      try {
        await keycloak.updateToken(30);
        
        if (config.headers) {
          (config.headers as Record<string, any>).Authorization = `Bearer ${keycloak.token}`;
        }
      } catch (error) {
        console.error("Token refresh fehlgeschlagen, leite zum Login:", error);
        keycloak.login();
      }
    }
    return config;
  },
  (error: any) => {
    return Promise.reject(error);
  }
);

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

export interface NotificationItem {
  id: number;
  title: string;
  message: string;
  type: string;
  data: any; 
  created_at: string;
  is_read: boolean;
}

export const api = {
  customers: {
    getAll: () => apiClient.get<Kunde[]>('/kunden'),
    create: (kunde: Omit<Kunde, 'id'>) => apiClient.post<Kunde>('/kunden', kunde),
  },

  vehicles: {
    getAll: () => apiClient.get<Fahrzeug[]>('/fahrzeuge'),
    create: (fahrzeug: Omit<Fahrzeug, 'id'>) => apiClient.post<Fahrzeug>('/fahrzeuge', fahrzeug),
  },

  workshops: {
    getAll: () => apiClient.get<Werkstatt[]>('/werkstatt'),
    create: (werkstatt: Omit<Werkstatt, 'id'>) => apiClient.post<Werkstatt>('/werkstatt', werkstatt),
  },

  chat: {
    sendMessage: (message: { message: string }) =>
      apiClient.post<{ response: string }>('/langchain/chat', message),
    
    saveMessage: (data: { user_id: string; sender: string; message: string }) =>
      apiClient.post('/chat/save', data),
    
    getHistory: (userId: string) =>
      apiClient.get(`/chat/history/${userId}`),
    
    clearHistory: (userId: string) =>
      apiClient.delete(`/chat/history/${userId}`),
  },

  files: {
    upload: (files: File[]) => {
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));
      return apiClient.post('/files/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    },
    transcribe: (storedFilename: string, language?: string) =>
      apiClient.post<{ success: boolean; text: string; model?: string }>(
        '/files/transcribe',
        { stored_filename: storedFilename, language }
      ),
    getFileUrl: (filename: string) => `${API_URL}/files/uploads/${filename}`,
  },

  sendToKI: (payload: { message: string }) => {
    // attach session_id from localStorage if present so backend agents can use per-session memory
    const sessionId = typeof window !== 'undefined' ? localStorage.getItem('sessionId') : null;
    const body = sessionId ? { ...payload, session_id: sessionId } : payload;
    return apiClient.post<{ response: string; structured: any; agent?: string }>('/ki-orchestrator/message', body);
  },

  notifications: {
    getAll: (userId: string) => apiClient.get<NotificationItem[]>(`/notifications/list/${userId}`),
    markRead: (id: number) => apiClient.post(`/notifications/mark-read/${id}`),
  },
 
  getKunden: () => apiClient.get<Kunde[]>('/kunden'),
  createKunde: (kunde: Omit<Kunde, 'id'>) => apiClient.post<Kunde>('/kunden', kunde),
  getFahrzeuge: () => apiClient.get<Fahrzeug[]>('/fahrzeuge'),
  createFahrzeug: (fahrzeug: Omit<Fahrzeug, 'id'>) => apiClient.post<Fahrzeug>('/fahrzeuge', fahrzeug),
  getWerkstatt: () => apiClient.get<Werkstatt[]>('/werkstatt'),
  createWerkstatt: (werkstatt: Omit<Werkstatt, 'id'>) => apiClient.post<Werkstatt>('/werkstatt', werkstatt),
  sendToOpenAI: (message: { message: string }) => apiClient.post<{ response: string }>('/langchain/chat', message),
};