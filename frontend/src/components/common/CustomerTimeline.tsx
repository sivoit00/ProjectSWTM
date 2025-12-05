import { useEffect, useState } from "react";
import ActiveAgentHeader from "./timeline/ActiveAgentHeader";
import EmptyState from "./timeline/EmptyState";
import TimelineItem, { TimelineEvent } from "./timeline/TimelineItem";
import TimelineFooter from "./timeline/TimelineFooter";
import "./CustomerTimeline.css";

interface CustomerTimelineProps {
  events: TimelineEvent[];
  onEventClick?: (messageId: string) => void;
}

const isCustomerRelevant = (event: TimelineEvent): boolean => {
  const agentLower = (event.agent || "").toLowerCase();
  
  if (agentLower.includes("guardrail")) {
    return false;
  }

  return true;
};

export type { TimelineEvent };

export default function CustomerTimeline({ events: propEvents, onEventClick }: CustomerTimelineProps) {
  const [events, setEvents] = useState<TimelineEvent[]>([]);

  useEffect(() => {
    console.log("📊 Timeline: Received events:", propEvents);
    const filteredEvents = propEvents.filter(isCustomerRelevant);
    console.log("📊 Timeline: After filtering:", filteredEvents);
    setEvents(filteredEvents);
  }, [propEvents]);

  const completedCount = events.filter(e => e.status === "completed").length;
  const totalCount = events.length;
  
  const activeAgents = new Set(
    events
      .filter(e => e.status === "working" || e.status === "active")
      .map(e => e.agent)
  );
  const activeCount = activeAgents.size;

  const lastActiveEvent = [...events].reverse().find(e => e.status === "working" || e.status === "active");
  const currentAgent = lastActiveEvent?.agent || "Tom";

  const hasActiveEvents = events.some(e => e.status === "working" || e.status === "active");
  const lastTimestamp = events.length > 0 ? events[events.length - 1].timestamp : new Date();

  const shouldAutoCollapse = (index: number) => {
    return events.length > 5 && index < events.length - 5;
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 p-3">
      <ActiveAgentHeader 
        currentAgent={currentAgent} 
        hasActiveEvents={hasActiveEvents} 
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
          activeCount={activeCount} 
          lastTimestamp={lastTimestamp} 
        />
      )}
    </div>
  );
}
