import { useState } from "react";
import { getTaskIcon, getStatusDisplay, getAgentColor } from "./timelineUtils";
import TimelineItemLine from "./TimelineItemLine";
import TimelineItemMarker from "./TimelineItemMarker";
import TimelineItemHeader from "./TimelineItemHeader";
import TimelineItemActions from "./TimelineItemActions";
import TimelineItemStatusIndicators from "./TimelineItemStatusIndicators";
import TimelineItemDetails from "./TimelineItemDetails";
import { getTimelineItemAnimationDelay } from "./timelineItem.utils";

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

export default function TimelineItem({ event, index, totalCount, onEventClick }: TimelineItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  
  const Icon = getTaskIcon(event.task);
  const statusInfo = getStatusDisplay(event.status);
  const StatusIcon = statusInfo.icon;
  const isActive = event.status === "working" || event.status === "active";
  const isCompleted = event.status === "completed";
  const hasDetails = event.details && event.details.length > 0;
  const isLastItem = index === totalCount - 1;
  const agentColor = getAgentColor(event.agent);

  return (
    <div 
      className="relative flex items-start gap-2 animate-slideIn"
      style={{
        animationDelay: getTimelineItemAnimationDelay(index)
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Vertikale Verbindungslinie */}
      <TimelineItemLine isLastItem={isLastItem} />
    
      <TimelineItemMarker
        Icon={Icon}
        index={index}
        isActive={isActive}
        isCompleted={isCompleted}
        agentColor={agentColor}
      />

   
      <div className="flex-1 pb-1">
        <div
          className={`
            backdrop-blur-sm rounded-lg p-2 border
            transition-all duration-300 cursor-pointer
            ${isHovered ? 'shadow-lg transform scale-[1.02]' : ''}
          `}
          style={{
            backgroundColor: `${agentColor}15`,
            borderColor: `${agentColor}50`,
            boxShadow: isActive ? `0 0 15px ${agentColor}30` : undefined
          }}
          onClick={() => {
            if (event.messageId && onEventClick) onEventClick(event.messageId);
          }}
        >
          {/* Header */}
          <TimelineItemHeader
            description={event.description}
            timestamp={event.timestamp}
            statusLabel={statusInfo.label}
            statusColor={statusInfo.color}
            StatusIcon={StatusIcon}
          />

          {/* Details Toggle */}
          <TimelineItemActions
            hasDetails={Boolean(hasDetails)}
            isExpanded={isExpanded}
            onToggle={(e) => {
              e.stopPropagation();
              setIsExpanded((v) => !v);
            }}
          />

          {/* Status Indicators */}
          <TimelineItemStatusIndicators
            status={event.status}
            isActive={isActive}
            isCompleted={isCompleted}
            agentColor={agentColor}
          />

          {/* Details (nur beim Aufklappen) */}
          <TimelineItemDetails
            hasDetails={Boolean(hasDetails)}
            isExpanded={isExpanded}
            details={event.details}
          />
        </div>
      </div>
    </div>
  );
}
