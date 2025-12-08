import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';
import type { NotificationItem } from '../services/api';
import keycloak from '../keycloak';

interface NotificationContextType {
  notifications: NotificationItem[];
  unreadCount: number;
  markAsRead: (id: number) => void;
  refreshNotifications: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const userId = keycloak.tokenParsed?.sub;

  const fetchNotifications = async () => {
    if (!userId) return;
    try {
      const res = await api.notifications.getAll(userId);
      setNotifications(res.data);
    } catch (e) {
      console.error("Fehler beim Laden der Notifications", e);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60000); 
    return () => clearInterval(interval);
  }, [userId]);

  const markAsRead = async (id: number) => {
    setNotifications(prev => prev.map(n => 
      n.id === id ? { ...n, is_read: true } : n
    ));

    try {
      await api.notifications.markRead(id);
    } catch (e) {
      console.error("Fehler beim Markieren als gelesen", e);
    }
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <NotificationContext.Provider value={{ 
      notifications, 
      unreadCount, 
      markAsRead, 
      refreshNotifications: fetchNotifications 
    }}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) throw new Error("useNotifications must be used within NotificationProvider");
  return context;
};