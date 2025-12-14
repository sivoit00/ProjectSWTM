import keycloak from "../../../../keycloak";
import type { TimelineEvent } from "../../../../components/common/CustomerTimeline";

export const getAgentDisplayName = (agent?: string) => {
  const a = (agent || "chatbot").toLowerCase();
  if (a === "lawyer") return "Lawyer Agent";
  if (a === "repair") return "Repair Agent";
  if (a === "insurance") return "Insurance Agent";
  return `${keycloak.tokenParsed?.preferred_username || "Your"} Agent`;
};

export function asText(value: any, fallback = ""): string {
  if (typeof value === "string") return value;
  try {
    return typeof value === "object" ? JSON.stringify(value) : String(value);
  } catch {
    return fallback;
  }
}

export const appendSessionStep = (
  steps: TimelineEvent[],
  agent: string,
  userText: string,
  botText: string,
  agentChanged: boolean,
  isFinal: boolean
): TimelineEvent[] => {
  const now = new Date().toISOString();
  const normalizedAgent = (agent || "chatbot").toLowerCase();
  const displayName = getAgentDisplayName(normalizedAgent);

  const next = [...steps];
  const last = next.length > 0 ? next[next.length - 1] : null;
  const lastAgent = (last?.agent || "").toLowerCase();

  const shouldStartNewSession = !last || agentChanged || lastAgent !== normalizedAgent;

  if (shouldStartNewSession && last && last.status === "working") {
    next[next.length - 1] = { ...last, status: "completed", timestamp: now } as any;
  }

  const safeUserText = asText(userText, "").trim();
  const safeBotText = asText(botText, "").trim();
  
  let newDetails = "";
  if (safeUserText) newDetails += `User: ${safeUserText}\n`;
  if (safeBotText) newDetails += `Agent: ${safeBotText}`;

  if (shouldStartNewSession) {
    const sessionId = `sess-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    next.push({
      task: "agent_session",
      timestamp: now,
      status: "working",
      description: displayName,
      agent: normalizedAgent,
      event_type: "agent_session",
      details: newDetails.trim(),
      sessionId,
    } as any);
    return next;
  }
  
  const prevDetails = last?.details || "";
  const combinedDetails = prevDetails.includes(safeUserText) 
      ? prevDetails + (safeBotText ? `\nAgent: ${safeBotText}` : "")
      : prevDetails + "\n" + newDetails;
  
  next[next.length - 1] = {
    ...(last as any),
    timestamp: now,
    details: isFinal ? combinedDetails : (last?.details || "Agent is typing..."), 
    status: "working",
  };
  
  return next;
};