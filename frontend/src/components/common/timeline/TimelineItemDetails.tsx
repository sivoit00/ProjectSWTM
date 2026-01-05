import { getDetailsLines } from "./timelineItem.utils";

interface TimelineItemDetailsProps {
  hasDetails: boolean;
  isExpanded: boolean;
  details?: string;
}

export default function TimelineItemDetails({ hasDetails, isExpanded, details }: TimelineItemDetailsProps) {
  if (!hasDetails || !isExpanded) return null;

  return (
    <div className="mt-2 border-t border-gray-200 pt-2 space-y-1 dark:border-gray-700/50">
      {getDetailsLines(details).map((line, i) => (
        <div key={i} className="text-[10px] text-gray-700 dark:text-gray-300 leading-snug">
          {line}
        </div>
      ))}
    </div>
  );
}
