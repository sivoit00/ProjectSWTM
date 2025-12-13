import { useState } from "react";
import { CheckCircle2, ChevronDown, ChevronUp } from "lucide-react";
import { getTaskIcon, getStatusDisplay, getAgentColor, formatTime } from "./timelineUtils";

export interface TimelineEvent {
  task: string;
  timestamp: string | Date;
  status: "pending" | "working" | "sent" | "completed" | "active" | "standby" | "idle" | "disabled" | "done";
  description: string;
  details?: string;
  agent?: string;
  event_type?: "task" | "user_request" | "internal" | "agent_session";
  messageId?: string;
  sessionId?: string;
}

interface TimelineItemProps {
  event: TimelineEvent;
  index: number;
  totalCount: number;
  isAutoCollapsed?: boolean;
  onEventClick?: (messageId: string) => void;
}

export default function TimelineItem({ event, index, totalCount, isAutoCollapsed = false, onEventClick }: TimelineItemProps) {
  const [isExpanded, setIsExpanded] = useState(!isAutoCollapsed);
  const [isHovered, setIsHovered] = useState(false);
  
  const Icon = getTaskIcon(event.task);
  const statusInfo = getStatusDisplay(event.status);
  const StatusIcon = statusInfo.icon;
  const isActive = event.status === "working" || event.status === "active";
  const isCompleted = event.status === "completed";
  const hasDetails = event.details && event.details.length > 0;
  const isLastItem = index === totalCount - 1;

  return (
    <div 
      className="relative flex items-start gap-2 animate-slideIn"
      style={{
        animationDelay: `${index * 0.05}s`
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Vertikale Verbindungslinie */}
      {!isLastItem && (
        <div 
          className="absolute left-3.5 top-7 w-0.5 h-full bg-gradient-to-b from-gray-700 to-transparent"
          style={{ height: 'calc(100% + 8px)' }}
        />
      )}
    
      <div className="relative z-10 flex-shrink-0">
        <div
          className={`
            flex items-center justify-center w-7 h-7 rounded-full
            transition-all duration-300 relative
            ${isActive ? 'ring-2 ring-opacity-50 shadow-lg' : ''}
            ${isCompleted ? 'bg-green-500' : 'bg-gray-800'}
          `}
          style={{
            backgroundColor: isActive ? getAgentColor(event.agent) : isCompleted ? '#10B981' : '#1f2937',
            boxShadow: isActive ? `0 0 10px ${getAgentColor(event.agent)}40` : undefined
          }}
        >
          <Icon size={14} className="text-white" />
        
          {isActive && (
            <div 
              className="absolute inset-0 rounded-full animate-ping opacity-30"
              style={{ backgroundColor: getAgentColor(event.agent) }}
            ></div>
          )}
        </div>
        
    
        <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-gray-900 rounded-full flex items-center justify-center border border-gray-700">
          <span className="text-[8px] text-gray-400 font-bold">
            {index + 1}
          </span>
        </div>
      </div>

   
      <div className="flex-1 pb-1">
        <div
          className={`
            backdrop-blur-sm rounded-lg p-2 border
            transition-all duration-300 cursor-pointer
            ${isHovered ? 'shadow-lg transform scale-[1.02]' : ''}
          `}
          style={{
            backgroundColor: `${getAgentColor(event.agent)}15`,
            borderColor: `${getAgentColor(event.agent)}50`,
            boxShadow: isActive ? `0 0 15px ${getAgentColor(event.agent)}30` : undefined
          }}
          onClick={() => {
            if (event.messageId && onEventClick) onEventClick(event.messageId);
          }}
        >
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 flex-1">
              <h4 className="text-white font-semibold text-xs">
                {event.description}
              </h4>
      
              <span
                className="flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-medium transition-all"
                style={{
                  backgroundColor: `${statusInfo.color}20`,
                  color: statusInfo.color,
                }}
              >
                <StatusIcon size={10} />
                {statusInfo.label}
              </span>
            </div>
            
            <span className="text-[10px] text-gray-500">
              {formatTime(event.timestamp)}
            </span>
          </div>

          {/* Details Toggle */}
          {hasDetails && (
            <div className="mt-1 flex items-center justify-end">
              <button
                type="button"
                className="flex items-center gap-1 text-[10px] text-gray-400 hover:text-white transition-colors"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsExpanded((v) => !v);
                }}
              >
                {isExpanded ? (
                  <>
                    <ChevronUp size={12} />
                    Hide details
                  </>
                ) : (
                  <>
                    <ChevronDown size={12} />
                    Show details
                  </>
                )}
              </button>
            </div>
          )}

          {/* Status Indicators */}
          {isActive && (
            <div className="mt-1.5 flex items-center gap-1.5 animate-pulse">
              <div className="relative">
                <div 
                  className="w-1.5 h-1.5 rounded-full animate-ping"
                  style={{ backgroundColor: getAgentColor(event.agent) }}
                ></div>
                <div 
                  className="w-1.5 h-1.5 rounded-full absolute top-0 left-0"
                  style={{ backgroundColor: getAgentColor(event.agent) }}
                ></div>
              </div>
              <span 
                className="text-[10px] font-medium"
                style={{ color: getAgentColor(event.agent) }}
              >
                Processing...
              </span>
            </div>
          )}
          
          {isCompleted && (
            <div className="mt-1.5 flex items-center gap-1.5">
              <CheckCircle2 size={12} className="text-green-400" />
              <span className="text-[10px] text-green-400 font-medium">
                Done
              </span>
            </div>
          )}
          
          {event.status === "pending" && (
            <div className="mt-1.5 flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-yellow-400"></div>
              <span className="text-[10px] text-yellow-400 font-medium">
                Waiting...
              </span>
            </div>
          )}

          {/* Details (nur beim Aufklappen) */}
          {hasDetails && isExpanded && (
            <div className="mt-2 border-t border-gray-700/50 pt-2 space-y-1">
              {String(event.details)
                .split("\n")
                .filter((l) => l.trim().length > 0)
                .map((line, i) => (
                  <div key={i} className="text-[10px] text-gray-300 leading-snug">
                    {line}
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
