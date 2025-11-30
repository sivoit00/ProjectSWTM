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
  if (event.event_type === "internal") {
    return false;
  }

  const internalTasks = ["guardrail", "validation", "safety_check"];
  if (internalTasks.some(internal => event.task.toLowerCase().includes(internal))) {
    return false;
  }

  return true;
};

export type { TimelineEvent };

export default function CustomerTimeline({ events: propEvents, onEventClick }: CustomerTimelineProps) {
  const [events, setEvents] = useState<TimelineEvent[]>([]);

  useEffect(() => {
    const filteredEvents = propEvents.filter(isCustomerRelevant);
    setEvents(filteredEvents);
  }, [propEvents]);

  const completedCount = events.filter(e => e.status === "completed").length;
  const totalCount = events.length;
  const activeCount = events.filter(e => e.status === "working" || e.status === "active").length;

  const currentAgent = events.length > 0 
    ? events[events.length - 1]?.agent || "Tom"
    : "Tom";

  const hasActiveEvents = events.some(e => e.status === "working" || e.status === "active");
  const lastTimestamp = events.length > 0 ? events[events.length - 1].timestamp : new Date();

  // Auto-Collapse: Alte Events minimieren wenn mehr als 5 vorhanden
  const shouldAutoCollapse = (index: number) => {
    return events.length > 5 && index < events.length - 5;
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 p-3">
      <ActiveAgentHeader 
        currentAgent={currentAgent} 
        hasActiveEvents={hasActiveEvents} 
      />

      {}
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

      {}
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
