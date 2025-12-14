
import { useState, useEffect } from "react";
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
};

export function useChatState() {
  const { clearChatTrigger } = useOutletContext<{ clearChatTrigger: number }>();
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [allAgentSteps, setAllAgentSteps] = useState<TimelineEvent[]>([]);
  
  const userId = keycloak.tokenParsed?.sub || "anonymous";

  useEffect(() => {
    loadChatHistory();
    const savedSteps = localStorage.getItem(`timeline_${userId}`);
    if (savedSteps) {
      try {
        const parsed = JSON.parse(savedSteps);
        // Migration: wir zeigen nur Agent-Session-Events (alte noisy Events werden ignoriert)
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
    if (value === null || value === undefined) return fallback;
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
    agentChanged: boolean
  ): TimelineEvent[] => {
    const now = new Date().toISOString();
    const normalizedAgent = (agent || "chatbot").toLowerCase();
    const displayName = getAgentDisplayName(normalizedAgent);

    const next = [...steps];
    const last = next.length > 0 ? next[next.length - 1] : null;
    const lastAgent = (last?.agent || "").toLowerCase();

    const shouldStartNewSession = !last || agentChanged || lastAgent !== normalizedAgent;

    // Wenn neuer Agent startet: vorherige aktive Session abschließen
    if (shouldStartNewSession && last && last.status === "working") {
      next[next.length - 1] = { ...last, status: "completed", timestamp: now } as any;
    }

    const safeUserText = asText(userText, "");
    const safeBotText = asText(botText, "");

    const stepLines: string[] = [];
    if (safeUserText.trim()) stepLines.push(`User: ${safeUserText.trim()}`);
    if (safeBotText.trim()) stepLines.push(`Agent: ${safeBotText.trim()}`);

    if (shouldStartNewSession) {
      const sessionId = `sess-${Date.now()}-${Math.random().toString(16).slice(2)}`;
      next.push({
        task: "agent_session",
        timestamp: now,
        status: "working",
        description: displayName,
        agent: normalizedAgent,
        event_type: "agent_session",
        details: stepLines.join("\n"),
        messageId: undefined,
        sessionId,
      } as any);
      return next;
    }

    // gleiche Session: Details anhängen + Timestamp aktualisieren
    const mergedDetails = [last?.details, stepLines.join("\n")].filter(Boolean).join("\n");
    next[next.length - 1] = {
      ...(last as any),
      timestamp: now,
      description: displayName,
      details: mergedDetails,
      status: "working",
    };
    return next;
  };

  const handleClearChat = async () => {
    setMessages([]);
    setAllAgentSteps([]);
    setInput("");
    setSelectedFiles([]);
    localStorage.removeItem(`timeline_${userId}`);
    try { await api.chat.clearHistory(userId); } catch (e) { console.error(e); }
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

  const handleSend = async (overrideText?: string, isSystemInjection = false) => {
    const override = typeof overrideText === "string" ? overrideText : undefined;
    console.log("handleSend ausgelöst!", { overrideText: override, isSystemInjection });

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

      // If user sent only an audio file, transcribe it and send transcript to KI.
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

      // If the user only sent non-audio files (and no text), don't force an AI response.
      if (!finalTextToSend && uploadedFileNames.length > 0 && !isSystemInjection) {
        return;
      }

      console.log("Sende an Backend...");
      const res = await api.sendToKI({ message: finalTextToSend });
      
      const answer = asText(res.data?.response, "Keine Antwort erhalten.");
      const agentSteps = (res.data as any)?.agent_steps || [];
      const currentAgent = ((res.data as any)?.agent || "chatbot") as string;
      const agentChanged = Boolean((res.data as any)?.agent_changed);
      
      console.log("Antwort erhalten:", answer);

      const botMsgId = `msg-${Date.now()}-bot`;
      // Session-basierte Timeline: ein Eintrag pro Agent, Updates werden gesammelt
      setAllAgentSteps((prev) => appendSessionStep(
        prev,
        currentAgent,
        displayText,
        answer,
        agentChanged
      ));
   
      setMessages((prev) => [
          ...prev, 
          { id: botMsgId, sender: "Bot", text: answer, agentSteps, agent: currentAgent }
      ]);
      
      saveMessageToHistory("Bot", answer);

    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [...prev, { 
          id: `msg-err-${Date.now()}`, 
          sender: "Bot", 
          text: "Entschuldigung, ein Fehler ist aufgetreten." 
      }]);
    } finally {
      setLoading(false);
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
