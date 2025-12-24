import type { ComponentType } from "react";

interface TimelineItemMarkerProps {
  Icon: ComponentType<{ size?: number; className?: string }>;
  index: number;
  isActive: boolean;
  isCompleted: boolean;
  agentColor: string;
}

export default function TimelineItemMarker({
  Icon,
  index,
  isActive,
  isCompleted,
  agentColor,
}: TimelineItemMarkerProps) {
  return (
    <div className="relative z-10 flex-shrink-0">
      <div
        className={`
            flex items-center justify-center w-7 h-7 rounded-full
            transition-all duration-300 relative
            ${isActive ? "ring-2 ring-opacity-50 shadow-lg" : ""}
            ${isCompleted ? "bg-green-500" : "bg-gray-800"}
          `}
        style={{
          backgroundColor: isActive ? agentColor : isCompleted ? "#10B981" : "#1f2937",
          boxShadow: isActive ? `0 0 10px ${agentColor}40` : undefined,
        }}
      >
        <Icon size={14} className="text-white" />

        {isActive && (
          <div
            className="absolute inset-0 rounded-full animate-ping opacity-30"
            style={{ backgroundColor: agentColor }}
          ></div>
        )}
      </div>

      <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-white dark:bg-gray-900 rounded-full flex items-center justify-center border border-gray-300 dark:border-gray-700">
        <span className="text-[8px] text-gray-600 dark:text-gray-400 font-bold">{index + 1}</span>
      </div>
    </div>
  );
}
