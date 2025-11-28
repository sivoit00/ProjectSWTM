import { useEffect, useState } from "react";
import { 
  MessageSquare, 
  Shield, 
  Database, 
  Scale, 
  Wrench,
  Building2,
  CheckCircle2,
  Clock
} from "lucide-react";

export interface AgentStep {
  agent: string;
  timestamp: string | Date;
  status: "active" | "completed" | "pending";
  description: string;
}

interface VisualizationProps {
  steps: AgentStep[];
}

export default function VisualizationTimeline({ steps: propSteps }: VisualizationProps) {
  const [steps, setSteps] = useState<AgentStep[]>(propSteps);

  useEffect(() => {
    setSteps(propSteps);
  }, [propSteps]);

  // Agent-Konfiguration mit Icons und Farben
  const agentConfig: Record<string, { icon: any; color: string; label: string }> = {
    chatbot: { icon: MessageSquare, color: "#D22DD8", label: "AI Chatbot" },
    guardrails: { icon: Shield, color: "#0A4BFF", label: "GuardRails" },
    lawyer: { icon: Scale, color: "#3EC764", label: "Lawyer Agent" },
    insurance: { icon: Building2, color: "#D46A29", label: "Insurance Agent" },
    repair: { icon: Wrench, color: "#A237E0", label: "Repair Agent" },
    database: { icon: Database, color: "#E6C62F", label: "Database" },
    general: { icon: MessageSquare, color: "#26B6C6", label: "General AI" },
  };

  const getAgentIcon = (agentName: string) => {
    const config = agentConfig[agentName.toLowerCase()] || agentConfig.general;
    return config.icon;
  };

  const getAgentColor = (agentName: string) => {
    const config = agentConfig[agentName.toLowerCase()] || agentConfig.general;
    return config.color;
  };

  const getAgentLabel = (agentName: string) => {
    const config = agentConfig[agentName.toLowerCase()] || agentConfig.general;
    return config.label;
  };

  const formatTime = (timestamp: string | Date) => {
    const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
    return date.toLocaleTimeString('de-DE', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 p-4">
      <div className="mb-4">
        <h3 className="text-lg font-bold text-white mb-1">Agent Timeline</h3>
        <p className="text-xs text-gray-400">
          Echtzeit-Übersicht der aktiven AI-Agenten
        </p>
      </div>

      <div className="flex-1 overflow-y-auto">
        {steps.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <Clock size={32} className="mb-2 opacity-50" />
            <p className="text-sm">Noch keine Aktivität</p>
            <p className="text-xs mt-1">Senden Sie eine Nachricht, um die Timeline zu starten</p>
          </div>
        ) : (
          <div className="relative">
            {/* Timeline-Linie */}
            <div className="absolute left-[18px] top-0 bottom-0 w-0.5 bg-gray-700"></div>

            {/* Timeline-Einträge */}
            <div className="space-y-3">
              {steps.map((step, index) => {
                const Icon = getAgentIcon(step.agent);
                const color = getAgentColor(step.agent);
                const isActive = step.status === "active";
                const isCompleted = step.status === "completed";
                const isPending = step.status === "pending";

                return (
                  <div key={index} className="relative flex items-start">
                    {/* Icon-Circle */}
                    <div
                      className={`
                        relative z-10 flex items-center justify-center w-9 h-9 rounded-full
                        ${isActive ? 'ring-2 ring-opacity-50 animate-pulse' : ''}
                        ${isCompleted ? 'bg-green-600' : isPending ? 'bg-gray-600' : ''}
                      `}
                      style={{
                        backgroundColor: isActive ? color : isCompleted ? '#16a34a' : isPending ? '#4b5563' : color,
                      }}
                    >
                      {isCompleted ? (
                        <CheckCircle2 size={18} className="text-white" />
                      ) : (
                        <Icon size={18} className="text-white" />
                      )}
                    </div>

                    {/* Content */}
                    <div className="ml-3 flex-1">
                      <div
                        className={`
                          bg-gray-800 rounded-lg p-3 border
                          ${isActive ? 'border-opacity-100 shadow-lg' : 'border-gray-700'}
                        `}
                        style={{
                          borderColor: isActive ? color : undefined,
                        }}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="text-white font-semibold text-sm">
                            {getAgentLabel(step.agent)}
                          </h4>
                          <span className="text-xs text-gray-400">
                            {formatTime(step.timestamp)}
                          </span>
                        </div>
                        <p className="text-xs text-gray-300">
                          {step.description}
                        </p>
                        {isActive && (
                          <div className="mt-2 flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-green-400 animate-ping"></div>
                            <span className="text-xs text-green-400 font-medium">
                              In Bearbeitung...
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
