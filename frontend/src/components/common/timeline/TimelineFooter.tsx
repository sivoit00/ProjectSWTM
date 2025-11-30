import { Loader2 } from "lucide-react";

interface TimelineFooterProps {
  completedCount: number;
  totalCount: number;
  activeCount: number;
  lastTimestamp: string | Date;
}

const formatTime = (timestamp: string | Date) => {
  const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
  return date.toLocaleTimeString('de-DE', { 
    hour: '2-digit', 
    minute: '2-digit'
  });
};

export default function TimelineFooter({ 
  completedCount, 
  totalCount, 
  activeCount,
  lastTimestamp 
}: TimelineFooterProps) {
  if (totalCount === 0) return null;

  return (
    <div className="mt-2 pt-2 border-t border-gray-800">
      <div className="flex items-center justify-between text-[10px]">
        <span className="text-gray-500">
          {completedCount} von {totalCount} abgeschlossen
        </span>
        <span className="text-gray-500">
          {formatTime(lastTimestamp)}
        </span>
      </div>
      
      {activeCount > 0 && (
        <div className="mt-1.5 flex items-center justify-center gap-1.5 text-[10px] text-blue-400">
          <div className="w-1 h-1 rounded-full bg-blue-400 animate-pulse"></div>
          <span>
            {activeCount} Agent(en) aktiv
          </span>
        </div>
      )}
    </div>
  );
}
