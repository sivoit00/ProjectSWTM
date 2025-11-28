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

interface AgentStep {
  agent: string;
  timestamp: string;
  status: "active" | "completed" | "pending";
  description: string;
}

interface VisualizationProps {
  activeAgent?: string;
  agentHistory?: AgentStep[];
}

export default function Visualization({ activeAgent, agentHistory = [] }: VisualizationProps) {
  const [steps, setSteps] = useState<AgentStep[]>(agentHistory);

  useEffect(() => {
    if (agentHistory.length > 0) {
      setSteps(agentHistory);
    }
  }, [agentHistory]);

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

  type NodeKey = keyof typeof graphNodes;

  const graphEdges: [NodeKey, NodeKey][] = [
    ["insurance", "chatbot"],
    ["chatbot", "guard"],
    ["chatbot", "server"],
    ["chatbot", "lawyer"],
    ["chatbot", "garage"],
    ["chatbot", "sql"],
    ["insurance", "server"],
    ["insurance", "lawyer"],
    ["insurance", "sql"],
    ["server", "sql"],
    ["sql", "garage"],
    ["sql", "guard"],
    ["guard", "garage"],
    ["garage", "lawyer"],
  ];

  function edgePoint(a: GraphNode, b: GraphNode) {
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const w = a.w / 2;
    const h = a.h / 2;
    const scale = Math.max(Math.abs(dx) / w, Math.abs(dy) / h);
    return { x: a.x + dx / scale, y: a.y + dy / scale };
  }

  return (
    <div className="flex items-center justify-center p-8 bg-gray-900">
      <div className="relative w-full max-w-[650px] h-[650px] bg-gray-800/50 rounded-xl border border-gray-700">
        <svg width="100%" height="100%" viewBox="0 0 650 650" preserveAspectRatio="xMidYMid meet">
          {graphEdges.map(([a, b], i) => {
            const A = graphNodes[a];
            const B = graphNodes[b];
            const p1 = edgePoint(A, B);
            const p2 = edgePoint(B, A);
            return (
              <line
                key={i}
                x1={p1.x}
                y1={p1.y}
                x2={p2.x}
                y2={p2.y}
                stroke="#85D4E6"
                strokeWidth="3"
                strokeDasharray="6 6"
              />
            );
          })}

          {Object.values(graphNodes).map((n, i) => (
            <g key={i}>
              <rect
                x={n.x - n.w / 2}
                y={n.y - n.h / 2}
                width={n.w}
                height={n.h}
                rx="12"
                fill={n.color}
              />
              <text x={n.x} y={n.y + 4} textAnchor="middle" fontSize="14" fill="white" fontWeight="500">
                {n.label}
              </text>
            </g>
          ))}
        </svg>

        <div className="absolute bottom-4 w-full text-center text-sm text-gray-400">
          AI-system-module overview (Sprint 1)
        </div>
      </div>
    </div>
  );
}
