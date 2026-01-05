import type { ChatConversationListItem } from "./conversationTypes";

export function normalizeConversationList(data: unknown): ChatConversationListItem[] {
  const convs = Array.isArray(data) ? data : [];
  return convs
    .filter((c: any) => c?.conversation_id)
    .map((c: any) => ({
      conversation_id: String(c.conversation_id),
      title: (c as any).title ?? null,
    }));
}
