import { CheckCircle2 } from "lucide-react";

interface TimelineItemStatusIndicatorsProps {
  status: string;
  isActive: boolean;
  isCompleted: boolean;
  agentColor: string;
}

export default function TimelineItemStatusIndicators({
  status,
  isActive,
  isCompleted,
  agentColor,
}: TimelineItemStatusIndicatorsProps) {
  return (
    <>
      {isActive && (
        <div className="mt-1.5 flex items-center gap-1.5 animate-pulse">
          <div className="relative">
            <div
              className="w-1.5 h-1.5 rounded-full animate-ping"
              style={{ backgroundColor: agentColor }}
            ></div>
            <div
              className="w-1.5 h-1.5 rounded-full absolute top-0 left-0"
              style={{ backgroundColor: agentColor }}
            ></div>
          </div>
          <span className="text-[10px] font-medium" style={{ color: agentColor }}>
            Processing...
          </span>
        </div>
      )}

      {isCompleted && (
        <div className="mt-1.5 flex items-center gap-1.5">
          <CheckCircle2 size={12} className="text-green-400" />
          <span className="text-[10px] text-green-400 font-medium">Done</span>
        </div>
      )}

      {status === "pending" && (
        <div className="mt-1.5 flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-yellow-400"></div>
          <span className="text-[10px] text-yellow-400 font-medium">Waiting...</span>
        </div>
      )}
    </>
  );
}
