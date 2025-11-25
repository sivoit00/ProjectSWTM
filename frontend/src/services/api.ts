import axios from "axios";
import keycloak from "../keycloak";

const API_URL =
  (import.meta.env?.VITE_API_URL as string) || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use(
  async (config) => {
    if (keycloak.token) {
      try {
        await keycloak.updateToken(30);

        if (config.headers) {
          config.headers.Authorization = `Bearer ${keycloak.token}`;
        }
      } catch (error) {
        console.error("Token refresh failed, redirecting to login:", error);
        keycloak.login();
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ----- Interfaces (English, aligned with Profile form) -----

export interface Customer {
  id?: number;
  firstName: string;
  lastName: string;
  username: string;
  email: string;
  phone: string;
  postcode: string;
  city: string;
}

export interface Vehicle {
  id?: number;
  brand: string;
  model: string;
  year: number;
  numberPlate: string;
  customerId: number;
}

export interface Workshop {
  id?: number;
  name: string;
  email: string;
  phone: string;
  postcode: string;
  city: string;
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
}

export interface Insurance {
  id?: number;
  name: string;
  email: string;
  phone: string;
  postcode: string;
  city: string;
}

// ----- API wrapper -----

export const api = {
  customers: {
    getAll: () => apiClient.get<Customer[]>("/customers"),
    create: (customer: Omit<Customer, "id">) =>
      apiClient.post<Customer>("/customers", customer),
  },

  vehicles: {
    getAll: () => apiClient.get<Vehicle[]>("/vehicles"),
    create: (vehicle: Omit<Vehicle, "id">) =>
      apiClient.post<Vehicle>("/vehicles", vehicle),
  },

  workshops: {
    getAll: () => apiClient.get<Workshop[]>("/workshops"),
    create: (workshop: Omit<Workshop, "id">) =>
      apiClient.post<Workshop>("/workshops", workshop),
  },

  lawyers: {
    getAll: () => apiClient.get<Lawyer[]>("/lawyers"),
    create: (lawyer: Omit<Lawyer, "id">) =>
      apiClient.post<Lawyer>("/lawyers", lawyer),
  },

  insurances: {
    getAll: () => apiClient.get<Insurance[]>("/insurances"),
    create: (insurance: Omit<Insurance, "id">) =>
      apiClient.post<Insurance>("/insurances", insurance),
  },

  chat: {
    sendMessage: (message: { message: string }) =>
      apiClient.post<{ response: string }>("/langchain/chat", message),

    saveMessage: (data: { user_id: string; sender: string; message: string }) =>
      apiClient.post("/chat/save", data),

    getHistory: (userId: string) => apiClient.get(`/chat/history/${userId}`),

    clearHistory: (userId: string) =>
      apiClient.delete(`/chat/history/${userId}`),
  },

  files: {
    upload: (files: File[]) => {
      const formData = new FormData();
      files.forEach((file) => formData.append("files", file));
      return apiClient.post("/files/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    },
    getFileUrl: (filename: string) => `${API_URL}/files/uploads/${filename}`,
  },

  sendToKI: (payload: { message: string }) =>
    apiClient.post<{ response: string; structured: any }>(
      "/ki-orchestrator/message",
      payload
    ),

  // optional alias, falls du die alten Namen noch irgendwo nutzt
  getCustomers: () => apiClient.get<Customer[]>("/customers"),
  createCustomer: (customer: Omit<Customer, "id">) =>
    apiClient.post<Customer>("/customers", customer),
};
