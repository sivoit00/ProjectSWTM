import { useState, useEffect, useRef } from "react";
import { useOutletContext } from "react-router-dom";
import { api } from "../../../services/api";
import keycloak from "../../../keycloak";
import type { TimelineEvent } from "../../../components/common/CustomerTimeline";
import type { Message } from "./chat/chatTypes";
import { appendSessionStep } from "./chat/chatUtils";
import { chatService } from "./chat/chatService";

export function useChatState() {
  const { clearChatTrigger } = useOutletContext<{ clearChatTrigger: number }>();

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [allAgentSteps, setAllAgentSteps] = useState<TimelineEvent[]>([]);
  
  const abortControllerRef = useRef<AbortController | null>(null);
  const userId = keycloak.tokenParsed?.sub || "anonymous";

  useEffect(() => {
    loadChatHistory();
    const savedSteps = localStorage.getItem(`timeline_${userId}`);
    if (savedSteps) {
      try {
        const parsed = JSON.parse(savedSteps);
        if (Array.isArray(parsed)) {
          setAllAgentSteps(parsed.filter((e: any) => e?.event_type === "agent_session"));
        }
      } catch (e) { console.error(e); }
    }
  }, [userId]);

  useEffect(() => {
    if (clearChatTrigger > 0) handleClearChat();
  }, [clearChatTrigger]);

  useEffect(() => {
    if (allAgentSteps.length > 0) {
      localStorage.setItem(`timeline_${userId}`, JSON.stringify(allAgentSteps));
    }
  }, [allAgentSteps, userId]);

  const loadChatHistory = async () => {
    try {
      const response = await api.chat.getHistory(userId);
      setMessages(response.data.messages.map((msg: any, idx: number) => ({
        id: `msg-history-${idx}`,
        sender: msg.sender,
        text: msg.message,
      })));
    } catch (e) { console.error(e); }
  };

  const handleClearChat = async () => {
    if (abortControllerRef.current) abortControllerRef.current.abort();
    setMessages([]);
    setAllAgentSteps([]);
    setInput("");
    setSelectedFiles([]);
    localStorage.removeItem(`timeline_${userId}`);
    api.chat.clearHistory(userId).catch(console.error);
  };

  const handleSend = async (overrideText?: string, isSystemInjection = false) => {
    const textInput = overrideText ?? input.trim();
    if ((!textInput && selectedFiles.length === 0) || loading) return;

    setLoading(true);
    if (!overrideText) setInput("");

    try {
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
         api.chat.saveMessage({ user_id: userId, sender: "User", message: displayText });
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
      api.chat.saveMessage({ user_id: userId, sender: "User", message: displayText });

      const botMsgId = `msg-${Date.now()}-bot`;
      const lastActiveStep = allAgentSteps.at(-1);
      let currentAgent = lastActiveStep?.agent || "chatbot";

      setMessages(prev => [...prev, { 
        id: botMsgId, sender: "Bot", text: "", isStreaming: true, agent: currentAgent 
      }]);
      setLoading(false);

      abortControllerRef.current = new AbortController();
      
      await chatService.streamMessage(finalText, abortControllerRef.current.signal, {
        
        onDelta: (text) => {
          setMessages(prev => prev.map(m => m.id === botMsgId ? { ...m, text } : m));
        },
        
        onAgentUpdate: (agent) => {
          currentAgent = agent;
        },

        onDone: (fullText, finalAgent, changed) => {
          setMessages(prev => prev.map(m => m.id === botMsgId ? { 
            ...m, isStreaming: false, agent: finalAgent 
          } : m));
          
          api.chat.saveMessage({ user_id: userId, sender: "Bot", message: fullText });

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
    handleSend,
  };
}