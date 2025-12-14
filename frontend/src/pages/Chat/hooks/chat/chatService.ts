import { api } from "../../../../services/api";
import keycloak from "../../../../keycloak";

type StreamCallbacks = {
  onDelta: (text: string) => void;
  onAgentUpdate: (agent: string, changed: boolean) => void;
  onDone: (fullText: string, finalAgent: string, changed: boolean) => void;
  onError: (err: any) => void;
};

export const chatService = {
  async processUploads(files: File[]): Promise<{ fileNames: string[]; transcribedText?: string }> {
    if (files.length === 0) return { fileNames: [] };

    const uploadResponse = await api.files.upload(files);
    const fileNames = uploadResponse.data.files.map((f: any) => f.stored_filename);

    const audioFiles = fileNames.filter((n: string) => /\.(webm|wav|mp3|m4a|aac|ogg|mp4)$/i.test(n));
    let transcribedText: string | undefined;

    if (audioFiles.length > 0) {
      const tRes = await api.files.transcribe(audioFiles[0]);
      transcribedText = (tRes.data?.text || "").trim();
    }

    return { fileNames, transcribedText };
  },

  async streamMessage(
    message: string, 
    signal: AbortSignal, 
    callbacks: StreamCallbacks
  ) {
    const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    
    try {
      const response = await fetch(`${baseUrl}/ki-orchestrator/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${keycloak.token}`,
        },
        body: JSON.stringify({ message }),
        signal,
      });

      if (!response.body) throw new Error("No readable stream");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      
      let fullText = "";
      let currentAgent = "chatbot"; 
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
                fullText += data.delta;
                callbacks.onDelta(fullText);
              } 
              else if (data.response && (data.blocked || !fullText)) {
                fullText = data.response;
                callbacks.onDelta(fullText);
              }

              if (data.agent) {
                currentAgent = data.agent;
                callbacks.onAgentUpdate(data.agent, !!data.agent_changed);
              }
              if (data.agent_changed) agentChanged = true;

            } catch (e) { console.warn("Stream parse error", e); }
          }
        }
      }
      
      callbacks.onDone(fullText, currentAgent, agentChanged);

    } catch (err) {
      callbacks.onError(err);
    }
  }
};