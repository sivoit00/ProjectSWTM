import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
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
  const lastSeenIdRef = useRef<number | null>(null);

  useEffect(() => {
    if ("Notification" in window && Notification.permission !== "granted") {
      Notification.requestPermission();
    }
  }, []);

  const fetchNotifications = async () => {
    if (!userId) return;
    try {
      const res = await api.notifications.getAll(userId);
      const latestData = res.data;

      if (latestData.length > 0) {
        const newestId = latestData[0].id;

        if (lastSeenIdRef.current !== null && newestId > lastSeenIdRef.current) {
          
          const newMessages = latestData.filter(n => n.id > lastSeenIdRef.current!);

          newMessages.forEach(msg => {
            if (!msg.is_read && "Notification" in window && Notification.permission === "granted") {
              new Notification(msg.title, {
                body: msg.message,
                icon: "/vite.svg", 
                tag: `notification-${msg.id}`
              });
            }
          });
        }

        lastSeenIdRef.current = newestId;
      }

      setNotifications(latestData);
    } catch (e) {
      console.error("Fehler beim Laden der Notifications", e);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000); 
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