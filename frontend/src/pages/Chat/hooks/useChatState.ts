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
        setAllAgentSteps(JSON.parse(savedSteps));
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

  const saveMessageToHistory = async (
    sender: "User" | "Bot",
    message: string
  ) => {
    try {
      await api.chat.saveMessage({ user_id: userId, sender, message });
    } catch (error) {
      console.error("Save Message Error:", error);
    }
  };

  const cleanInput = (value: any): string => {
    if (typeof value === "string") return value;
    console.warn("⚠️ Event oder Objekt als Input erkannt, setze auf leeren String.");
    return "";
  };

  const handleSend = async (overrideText?: string, isSystemInjection = false) => {
    console.log("handleSend ausgelöst!", { overrideText, isSystemInjection });

    // Event-Abfangroutine → fix für den White Screen
    let safeOverride = cleanInput(overrideText);
    let safeInput = cleanInput(input);

    const textToSend = safeOverride || safeInput.trim();

    if ((!textToSend && selectedFiles.length === 0) || loading) return;

    let uploadedFileNames: string[] = [];
    
    setLoading(true);

    if (!overrideText) setInput("");

    try {
      // Falls Dateien ausgewählt wurden → hochladen
      if (selectedFiles.length > 0) {
        const uploadResponse = await api.files.upload(selectedFiles);
        uploadedFileNames = uploadResponse.data.files.map((f: any) => f.stored_filename);
        setSelectedFiles([]);
        setShowFileUpload(false);
      }

      const displayText = isSystemInjection 
        ? "E-Mail Update: Analysiere eingegangene Antwort..." 
        : (textToSend || `[${uploadedFileNames.length} file(s) uploaded]`);

      const userMsgId = `msg-${Date.now()}-user`;
      
      setMessages((prev) => [
        ...prev,
        { 
          id: userMsgId, 
          sender: "User", 
          text: displayText, 
          files: uploadedFileNames 
        }
      ]);

      saveMessageToHistory("User", displayText);

      // Backend Call (jetzt sicher!)
      console.log("Sende an Backend...");

      // garantiert dass 'message' IMMER ein string ist
      const safeMessage =
      textToSend && textToSend.trim().length > 0
        ? textToSend
        : `[${uploadedFileNames.length} Datei(en) hochgeladen]`;

      const res = await api.sendToKI({
      message: safeMessage
      });
      
      const answer = res.data?.response ?? "Keine Antwort erhalten.";
      const agentSteps = (res.data as any)?.agent_steps || [];
      
      console.log("Antwort erhalten:", answer);

      const botMsgId = `msg-${Date.now()}-bot`;
      const stepsWithMsgId = agentSteps.map((step: any) => ({ ...step, messageId: botMsgId }));
      setAllAgentSteps((prev) => [...prev, ...stepsWithMsgId]);
   
      setMessages((prev) => [
        ...prev, 
        { id: botMsgId, sender: "Bot", text: answer, agentSteps }
      ]);
      
      saveMessageToHistory("Bot", answer);

    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [
        ...prev,
        { 
          id: `msg-err-${Date.now()}`, 
          sender: "Bot", 
          text: "Entschuldigung, ein Fehler ist aufgetreten." 
        }
      ]);
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
