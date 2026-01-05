import { useState, useEffect, useRef } from "react";
import { useOutletContext } from "react-router-dom";
import { api } from "../../../services/api";
import keycloak from "../../../keycloak";
import type { TimelineEvent } from "../../../components/common/CustomerTimeline";
import type { Message } from "./chat/chatTypes";
import { appendSessionStep } from "./chat/chatUtils";
import { chatService } from "./chat/chatService";
import type { ChatConversationListItem } from "../../../features/chat/conversations/conversationTypes";
import {
  getSavedActiveConversationId,
  emitConversationListChanged,
  saveActiveConversationId,
} from "../../../features/chat/conversations/conversationSync";
import { normalizeConversationList } from "../../../features/chat/conversations/conversationUtils";

export function useChatState() {
  const { clearChatTrigger } = useOutletContext<{ clearChatTrigger: number }>();

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [allAgentSteps, setAllAgentSteps] = useState<TimelineEvent[]>([]);
  const [conversations, setConversations] = useState<ChatConversationListItem[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  
  const abortControllerRef = useRef<AbortController | null>(null);
  const userId = keycloak.tokenParsed?.sub || "anonymous";

  const reloadConversations = async () => {
    try {
      const convRes = await api.chat.listConversations(userId);
      const normalized = normalizeConversationList(convRes.data);
      setConversations(normalized);
      return normalized;
    } catch (e) {
      console.error(e);
      return [] as ChatConversationListItem[];
    }
  };

  useEffect(() => {
    (async () => {
      try {
        const normalized = await reloadConversations();

        const savedActive = getSavedActiveConversationId(userId);
        const ids = normalized.map(c => c.conversation_id);
        const initial = (savedActive && (ids.includes(savedActive) || ids.length === 0))
          ? savedActive
          : (ids[0] || null);

        if (initial) {
          setConversationId(initial);
          return;
        }

        const created = await api.chat.createSession();
        const newId = created.data.session_id;
        await api.chat.renameConversation(userId, newId, null);

        setConversations(prev => prev.some(c => c.conversation_id === newId) ? prev : [{ conversation_id: newId, title: null }, ...prev]);
        setConversationId(newId);
      } catch (e) {
        console.error(e);
      }
    })();
  }, [userId]);

  useEffect(() => {
    const onActiveConversationChanged = (evt: any) => {
      const newId = evt?.detail?.conversationId;
      if (typeof newId === "string" && newId.length > 0) {
        setConversationId(newId);
      }
    };

    const onConversationListChanged = async () => {
      await reloadConversations();
    };

    window.addEventListener("activeConversationChanged", onActiveConversationChanged as EventListener);
    window.addEventListener("conversationListChanged", onConversationListChanged as EventListener);

    return () => {
      window.removeEventListener("activeConversationChanged", onActiveConversationChanged as EventListener);
      window.removeEventListener("conversationListChanged", onConversationListChanged as EventListener);
    };
  }, [userId]);

  useEffect(() => {
    if (!conversationId) return;

    saveActiveConversationId(userId, conversationId);
    loadChatHistory(conversationId);

    const savedSteps = localStorage.getItem(`timeline_${userId}_${conversationId}`);
    if (savedSteps) {
      try {
        const parsed = JSON.parse(savedSteps);
        if (Array.isArray(parsed)) {
          setAllAgentSteps(parsed.filter((e: any) => e?.event_type === "agent_session"));
        } else {
          setAllAgentSteps([]);
        }
      } catch (e) {
        console.error(e);
        setAllAgentSteps([]);
      }
    } else {
      setAllAgentSteps([]);
    }
  }, [conversationId, userId]);

  useEffect(() => {
    if (clearChatTrigger > 0) handleClearChat();
  }, [clearChatTrigger]);

  useEffect(() => {
    if (!conversationId) return;
    if (allAgentSteps.length > 0) {
      localStorage.setItem(`timeline_${userId}_${conversationId}`, JSON.stringify(allAgentSteps));
    } else {
      localStorage.removeItem(`timeline_${userId}_${conversationId}`);
    }
  }, [allAgentSteps, userId, conversationId]);

  const loadChatHistory = async (convId: string) => {
    try {
      const response = await api.chat.getHistory(userId, convId);
      setMessages(response.data.messages.map((msg: any, idx: number) => ({
        id: `msg-history-${idx}`,
        sender: msg.sender,
        text: msg.message,
      })));
    } catch (e) { console.error(e); }
  };

  const ensureConversationId = async () => {
    if (conversationId) return conversationId;
    const created = await api.chat.createSession();
    const newId = created.data.session_id;
    await api.chat.renameConversation(userId, newId, null);

    setConversations(prev => prev.some(c => c.conversation_id === newId) ? prev : [{ conversation_id: newId, title: null }, ...prev]);
    setConversationId(newId);
    return newId;
  };

  const handleNewChat = async () => {
    if (abortControllerRef.current) abortControllerRef.current.abort();
    setMessages([]);
    setAllAgentSteps([]);
    setInput("");
    setSelectedFiles([]);

    const created = await api.chat.createSession();
    const newId = created.data.session_id;
    await api.chat.renameConversation(userId, newId, null);

    setConversations(prev => prev.some(c => c.conversation_id === newId) ? prev : [{ conversation_id: newId, title: null }, ...prev]);
    setConversationId(newId);
  };

  const activeConversationTitle = conversationId
    ? (conversations.find(c => c.conversation_id === conversationId)?.title ?? null)
    : null;

  const renameActiveConversation = async (title: string) => {
    if (!conversationId) return;
    const trimmed = title.trim();
    const newTitle = trimmed.length > 0 ? trimmed : null;

    try {
      await api.chat.renameConversation(userId, conversationId, newTitle);
      setConversations(prev => prev.map(c =>
        c.conversation_id === conversationId ? { ...c, title: newTitle } : c
      ));
    } catch (e) {
      console.error(e);
    }
  };

  const handleClearChat = async () => {
    if (abortControllerRef.current) abortControllerRef.current.abort();
    setMessages([]);
    setAllAgentSteps([]);
    setInput("");
    setSelectedFiles([]);
    if (conversationId) {
      localStorage.removeItem(`timeline_${userId}_${conversationId}`);
      api.chat.clearHistory(userId, conversationId).catch(console.error);
    }
  };

  const handleSend = async (overrideText?: string, isSystemInjection = false) => {
    const textInput = overrideText ?? input.trim();
    if ((!textInput && selectedFiles.length === 0) || loading) return;

    setLoading(true);
    if (!overrideText) setInput("");

    try {
      const convId = await ensureConversationId();
      const { fileNames, transcribedText } = await chatService.processUploads(selectedFiles);
      setSelectedFiles([]);
      setShowFileUpload(false);

      let finalText = textInput;
      if (!isSystemInjection && !finalText && transcribedText) {
          finalText = transcribedText;
      }

      if (!finalText && fileNames.length > 0 && !transcribedText && !isSystemInjection) {
         const displayText = `[${fileNames.length} file(s) uploaded]`;
         setMessages(p => [...p, { id: `msg-${Date.now()}`, sender: "User", text: displayText, files: fileNames }]);
        await api.chat.saveMessage({ user_id: userId, sender: "User", message: displayText, conversation_id: convId });
         setLoading(false);
         return;
      }

      const displayText = isSystemInjection 
        ? "E-Mail Update: Analysiere eingegangene Antwort..." 
        : (finalText || `[${fileNames.length} file(s) uploaded]`);

      setMessages(prev => [...prev, { 
        id: `msg-${Date.now()}-user`, 
        sender: "User", 
        text: displayText, 
        files: fileNames 
      }]);
      await api.chat.saveMessage({ user_id: userId, sender: "User", message: displayText, conversation_id: convId });

      if (!isSystemInjection && finalText.trim().length > 0) {
        const currentTitle = conversations.find(c => c.conversation_id === convId)?.title;
        if (!currentTitle || currentTitle.trim().length === 0) {
          emitConversationListChanged();
        }
      }

      const botMsgId = `msg-${Date.now()}-bot`;
      const lastActiveStep = allAgentSteps.at(-1);
      let currentAgent = lastActiveStep?.agent || "chatbot";

      setMessages(prev => [...prev, { 
        id: botMsgId, sender: "Bot", text: "", isStreaming: true, agent: currentAgent 
      }]);
      setLoading(false);

      abortControllerRef.current = new AbortController();
      
      await chatService.streamMessage(finalText, convId, abortControllerRef.current.signal, {
        
        onDelta: (text) => {
          setMessages(prev => prev.map(m => m.id === botMsgId ? { ...m, text } : m));
        },
        
        onAgentUpdate: (agent, _changed) => {
          currentAgent = agent;
        },

        onDone: (fullText, finalAgent, changed) => {
          setMessages(prev => prev.map(m => m.id === botMsgId ? { 
            ...m, isStreaming: false, agent: finalAgent 
          } : m));
          
          api.chat.saveMessage({ user_id: userId, sender: "Bot", message: fullText, conversation_id: convId });

          setAllAgentSteps(prev => appendSessionStep(
            prev, finalAgent, displayText, fullText, changed, true
          ));
        },

        onError: (err: any) => {
          if (err.name !== 'AbortError') {
            console.error(err);
            setMessages(prev => [...prev, { id: `err-${Date.now()}`, sender: "Bot", text: "Fehler aufgetreten." }]);
          }
        }
      });

    } catch (e) {
      console.error(e);
      setLoading(false);
    } finally {
      abortControllerRef.current = null;
    }
  };

  return {
    messages,
    input,
    setInput,
    loading,
    showFileUpload,
    setShowFileUpload,
    selectedFiles,
    setSelectedFiles,
    allAgentSteps,
    conversations,
    conversationId,
    setConversationId,
    handleNewChat,
    activeConversationTitle,
    renameActiveConversation,
    handleSend,
  };
}