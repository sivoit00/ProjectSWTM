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

export interface Customer {
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

export interface Vehicle {
  id?: number;
  brand: string;
  model: string;
  year: number;
  numberplate: string;
}

export interface Workshop {
  id?: number;
  name: string;
  email: string;
  phone: string;
  postcode: string;
  city: string;
  address: string;
}

export interface Lawyer {
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

export interface Insurance {
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
    getAll: () => apiClient.get<Customer[]>('/customers'),
    create: (customer: Omit<Customer, 'id'>) =>
      apiClient.post<Customer>('/customers', customer),
    update: (id: number, customer: Partial<Omit<Customer, 'id'>>) =>
      apiClient.put<Customer>(`/customers/${id}`, customer),
  },

  vehicles: {
    getAll: () => apiClient.get<Vehicle[]>('/vehicles'),
    create: (vehicle: Omit<Vehicle, 'id'>) =>
      apiClient.post<Vehicle>('/vehicles', vehicle),
    update: (id: number, vehicle: Partial<Omit<Vehicle, 'id'>>) =>
      apiClient.put<Vehicle>(`/vehicles/${id}`, vehicle),
  },

  workshops: {
    getAll: () => apiClient.get<Workshop[]>('/workshops'),
    create: (workshop: Omit<Workshop, 'id'>) =>
      apiClient.post<Workshop>('/workshops', workshop),
    update: (id: number, workshop: Partial<Omit<Workshop, 'id'>>) =>
      apiClient.put<Workshop>(`/workshops/${id}`, workshop),
  },

  lawyers: {
    getAll: () => apiClient.get<Lawyer[]>('/lawyers'),
    create: (lawyer: Omit<Lawyer, 'id'>) =>
      apiClient.post<Lawyer>('/lawyers', lawyer),
    update: (id: number, lawyer: Partial<Omit<Lawyer, 'id'>>) =>
      apiClient.put<Lawyer>(`/lawyers/${id}`, lawyer),
  },

  insurances: {
    getAll: () => apiClient.get<Insurance[]>('/insurances'),
    create: (insurance: Omit<Insurance, 'id'>) =>
      apiClient.post<Insurance>('/insurances', insurance),
    update: (id: number, insurance: Partial<Omit<Insurance, 'id'>>) =>
      apiClient.put<Insurance>(`/insurances/${id}`, insurance),
  },


  chat: {
    saveMessage: (data: { user_id: string; sender: string; message: string }) =>
      apiClient.post('/chat/save', data),
    
    getHistory: (userId: string) =>
      apiClient.get(`/chat/history/${userId}`),
    
    clearHistory: (userId: string) =>
      apiClient.delete(`/chat/history/${userId}`),

    createSession: () => 
      apiClient.post<{ ok: boolean; session_id: string; message: string }>('/ki-orchestrator/session/new'),
      
    clearSession: (sessionId: string) => 
      apiClient.delete(`/ki-orchestrator/session/${sessionId}`),
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

  notifications: {
    getAll: (userId: string) => apiClient.get<NotificationItem[]>(`/notifications/list/${userId}`),
    markRead: (id: number) => apiClient.post(`/notifications/mark-read/${id}`),
  },
};