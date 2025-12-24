import * as React from "react";
import { MoreVertical, Pencil, Trash2, Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { api } from "../../../services/api";
import type { ChatConversationListItem } from "../conversations/conversationTypes";
import {
  emitActiveConversationChanged,
  emitConversationListChanged,
  getSavedActiveConversationId,
  saveActiveConversationId,
} from "../conversations/conversationSync";
import { normalizeConversationList } from "../conversations/conversationUtils";

interface ChatSidebarSectionProps {
  userId: string;
  onNewChat?: () => void;
}

export function ChatSidebarSection({ userId, onNewChat }: ChatSidebarSectionProps) {
  const navigate = useNavigate();

  const [conversations, setConversations] = React.useState<ChatConversationListItem[]>([]);
  const [activeConversationId, setActiveConversationId] = React.useState<string | null>(null);
  const [editingConversationId, setEditingConversationId] = React.useState<string | null>(null);
  const [editingTitle, setEditingTitle] = React.useState<string>("");
  const [openMenuId, setOpenMenuId] = React.useState<string | null>(null);

  const formatConversationLabel = (id: string) => {
    if (!id) return "";
    return id.length > 12 ? `${id.slice(0, 8)}…${id.slice(-4)}` : id;
  };

  const loadConversations = React.useCallback(async () => {
    try {
      const res = await api.chat.listConversations(userId);
      const normalized = normalizeConversationList(res.data);
      setConversations(normalized);
      return normalized;
    } catch (e) {
      console.error(e);
      setConversations([]);
      return [] as ChatConversationListItem[];
    }
  }, [userId]);

  React.useEffect(() => {
    (async () => {
      const normalized = await loadConversations();

      const savedActive = getSavedActiveConversationId(userId);
      const ids = normalized.map((c) => c.conversation_id);
      const initial = savedActive && ids.includes(savedActive) ? savedActive : ids[0] || null;

      setActiveConversationId(initial);
      if (editingConversationId && !normalized.some((c) => c.conversation_id === editingConversationId)) {
        setEditingConversationId(null);
        setEditingTitle("");
      }
    })();
  }, [loadConversations, userId, editingConversationId]);

  React.useEffect(() => {
    const handler = () => {
      loadConversations().then((normalized) => {
        const savedActive = getSavedActiveConversationId(userId);
        if (savedActive) {
          setActiveConversationId(savedActive);
        }

        if (editingConversationId && !normalized.some((c) => c.conversation_id === editingConversationId)) {
          setEditingConversationId(null);
          setEditingTitle("");
        }
      });
    };

    window.addEventListener("conversationListChanged", handler as EventListener);
    return () => window.removeEventListener("conversationListChanged", handler as EventListener);
  }, [loadConversations, userId, editingConversationId]);

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = () => setOpenMenuId(null);
    if (openMenuId) {
      document.addEventListener("click", handleClickOutside);
      return () => document.removeEventListener("click", handleClickOutside);
    }
  }, [openMenuId]);

  const handleSelectConversation = (conversationId: string) => {
    setActiveConversationId(conversationId);
    saveActiveConversationId(userId, conversationId);
    emitActiveConversationChanged(conversationId);
    navigate("/chat");
  };

  const handleNewChat = React.useCallback(async () => {
    try {
      const created = await api.chat.createSession();
      const newId = created.data.session_id;
      await api.chat.renameConversation(userId, newId, null);

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
  }, [userId, navigate]);

  React.useEffect(() => {
    if (onNewChat) {
      (window as any).__handleNewChat = handleNewChat;
    }
    return () => {
      delete (window as any).__handleNewChat;
    };
  }, [handleNewChat, onNewChat]);

  const startEditing = (conversationId: string) => {
    const existingTitle = conversations.find((c) => c.conversation_id === conversationId)?.title ?? "";
    setEditingConversationId(conversationId);
    setEditingTitle(existingTitle || "");
    setOpenMenuId(null);
  };

  const cancelEditing = () => {
    setEditingConversationId(null);
    setEditingTitle("");
  };

  const saveEditing = async (conversationId: string) => {
    try {
      const trimmed = editingTitle.trim();
      await api.chat.renameConversation(userId, conversationId, trimmed.length > 0 ? trimmed : null);
      cancelEditing();
      emitConversationListChanged();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteConversation = async (conversationId: string) => {
    const confirmed = window.confirm("Diesen Chat wirklich löschen?");
    if (!confirmed) return;

    try {
      await api.chat.deleteConversation(userId, conversationId);

      const nextList = await loadConversations();
      if (conversationId === activeConversationId) {
        const nextId = nextList.find((c) => c.conversation_id !== conversationId)?.conversation_id || null;
        if (nextId) {
          saveActiveConversationId(userId, nextId);
          setActiveConversationId(nextId);
          cancelEditing();
          emitActiveConversationChanged(nextId);
        } else {
          const created = await api.chat.createSession();
          const newId = created.data.session_id;
          await api.chat.renameConversation(userId, newId, null);

          saveActiveConversationId(userId, newId);
          setActiveConversationId(newId);
          setEditingConversationId(newId);
          setEditingTitle("");
          emitActiveConversationChanged(newId);
          emitConversationListChanged();
        }
      } else {
        emitConversationListChanged();
      }
    } catch (e) {
      console.error(e);
    }
    setOpenMenuId(null);
  };

  return (
    <div className="mt-4">
      <div className="space-y-0.5">
        {conversations.length === 0 ? (
          <div className="px-3 py-4 text-sm text-gray-600 dark:text-gray-400 text-center">Keine Chats vorhanden</div>
        ) : (
          conversations.map((c) => {
            const isSelected = c.conversation_id === activeConversationId;
            const isEditing = c.conversation_id === editingConversationId;
            const label = c.title && c.title.trim().length > 0 ? c.title : formatConversationLabel(c.conversation_id);
            const preview = c.last_message_preview || "";

            return (
              <div
                key={c.conversation_id}
                className={`group relative flex items-start gap-2 px-3 py-2.5 rounded-lg transition-colors cursor-pointer ${
                  isSelected
                    ? "bg-gray-200 dark:bg-gray-700/70"
                    : "hover:bg-gray-100 dark:hover:bg-gray-700/30"
                }`}
                onClick={() => !isEditing && handleSelectConversation(c.conversation_id)}
              >
                <div className="flex-1 min-w-0">
                  {isEditing ? (
                    <input
                      className="w-full bg-white text-gray-900 border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-800 dark:text-gray-100 dark:border-gray-600"
                      autoFocus
                      value={editingTitle}
                      onChange={(e) => setEditingTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") saveEditing(c.conversation_id);
                        if (e.key === "Escape") cancelEditing();
                      }}
                      onBlur={() => saveEditing(c.conversation_id)}
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <>
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate mb-0.5">
                        {label}
                      </div>
                      {preview && (
                        <div className="text-xs text-gray-600 dark:text-gray-400 truncate">
                          {preview}
                        </div>
                      )}
                    </>
                  )}
                </div>

                {!isEditing && (
                  <div className="relative">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setOpenMenuId(openMenuId === c.conversation_id ? null : c.conversation_id);
                      }}
                      className={`p-1.5 rounded-md transition-opacity ${
                        openMenuId === c.conversation_id || isSelected
                          ? "opacity-100"
                          : "opacity-0 group-hover:opacity-100"
                      } hover:bg-gray-200 dark:hover:bg-gray-600/50`}
                    >
                      <MoreVertical size={16} className="text-gray-600 dark:text-gray-300" />
                    </button>

                    {openMenuId === c.conversation_id && (
                      <div
                        className="absolute right-0 top-8 w-36 bg-white border border-gray-200 rounded-lg shadow-xl z-50 overflow-hidden dark:bg-gray-800 dark:border-gray-600"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            startEditing(c.conversation_id);
                          }}
                          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-900 hover:bg-gray-100 transition-colors dark:text-gray-200 dark:hover:bg-gray-700"
                        >
                          <Pencil size={14} />
                          <span>Umbenennen</span>
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteConversation(c.conversation_id);
                          }}
                          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-gray-100 transition-colors dark:text-red-400 dark:hover:bg-gray-700"
                        >
                          <Trash2 size={14} />
                          <span>Löschen</span>
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

