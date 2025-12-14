import type { TimelineEvent } from "../../../../components/common/CustomerTimeline";

export type Message = {
  id: string;
  sender: "User" | "Bot";
  text: string;
  files?: string[];
  agentSteps?: TimelineEvent[];
  agent?: string;
  isStreaming?: boolean;
};