import { useEffect, useState } from "react";
import ActiveAgentHeader from "./timeline/ActiveAgentHeader";
import EmptyState from "./timeline/EmptyState";
import TimelineItem, { TimelineEvent } from "./timeline/TimelineItem";
import TimelineFooter from "./timeline/TimelineFooter";
import "./CustomerTimeline.css";

interface CustomerTimelineProps {
  events: TimelineEvent[];
  onEventClick?: (messageId: string) => void;
  userName?: string;
}

const isCustomerRelevant = (event: TimelineEvent): boolean => {
  const agentLower = (event.agent || "").toLowerCase();
  
  if (agentLower.includes("guardrail")) {
    return false;
  }

  if (event.status === "standby" && (agentLower.includes("tom") || agentLower.includes("chatbot"))) {
    return false;
  }

  return true;
};

export type { TimelineEvent };

export default function CustomerTimeline({ events: propEvents, onEventClick, userName }: CustomerTimelineProps) {
  const [events, setEvents] = useState<TimelineEvent[]>([]);

  useEffect(() => {
    console.log("📊 Timeline: Received events:", propEvents);
    const filteredEvents = propEvents.filter(isCustomerRelevant);
    console.log("📊 Timeline: After filtering:", filteredEvents);
    setEvents(filteredEvents);
  }, [propEvents]);

  const completedCount = events.filter(e => e.status === "completed").length;
  const totalCount = events.length;
  
  const activeAgents = events.filter(e => 
    (e.status === "working" || e.status === "active") &&
    e.event_type !== "internal"
  );
  
  const lastActiveEvent = activeAgents.length > 0 ? activeAgents[activeAgents.length - 1] : null;
  const currentAgent = lastActiveEvent?.agent || "chatbot";
  const hasActiveEvents = activeAgents.length > 0;
  const lastTimestamp = events.length > 0 ? events[events.length - 1].timestamp : new Date();

  const shouldAutoCollapse = (index: number) => {
    return events.length > 5 && index < events.length - 5;
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 p-3">
      <ActiveAgentHeader 
        currentAgent={currentAgent} 
        hasActiveEvents={hasActiveEvents}
        userName={userName}
      />

      <div className="flex-1 overflow-y-auto">
        {events.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="space-y-2">
            {events.map((event, index) => (
              <TimelineItem 
                key={index} 
                event={event} 
                index={index}
                totalCount={events.length}
                isAutoCollapsed={shouldAutoCollapse(index)}
                onEventClick={onEventClick}
              />
            ))}
          </div>
        )}
      </div>

      {events.length > 0 && (
        <TimelineFooter 
          completedCount={completedCount} 
          totalCount={totalCount} 
          hasActiveAgent={hasActiveEvents} 
          lastTimestamp={lastTimestamp} 
        />
      )}
    </div>
  );
}
