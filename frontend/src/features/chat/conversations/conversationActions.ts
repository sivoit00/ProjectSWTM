import type { AxiosResponse } from "axios";
import type { ChatConversationListItem } from "./conversationTypes";
import { normalizeConversationList } from "./conversationUtils";

export interface ChatApi {
  listConversations: (userId: string) => Promise<AxiosResponse<unknown>>;
  createSession: () => Promise<AxiosResponse<{ session_id: string }>>;
  renameConversation: (userId: string, conversationId: string, title: string | null) => Promise<unknown>;
  deleteConversation: (userId: string, conversationId: string) => Promise<unknown>;
}

export async function fetchConversationList(chatApi: ChatApi, userId: string): Promise<ChatConversationListItem[]> {
  const res = await chatApi.listConversations(userId);
  return normalizeConversationList(res.data);
}

export async function createConversation(chatApi: ChatApi, userId: string): Promise<string> {
  const created = await chatApi.createSession();
  const newId = created.data.session_id;
  await chatApi.renameConversation(userId, newId, null);
  return newId;
}

export async function renameConversationTitle(
  chatApi: ChatApi,
  userId: string,
  conversationId: string,
  title: string
): Promise<void> {
  const trimmed = title.trim();
  await chatApi.renameConversation(userId, conversationId, trimmed.length > 0 ? trimmed : null);
}

export async function deleteConversationAndPickNext(
  chatApi: ChatApi,
  userId: string,
  deleteId: string,
  activeId: string | null
): Promise<{ nextActiveId: string | null; createdId: string | null; listAfterDelete: ChatConversationListItem[] }> {
  await chatApi.deleteConversation(userId, deleteId);

  const listAfterDelete = await fetchConversationList(chatApi, userId);

  if (deleteId !== activeId) {
    return { nextActiveId: null, createdId: null, listAfterDelete };
  }

  const nextActiveId = listAfterDelete.find((c) => c.conversation_id !== deleteId)?.conversation_id ?? null;
  if (nextActiveId) {
    return { nextActiveId, createdId: null, listAfterDelete };
  }

  const createdId = await createConversation(chatApi, userId);
  return { nextActiveId: createdId, createdId, listAfterDelete };
}
