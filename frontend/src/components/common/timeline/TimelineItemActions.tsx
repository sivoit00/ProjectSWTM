import { ChevronDown, ChevronUp } from "lucide-react";

interface TimelineItemActionsProps {
  hasDetails: boolean;
  isExpanded: boolean;
  onToggle: (e: React.MouseEvent<HTMLButtonElement>) => void;
}

export default function TimelineItemActions({
  hasDetails,
  isExpanded,
  onToggle,
}: TimelineItemActionsProps) {
  if (!hasDetails) return null;

  return (
    <div className="mt-1 flex items-center justify-end">
      <button
        type="button"
        className="flex items-center gap-1 text-[10px] text-gray-400 hover:text-white transition-colors"
        onClick={onToggle}
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
  );
}
