import { useState, useRef, useEffect } from 'react';
import { Bell } from 'lucide-react'; 
import { useNotifications } from '../../context/NotificationContext';

interface Props {
  onProcessEmail?: (emailData: any) => void; 
}

export default function NotificationBell({ onProcessEmail }: Props) {
  const { notifications, unreadCount, markAsRead } = useNotifications();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleItemClick = (notif: any) => {
    markAsRead(notif.id);
    setIsOpen(false);

    if (notif.type === 'EMAIL_REPLY' && onProcessEmail) {
      setTimeout(() => {
          onProcessEmail(notif.data);
      }, 50);
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button 
        onClick={() => setIsOpen(!isOpen)} 
        className="p-2 text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white relative focus:outline-none transition-colors"
      >
        <Bell
          className={`h-6 w-6 ${
            unreadCount > 0
              ? "text-gray-900 dark:text-white"
              : "text-gray-500 dark:text-gray-400"
          }`}
        />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 h-4 w-4 bg-red-500 rounded-full text-xs flex items-center justify-center text-white font-bold animate-pulse">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 dark:bg-gray-800 dark:border-gray-700 rounded-lg shadow-xl z-50 overflow-hidden ring-1 ring-black ring-opacity-5">
          <div className="p-3 text-sm font-semibold text-gray-900 border-b border-gray-200 bg-gray-50 dark:text-gray-300 dark:border-gray-700 dark:bg-gray-900 flex justify-between items-center">
            <span>Notifications</span>
            <span className="text-xs font-normal text-gray-500">{notifications.length} Total</span>
          </div>
          
          <div className="max-h-96 overflow-y-auto custom-scrollbar">
            {notifications.length === 0 ? (
              <div className="p-6 text-gray-500 text-sm text-center italic">
                No new messages
              </div>
            ) : (
              <ul className="divide-y divide-gray-200 dark:divide-gray-700">
                {notifications.map(n => (
                  <li 
                    key={n.id} 
                    onClick={() => handleItemClick(n)}
                    className={`p-3 cursor-pointer transition-all duration-200 ${
                        n.is_read 
                        ? 'bg-gray-50 opacity-80 hover:opacity-100 dark:bg-gray-800 dark:opacity-60 dark:hover:opacity-100' 
                        : 'bg-blue-50 hover:bg-blue-100 border-l-4 border-blue-500 dark:bg-gray-750 dark:hover:bg-gray-700'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                        <div className={`font-bold text-sm mb-1 ${n.is_read ? 'text-gray-500 dark:text-gray-400' : 'text-gray-900 dark:text-white'}`}>
                            {n.title}
                        </div>
                        {n.is_read && <span className="text-[10px] text-gray-500 border border-gray-300 px-1 rounded dark:border-gray-600">Read</span>}
                    </div>
                    
                    <div className="text-xs text-gray-700 truncate mb-1 dark:text-gray-300">{n.message}</div>
                    <div className="text-[10px] text-gray-500 text-right">
                        {new Date(n.created_at).toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: 'short' })}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
}