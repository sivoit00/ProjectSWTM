interface TimelineItemLineProps {
  isLastItem: boolean;
}

export default function TimelineItemLine({ isLastItem }: TimelineItemLineProps) {
  if (isLastItem) return null;

  return (
    <div
      className="absolute left-3.5 top-7 w-0.5 h-full bg-gradient-to-b from-gray-700 to-transparent"
      style={{ height: "calc(100% + 8px)" }}
    />
  );
}
