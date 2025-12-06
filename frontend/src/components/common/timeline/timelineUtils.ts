import { 
  CheckCircle2,
  Clock,
  Send,
  Loader,
  Search,
  MapPin,
  Mail,
  FileText,
  AlertCircle
} from "lucide-react";

export const getTaskIcon = (taskName: string) => {
  const normalized = taskName.toLowerCase();
  
  if (normalized.includes("search") || normalized.includes("suche")) return Search;
  if (normalized.includes("locate") || normalized.includes("standort")) return MapPin;
  if (normalized.includes("email") || normalized.includes("mail")) return Mail;
  if (normalized.includes("document") || normalized.includes("dokument")) return FileText;
  if (normalized.includes("error") || normalized.includes("fehler")) return AlertCircle;
  if (normalized.includes("verify") || normalized.includes("prüf")) return CheckCircle2;
  
  return Clock; 
};

export const getStatusDisplay = (status: string): { label: string; color: string; icon: any } => {
  const statusMap: Record<string, { label: string; color: string; icon: any }> = {
    pending: { label: "Pending", color: "#9CA3AF", icon: Clock },
    working: { label: "Running", color: "#3B82F6", icon: Loader },
    sent: { label: "Sent", color: "#8B5CF6", icon: Send },
    completed: { label: "Done", color: "#10B981", icon: CheckCircle2 },
    active: { label: "Running", color: "#3B82F6", icon: Loader },
  };

  return statusMap[status] || statusMap.pending;
};

export const getTaskColor = (taskName: string): string => {
  const normalized = taskName.toLowerCase();
  
  if (normalized.includes("search") || normalized.includes("suche")) return "#3B82F6";
  if (normalized.includes("locate") || normalized.includes("standort")) return "#10B981";
  if (normalized.includes("email") || normalized.includes("mail")) return "#8B5CF6";
  if (normalized.includes("document")) return "#F59E0B";
  if (normalized.includes("error") || normalized.includes("fehler")) return "#EF4444";
  if (normalized.includes("verify")) return "#14B8A6";
  
  return "#6B7280";
};

export const getAgentColor = (agentName: string | undefined): string => {
  if (!agentName) return "#6B7280"; // Default gray
  
  const normalized = agentName.toLowerCase();
  
  // Agent-spezifische Farben
  if (normalized.includes("ki clone") || normalized.includes("chatbot")) return "#3B82F6"; // Blau
  if (normalized.includes("repair") || normalized.includes("werkstatt")) return "#10B981"; // Grün
  if (normalized.includes("lawyer") || normalized.includes("anwalt")) return "#8B5CF6"; // Lila
  if (normalized.includes("insurance") || normalized.includes("versicherung")) return "#F59E0B"; // Orange
  if (normalized.includes("guardrails")) return "#EF4444"; // Rot
  
  return "#6B7280"; // Default gray
};

export const formatTime = (timestamp: string | Date) => {
  const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
  
  // Stelle sicher, dass die Zeit in der lokalen Zeitzone angezeigt wird
  return date.toLocaleTimeString('de-DE', { 
    hour: '2-digit', 
    minute: '2-digit',
    timeZone: 'Europe/Berlin'  // Deutsche Zeitzone
  });
};
