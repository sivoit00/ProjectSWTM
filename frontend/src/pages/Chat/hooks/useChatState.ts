import { useState, useEffect, useRef } from "react";
import { useOutletContext } from "react-router-dom";
import { api } from "../../../services/api";
import keycloak from "../../../keycloak";
import type { TimelineEvent } from "../../../components/common/CustomerTimeline";

export type Message = {
  id: string;
  sender: "User" | "Bot";
  text: string;
  files?: string[];
  agentSteps?: TimelineEvent[];
  agent?: string;
  isStreaming?: boolean;
};

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

  const getAgentDisplayName = (agent?: string) => {
    const a = (agent || "chatbot").toLowerCase();
    if (a === "lawyer") return "Lawyer Agent";
    if (a === "repair") return "Repair Agent";
    if (a === "insurance") return "Insurance Agent";
    return `${keycloak.tokenParsed?.preferred_username || "Your"} Agent`;
  };

  function asText(value: any, fallback = ""): string {
    if (typeof value === "string") return value;
    try {
      return typeof value === "object" ? JSON.stringify(value) : String(value);
    } catch {
      return fallback;
    }
  }

  const appendSessionStep = (
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

  const loadChatHistory = async () => {
    try {
      const response = await api.chat.getHistory(userId);
      const history = response.data.messages.map((msg: any, idx: number) => ({
        id: `msg-history-${idx}`,
        sender: msg.sender as "User" | "Bot",
        text: msg.message,
      }));
      setMessages(history);
    } catch (error) { console.error("History Load Error:", error); }
  };

  const saveMessageToHistory = async (sender: "User" | "Bot", message: string) => {
    try { await api.chat.saveMessage({ user_id: userId, sender, message }); } 
    catch (error) { console.error("Save Message Error:", error); }
  };

  const handleClearChat = async () => {
    if (abortControllerRef.current) abortControllerRef.current.abort();
    setMessages([]);
    setAllAgentSteps([]);
    setInput("");
    setSelectedFiles([]);
    localStorage.removeItem(`timeline_${userId}`);
    try { await api.chat.clearHistory(userId); } catch (e) { console.error(e); }
  };

  const handleSend = async (overrideText?: string, isSystemInjection = false) => {
    const override = typeof overrideText === "string" ? overrideText : undefined;
    const textToSend = override || input.trim();
    
    if ((!textToSend && selectedFiles.length === 0) || loading) return;

    let uploadedFileNames: string[] = [];
    setLoading(true);
    if (!override) setInput("");

    try {
      if (selectedFiles.length > 0) {
        const uploadResponse = await api.files.upload(selectedFiles);
        uploadedFileNames = uploadResponse.data.files.map((f: any) => f.stored_filename);
        setSelectedFiles([]);
        setShowFileUpload(false);
      }

      const audioFiles = uploadedFileNames.filter((n: string) => /\.(webm|wav|mp3|m4a|aac|ogg|mp4)$/i.test(n));
      let finalTextToSend = textToSend;

      if (!isSystemInjection && !finalTextToSend && audioFiles.length > 0) {
        try {
          const tRes = await api.files.transcribe(audioFiles[0]);
          finalTextToSend = (tRes.data?.text || "").trim();
        } catch (e) {
          console.error("Transcription error:", e);
          const errText = "Sprachnachricht konnte nicht transkribiert werden.";
          setMessages((prev) => [
            ...prev,
            {
              id: `msg-${Date.now()}-user`,
              sender: "User",
              text: `[${uploadedFileNames.length} file(s) uploaded]`,
              files: uploadedFileNames,
            },
            { id: `msg-err-${Date.now()}`, sender: "Bot", text: errText },
          ]);
          saveMessageToHistory("User", `[${uploadedFileNames.length} file(s) uploaded]`);
          saveMessageToHistory("Bot", errText);
          setLoading(false);
          return;
        }
      }

      const displayText = isSystemInjection 
        ? "E-Mail Update: Analysiere eingegangene Antwort..." 
        : (finalTextToSend || `[${uploadedFileNames.length} file(s) uploaded]`);

      const userMsgId = `msg-${Date.now()}-user`;
      setMessages((prev) => [...prev, { 
        id: userMsgId, 
        sender: "User", 
        text: displayText, 
        files: uploadedFileNames 
      }]);
      saveMessageToHistory("User", displayText);

      if (!finalTextToSend && uploadedFileNames.length > 0 && !isSystemInjection) {
        setLoading(false);
        return;
      }

      const botMsgId = `msg-${Date.now()}-bot`;
      const lastActiveStep = allAgentSteps.length > 0 ? allAgentSteps[allAgentSteps.length - 1] : null;
      let currentAgent = lastActiveStep?.agent || "chatbot";
      
      setMessages((prev) => [
        ...prev,
        { id: botMsgId, sender: "Bot", text: "", isStreaming: true, agent: currentAgent }
      ]);

      setLoading(false);

      abortControllerRef.current = new AbortController();
      const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
      
      const response = await fetch(`${baseUrl}/ki-orchestrator/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${keycloak.token}`,
        },
        body: JSON.stringify({ message: finalTextToSend }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.body) throw new Error("No readable stream");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      
      let botFullText = "";
      let agentChanged = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const jsonStr = line.slice(6);
              if (jsonStr === "[DONE]") continue;
              
              const data = JSON.parse(jsonStr);

              if (data.delta) {
                botFullText += data.delta;
                setMessages((prev) => 
                  prev.map((m) => m.id === botMsgId ? { ...m, text: botFullText } : m)
                );
              }

              if (data.agent) currentAgent = data.agent;
              if (data.agent_changed) agentChanged = true;

            } catch (e) { console.warn(e); }
          }
        }
      }

      setMessages((prev) => 
        prev.map((m) => m.id === botMsgId ? { ...m, isStreaming: false, agent: currentAgent } : m)
      );
      
      saveMessageToHistory("Bot", botFullText);
      
      setAllAgentSteps((prev) => appendSessionStep(
        prev,
        currentAgent,
        displayText,
        botFullText,
        agentChanged,
        true
      ));

    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error("Chat error:", err);
        setMessages((prev) => [...prev, { 
          id: `msg-err-${Date.now()}`, 
          sender: "Bot", 
          text: "Fehler aufgetreten." 
        }]);
      }
    } finally {
      setLoading(false);
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