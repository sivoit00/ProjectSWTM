export const ACTIVE_CONVERSATION_CHANGED_EVENT = "activeConversationChanged";
export const CONVERSATION_LIST_CHANGED_EVENT = "conversationListChanged";

export function activeConversationStorageKey(userId: string) {
  return `active_conversation_${userId}`;
}

export function getSavedActiveConversationId(userId: string): string | null {
  try {
    return localStorage.getItem(activeConversationStorageKey(userId));
  } catch {
    return null;
  }
}

export function saveActiveConversationId(userId: string, conversationId: string) {
  try {
    localStorage.setItem(activeConversationStorageKey(userId), conversationId);
  } catch {
    return;
  }
}

export function emitActiveConversationChanged(conversationId: string) {
  window.dispatchEvent(
    new CustomEvent(ACTIVE_CONVERSATION_CHANGED_EVENT, {
      detail: { conversationId },
    })
  );
}

export function emitConversationListChanged() {
  window.dispatchEvent(new CustomEvent(CONVERSATION_LIST_CHANGED_EVENT));
}
