import { Loader2 } from "lucide-react";

interface TimelineFooterProps {
  completedCount: number;
  totalCount: number;
  hasActiveAgent: boolean;
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
  hasActiveAgent,
  lastTimestamp 
}: TimelineFooterProps) {
  if (totalCount === 0) return null;

  return (
    <div className="mt-2 pt-2 border-t border-gray-800">
      <div className="flex items-center justify-end text-[10px]">
        <span className="text-gray-500">
          {formatTime(lastTimestamp)}
        </span>
      </div>
    </div>
  );
}
