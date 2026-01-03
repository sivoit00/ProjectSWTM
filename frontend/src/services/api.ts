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
        console.error("Token refresh failed; redirecting to login:", error);
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
  user_id?: string;
  email: string;
  username: string;
  firstName?: string | null;
  lastName?: string | null;
  phone?: string | null;
  address?: string | null;
  postcode?: string | null;
  city?: string | null;
}

export type CustomerUpsert = Omit<Customer, 'id' | 'user_id'>;

export interface Vehicle {
  id?: number;
  brand: string;
  model: string;
  year: number;
  numberplate: string;
}

export type VehicleCreate = Omit<Vehicle, 'id'>;

export interface Workshop {
  id?: number;
  name: string;
  email: string;
  phone: string;
  address: string;
  postcode: string;
  city: string;
}

export type WorkshopCreate = Omit<Workshop, 'id'>;

export interface Lawyer {
  id?: number;
  firstName: string;
  lastName: string;
  company: string;
  email: string;
  phone: string;
  address: string;
  postcode: string;
  city: string;
}

export type LawyerCreate = Omit<Lawyer, 'id'>;

export interface Insurance {
  id?: number;
  name: string;
  number: string;
  contact: string;
  email: string;
  phone: string;
  address: string;
  postcode: string;
  city: string;
}

export type InsuranceCreate = Omit<Insurance, 'id'>;

export interface NotificationItem {
  id: number;
  title: string;
  message: string;
  type: string;
  data: any; 
  created_at: string;
  is_read: boolean;
}

export interface ChatConversationSummary {
  user_id: string;
  conversation_id: string;
  title?: string | null;
  created_at: string;
  updated_at: string;
}

export const api = {
  customers: {
    getAll: () => apiClient.get<Customer[]>('/customers'),
    create: (customer: CustomerUpsert) => apiClient.post<Customer>('/customers', customer),
    update: (id: number, customer: CustomerUpsert) => apiClient.put<Customer>(`/customers/${id}`, customer),
    me: () => apiClient.get<Customer>('/customers/me'),
  },

  vehicles: {
    getAll: () => apiClient.get<Vehicle[]>('/vehicles'),
    create: (vehicle: VehicleCreate) => apiClient.post<Vehicle>('/vehicles', vehicle),
    update: (id: number, vehicle: VehicleCreate) => apiClient.put<Vehicle>(`/vehicles/${id}`, vehicle),
    delete: (id: number) => apiClient.delete(`/vehicles/${id}`),
  },

  workshops: {
    getAll: () => apiClient.get<Workshop[]>('/workshops'),
    create: (workshop: WorkshopCreate) => apiClient.post<Workshop>('/workshops', workshop),
    update: (id: number, workshop: WorkshopCreate) => apiClient.put<Workshop>(`/workshops/${id}`, workshop),
    delete: (id: number) => apiClient.delete(`/workshops/${id}`),
  },

  lawyers: {
    getAll: () => apiClient.get<Lawyer[]>('/lawyers'),
    create: (lawyer: LawyerCreate) => apiClient.post<Lawyer>('/lawyers', lawyer),
    update: (id: number, lawyer: LawyerCreate) => apiClient.put<Lawyer>(`/lawyers/${id}`, lawyer),
    delete: (id: number) => apiClient.delete(`/lawyers/${id}`),
  },

  insurances: {
    getAll: () => apiClient.get<Insurance[]>('/insurances'),
    create: (insurance: InsuranceCreate) => apiClient.post<Insurance>('/insurances', insurance),
    update: (id: number, insurance: InsuranceCreate) => apiClient.put<Insurance>(`/insurances/${id}`, insurance),
    delete: (id: number) => apiClient.delete(`/insurances/${id}`),
  },

  chat: {
    saveMessage: (data: { user_id: string; sender: string; message: string; conversation_id?: string }) =>
      apiClient.post('/chat/save', data),
    
    getHistory: (userId: string, conversationId?: string) =>
      apiClient.get(`/chat/history/${userId}`, {
        params: conversationId ? { conversation_id: conversationId } : {},
      }),

    listConversations: (userId: string) =>
      apiClient.get<ChatConversationSummary[]>(`/chat/conversations/${userId}/details`),

    renameConversation: (userId: string, conversationId: string, title: string | null) =>
      apiClient.patch<ChatConversationSummary>(`/chat/conversations/${userId}/${conversationId}`, { title }),

    deleteConversation: (userId: string, conversationId: string) =>
      apiClient.delete(`/chat/conversations/${userId}/${conversationId}`),
    
    clearHistory: (userId: string, conversationId?: string) =>
      apiClient.delete(`/chat/history/${userId}`, {
        params: conversationId ? { conversation_id: conversationId } : {},
      }),

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