import { formatTime } from "./timelineUtils";

interface TimelineItemHeaderProps {
  description: string;
  timestamp: string | Date;
  statusLabel: string;
  statusColor: string;
  StatusIcon: any;
}

export default function TimelineItemHeader({
  description,
  timestamp,
  statusLabel,
  statusColor,
  StatusIcon,
}: TimelineItemHeaderProps) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-1.5 flex-1">
        <h4 className="text-white font-semibold text-xs">{description}</h4>

        <span
          className="flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-medium transition-all"
          style={{
            backgroundColor: `${statusColor}20`,
            color: statusColor,
          }}
        >
          <StatusIcon size={10} />
          {statusLabel}
        </span>
      </div>

      <span className="text-[10px] text-gray-500">{formatTime(timestamp)}</span>
    </div>
  );
}
