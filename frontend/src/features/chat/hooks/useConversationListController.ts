import * as React from "react";
import type { NavigateFunction } from "react-router-dom";
import { CONVERSATION_LIST_CHANGED_EVENT, emitActiveConversationChanged, emitConversationListChanged, getSavedActiveConversationId, saveActiveConversationId } from "../conversations/conversationSync";
import type { ChatConversationListItem } from "../conversations/conversationTypes";
import { formatConversationLabel } from "../conversations/conversationLabel";
import type { ChatApi } from "../conversations/conversationActions";
import { createConversation, deleteConversationAndPickNext, fetchConversationList, renameConversationTitle } from "../conversations/conversationActions";

export interface UseConversationListControllerArgs {
  userId: string;
  chatApi: ChatApi;
  navigate: NavigateFunction;
  confirmDelete?: (message: string) => boolean;
  enableGlobalNewChatHandler?: boolean;
}

export function useConversationListController({
  userId,
  chatApi,
  navigate,
  confirmDelete,
  enableGlobalNewChatHandler,
}: UseConversationListControllerArgs) {
  const confirmFn = confirmDelete ?? ((msg) => window.confirm(msg));

  const [conversations, setConversations] = React.useState<ChatConversationListItem[]>([]);
  const [activeConversationId, setActiveConversationId] = React.useState<string | null>(null);
  const [editingConversationId, setEditingConversationId] = React.useState<string | null>(null);
  const [editingTitle, setEditingTitle] = React.useState<string>("");
  const [openMenuId, setOpenMenuId] = React.useState<string | null>(null);

  const applyListState = React.useCallback(
    (list: ChatConversationListItem[]) => {
      setConversations(list);
      if (editingConversationId && !list.some((c) => c.conversation_id === editingConversationId)) {
        setEditingConversationId(null);
        setEditingTitle("");
      }

      const savedActive = getSavedActiveConversationId(userId);
      const ids = list.map((c) => c.conversation_id);
      const initial = savedActive && ids.includes(savedActive) ? savedActive : ids[0] || null;
      setActiveConversationId(initial);
    },
    [editingConversationId, userId]
  );

  const reloadConversations = React.useCallback(async () => {
    try {
      const list = await fetchConversationList(chatApi, userId);
      setConversations(list);
      return list;
    } catch (e) {
      console.error(e);
      setConversations([]);
      return [] as ChatConversationListItem[];
    }
  }, [chatApi, userId]);

  React.useEffect(() => {
    reloadConversations().then(applyListState).catch(console.error);
  }, [applyListState, reloadConversations]);

  React.useEffect(() => {
    const handler = () => {
      reloadConversations().then((list) => {
        setConversations(list);

        const savedActive = getSavedActiveConversationId(userId);
        if (savedActive) setActiveConversationId(savedActive);

        if (editingConversationId && !list.some((c) => c.conversation_id === editingConversationId)) {
          setEditingConversationId(null);
          setEditingTitle("");
        }
      }).catch(console.error);
    };

    window.addEventListener(CONVERSATION_LIST_CHANGED_EVENT, handler as EventListener);
    return () => window.removeEventListener(CONVERSATION_LIST_CHANGED_EVENT, handler as EventListener);
  }, [editingConversationId, reloadConversations, userId]);

  React.useEffect(() => {
    const closeMenu = () => setOpenMenuId(null);
    if (!openMenuId) return;
    document.addEventListener("click", closeMenu);
    return () => document.removeEventListener("click", closeMenu);
  }, [openMenuId]);

  const handleSelectConversation = React.useCallback(
    (conversationId: string) => {
      setActiveConversationId(conversationId);
      saveActiveConversationId(userId, conversationId);
      emitActiveConversationChanged(conversationId);
      navigate("/chat");
    },
    [navigate, userId]
  );

  const handleNewChat = React.useCallback(async () => {
    try {
      const newId = await createConversation(chatApi, userId);
      saveActiveConversationId(userId, newId);
      setActiveConversationId(newId);
      setEditingConversationId(newId);
      setEditingTitle("");
      emitConversationListChanged();
      emitActiveConversationChanged(newId);
      navigate("/chat");
    } catch (e) {
      console.error(e);
    }
  }, [chatApi, navigate, userId]);

  React.useEffect(() => {
    if (!enableGlobalNewChatHandler) return;
    const w = window as unknown as { __handleNewChat?: () => void };
    w.__handleNewChat = handleNewChat;
    return () => {
      delete w.__handleNewChat;
    };
  }, [enableGlobalNewChatHandler, handleNewChat]);

  const startEditing = React.useCallback(
    (conversationId: string) => {
      const existingTitle = conversations.find((c) => c.conversation_id === conversationId)?.title ?? "";
      setEditingConversationId(conversationId);
      setEditingTitle(existingTitle || "");
      setOpenMenuId(null);
    },
    [conversations]
  );

  const cancelEditing = React.useCallback(() => {
    setEditingConversationId(null);
    setEditingTitle("");
  }, []);

  const saveEditing = React.useCallback(async (conversationId: string) => {
    try {
      await renameConversationTitle(chatApi, userId, conversationId, editingTitle);
      cancelEditing();
      emitConversationListChanged();
    } catch (e) {
      console.error(e);
    }
  }, [cancelEditing, chatApi, editingTitle, userId]);

  const toggleMenu = React.useCallback((conversationId: string) => {
    setOpenMenuId((prev) => (prev === conversationId ? null : conversationId));
  }, []);

  const handleDeleteConversation = React.useCallback(async (conversationId: string) => {
    const confirmed = confirmFn("Diesen Chat wirklich löschen?");
    if (!confirmed) return;

    try {
      const result = await deleteConversationAndPickNext(chatApi, userId, conversationId, activeConversationId);
      setConversations(result.listAfterDelete);

      if (conversationId === activeConversationId) {
        const nextId = result.nextActiveId;
        if (nextId) {
          saveActiveConversationId(userId, nextId);
          setActiveConversationId(nextId);
          if (result.createdId) {
            setEditingConversationId(nextId);
            setEditingTitle("");
          } else {
            cancelEditing();
          }
          emitActiveConversationChanged(nextId);
        }
        emitConversationListChanged();
      } else {
        emitConversationListChanged();
      }
    } catch (e) {
      console.error(e);
    }

    setOpenMenuId(null);
  }, [activeConversationId, cancelEditing, chatApi, confirmFn, userId]);

  const rows = conversations.map((c) => {
    const id = c.conversation_id;
    const isSelected = id === activeConversationId;
    const isEditing = id === editingConversationId;
    const label = c.title && c.title.trim().length > 0 ? c.title : formatConversationLabel(id);
    const menuOpen = openMenuId === id;

    return { id, label, isSelected, isEditing, menuOpen };
  });

  return {
    rows,
    editingTitle,
    setEditingTitle,
    handleSelectConversation,
    startEditing,
    saveEditing,
    cancelEditing,
    toggleMenu,
    handleDeleteConversation,
  };
}
