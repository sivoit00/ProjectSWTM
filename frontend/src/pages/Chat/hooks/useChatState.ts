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
  agentSteps?: TimelineEvent[] 
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

  // Lade Chat-History und Timeline beim Start
  useEffect(() => {
    loadChatHistory();
    const savedSteps = localStorage.getItem(`timeline_${userId}`);
    if (savedSteps) {
      try {
        setAllAgentSteps(JSON.parse(savedSteps));
      } catch (e) {
        console.error("Failed to load timeline from localStorage", e);
      }
    }
  }, [userId]);

  // Clear Chat Trigger von Sidebar
  useEffect(() => {
    if (clearChatTrigger > 0) {
      handleClearChat();
    }
  }, [clearChatTrigger]);

  // Speichere Timeline in localStorage
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
    
    try {
      await api.chat.clearHistory(userId);
    } catch (error) {
      console.error("Failed to clear chat history:", error);
    }
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
    } catch (error) {
      console.error("Failed to load chat history:", error);
    }
  };

  const saveMessageToHistory = async (sender: "User" | "Bot", message: string) => {
    try {
      await api.chat.saveMessage({
        user_id: userId,
        sender,
        message,
      });
    } catch (error) {
      console.error("Failed to save message:", error);
    }
  };

  const handleSend = async () => {
    if ((!input.trim() && selectedFiles.length === 0) || loading) return;

    const userMessage = input.trim();
    let uploadedFileNames: string[] = [];

    setLoading(true);

    try {
      if (selectedFiles.length > 0) {
        const uploadResponse = await api.files.upload(selectedFiles);
        uploadedFileNames = uploadResponse.data.files.map((f: any) => f.stored_filename);
        setSelectedFiles([]);
        setShowFileUpload(false);
      }

      const messageText = userMessage || `[${selectedFiles.length} file(s) uploaded]`;
      const userMsgId = `msg-${Date.now()}-user`;
      setMessages((prev) => [...prev, { id: userMsgId, sender: "User", text: messageText, files: uploadedFileNames }]);
      setInput("");

      await saveMessageToHistory("User", messageText);

      const res = await api.sendToKI({ message: userMessage });
      
      const answer = res.data?.response ?? "No response received";
      const agentSteps = (res.data as any)?.agent_steps || [];
      
      console.log("🔍 Backend Response:", res.data);
      console.log("🔍 Agent Steps received:", agentSteps);
      
      const botMsgId = `msg-${Date.now()}-bot`;
      
      // Verknüpfe Timeline-Events mit Message-ID
      const stepsWithMsgId = agentSteps.map((step: any) => ({
        ...step,
        messageId: botMsgId
      }));
      
      console.log("🔍 Steps with MsgId:", stepsWithMsgId);
      
      setAllAgentSteps((prev) => [...prev, ...stepsWithMsgId]);
      
      setMessages((prev) => [...prev, { id: botMsgId, sender: "Bot", text: answer, agentSteps }]);
      
      await saveMessageToHistory("Bot", answer);

    } catch (err) {
      console.error("Chat error:", err);
      const errorMsg = "Sorry, I encountered an error. Please try again.";
      setMessages((prev) => [...prev, { id: `msg-${Date.now()}-error`, sender: "Bot", text: errorMsg }]);
      await saveMessageToHistory("Bot", errorMsg);
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
