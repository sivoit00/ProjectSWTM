import axios, { type AxiosRequestConfig, type InternalAxiosRequestConfig } from 'axios';
import keycloak from '../keycloak';

export const API_URL = ((import.meta as any).env?.VITE_API_URL as string) || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
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
  firstName: string;
  lastName: string;
  username: string;
  email: string;
  phone: string;
  postcode: string;
  city: string;
  address: string;
}

export interface Fahrzeug {
  id?: number;
  brand: string;
  model: string;
  year: number;
  numberplate: string;
}

export interface Werkstatt {
  id?: number;
  name: string;
  email: string;
  phone: string;
  postcode: string;
  city: string;
  address: string;
}

export interface Anwalt {
  id?: number;
  firstName: string;
  lastName: string;
  company: string;
  email: string;
  phone: string;
  postcode: string;
  city: string;
  address: string;
}

export interface Versicherung {
  id?: number;
  name: string;
  number: string;
  email: string;
  phone: string;
  postcode: string;
  city: string;
  contact: string;
  address: string;
}

export const api = {
  customers: {
    getAll: () => apiClient.get<Kunde[]>('/kunden'),
    create: (kunde: Omit<Kunde, 'id'>) => apiClient.post<Kunde>('/kunden', kunde),
    update: (id: number, kunde: Partial<Omit<Kunde, 'id'>>) =>
      apiClient.put<Kunde>(`/kunden/${id}`, kunde),
  },

  vehicles: {
    getAll: () => apiClient.get<Fahrzeug[]>('/fahrzeuge'),
    create: (fahrzeug: Omit<Fahrzeug, 'id'>) =>
      apiClient.post<Fahrzeug>('/fahrzeuge', fahrzeug),
    update: (id: number, fahrzeug: Partial<Omit<Fahrzeug, 'id'>>) =>
      apiClient.put<Fahrzeug>(`/fahrzeuge/${id}`, fahrzeug),
  },


  workshops: {
    getAll: () => apiClient.get<Werkstatt[]>('/werkstatt'),
    create: (werkstatt: Omit<Werkstatt, 'id'>) => apiClient.post<Werkstatt>('/werkstatt', werkstatt),
    update: (id: number, werkstatt: Partial<Omit<Werkstatt, 'id'>>) =>
      apiClient.put<Werkstatt>(`/werkstatt/${id}`, werkstatt),
  },

  lawyers: {
    getAll: () => apiClient.get<Anwalt[]>('/rechtsanwalt'),
    create: (anwalt: Omit<Anwalt, 'id'>) => apiClient.post<Anwalt>('/rechtsanwalt', anwalt),
    update: (id: number, anwalt: Partial<Omit<Anwalt, 'id'>>) => 
      apiClient.put<Anwalt>(`/rechtsanwalt/${id}`, anwalt),
  },

  insurances: {
    getAll: () => apiClient.get<Versicherung[]>('/versicherung'),
    create: (versicherung: Omit<Versicherung, 'id'>) =>
      apiClient.post<Versicherung>('/versicherung', versicherung),
    update: (id: number, versicherung: Partial<Omit<Versicherung, 'id'>>) =>
      apiClient.put<Versicherung>(`/versicherung/${id}`, versicherung),
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
    getFileUrl: (filename: string) => `${API_URL}/files/uploads/${filename}`,
  },

  sendToKI: (payload: { message: string }) => {
    const sessionId = typeof window !== 'undefined' ? localStorage.getItem('sessionId') : null;
    const body = sessionId ? { ...payload, session_id: sessionId } : payload;
    return apiClient.post<{ response: string; structured: any; agent?: string }>(
      '/ki-orchestrator/message',
      body
    );
  },
};