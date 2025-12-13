export const getTimelineItemAnimationDelay = (index: number) => `${index * 0.05}s`;

export const getDetailsLines = (details?: string) =>
  String(details)
    .split("\n")
    .filter((l) => l.trim().length > 0);
