import * as React from "react";
import { Pencil, Trash2 } from "lucide-react";
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

export function ChatSidebarSection({ userId }: { userId: string }) {
  const navigate = useNavigate();

  const [conversations, setConversations] = React.useState<ChatConversationListItem[]>([]);
  const [activeConversationId, setActiveConversationId] = React.useState<string | null>(null);
  const [editingConversationId, setEditingConversationId] = React.useState<string | null>(null);
  const [editingTitle, setEditingTitle] = React.useState<string>("");

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

  const handleSelectConversation = (conversationId: string) => {
    setActiveConversationId(conversationId);
    saveActiveConversationId(userId, conversationId);
    emitActiveConversationChanged(conversationId);
    navigate("/chat");
  };

  const handleNewChat = async () => {
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
  };

  const startEditing = (conversationId: string) => {
    const existingTitle = conversations.find((c) => c.conversation_id === conversationId)?.title ?? "";
    setEditingConversationId(conversationId);
    setEditingTitle(existingTitle || "");
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
  };

  return (
    <div className="mt-4 pt-4 border-t border-gray-700">
      <div className="flex items-center justify-between px-2 mb-2">
        <div className="text-xs font-semibold tracking-wide text-gray-300">Deine Chats</div>
        <button
          onClick={handleNewChat}
          className="text-xs px-2.5 py-1.5 rounded-md border border-gray-700 bg-gray-900 text-gray-200 hover:bg-gray-800 transition-colors"
        >
          New
        </button>
      </div>

      <div className="max-h-64 overflow-y-auto rounded-lg border border-gray-700 bg-gray-900">
        {conversations.length === 0 ? (
          <div className="p-3 text-sm text-gray-400">Keine Chats</div>
        ) : (
          conversations.map((c) => {
            const isSelected = c.conversation_id === activeConversationId;
            const isEditing = c.conversation_id === editingConversationId;
            const label = c.title && c.title.trim().length > 0 ? c.title : formatConversationLabel(c.conversation_id);

            return (
              <div
                key={c.conversation_id}
                className={
                  "group flex items-center gap-2 px-3 py-2 text-sm border-b border-gray-800 transition-colors " +
                  (isSelected ? "bg-gray-800 text-white" : "text-gray-200 hover:bg-gray-800")
                }
              >
                {isEditing ? (
                  <input
                    className="flex-1 bg-gray-900 text-gray-200 border border-gray-700 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600/40"
                    autoFocus
                    value={editingTitle}
                    onChange={(e) => setEditingTitle(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") saveEditing(c.conversation_id);
                      if (e.key === "Escape") cancelEditing();
                    }}
                    onBlur={() => saveEditing(c.conversation_id)}
                  />
                ) : (
                  <button
                    onClick={() => handleSelectConversation(c.conversation_id)}
                    className="flex-1 text-left truncate"
                    title={label}
                  >
                    <span className="block truncate">{label}</span>
                  </button>
                )}

                {!isEditing && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      startEditing(c.conversation_id);
                    }}
                    className={
                      "p-1.5 rounded-md transition-colors " +
                      (isSelected ? "hover:bg-gray-700" : "opacity-0 group-hover:opacity-100 hover:bg-gray-700")
                    }
                    title="Umbenennen"
                  >
                    <Pencil size={16} />
                  </button>
                )}

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteConversation(c.conversation_id);
                  }}
                  className={
                    "p-1.5 rounded-md transition-colors " +
                    (isSelected ? "hover:bg-gray-700" : "opacity-0 group-hover:opacity-100 hover:bg-gray-700")
                  }
                  title="Chat löschen"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
