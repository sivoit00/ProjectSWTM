import { Bot } from "lucide-react";

interface ActiveAgentHeaderProps {
  currentAgent: string;
  hasActiveEvents: boolean;
  userName?: string;
}

const getAgentDisplayName = (agentName: string, userName?: string): string => {
  const mapping: Record<string, string> = {
    chatbot: userName ? `${userName}'s Agent` : "Your Agent",
    repair: "Repair Agent",
    insurance: "Insurance Agent",
    lawyer: "Lawyer Agent",
    user: "You",
  };

  const normalized = agentName.toLowerCase();
  return mapping[normalized] || agentName;
};

export default function ActiveAgentHeader({ currentAgent, hasActiveEvents, userName }: ActiveAgentHeaderProps) {
  return (
    <div className="mb-3">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-gradient-to-br from-indigo-500 to-indigo-700 rounded-full flex items-center justify-center">
            <Bot size={12} className="text-white" />
          </div>
          <div>
            <p className="text-[10px] text-gray-500">Active Agent</p>
            <p className="text-xs font-semibold text-gray-900 dark:text-white">
              {getAgentDisplayName(currentAgent, userName)}
            </p>
          </div>
        </div>
        {hasActiveEvents && (
          <span className="flex items-center gap-1 text-[10px] text-green-400">
            <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></div>
            Live
          </span>
        )}
      </div>
      <div className="border-t border-gray-200 pt-2 dark:border-gray-800">
        <h3 className="text-xs font-bold text-gray-900 dark:text-white">Activity Timeline</h3>
        <p className="text-[10px] text-gray-600 dark:text-gray-400">What's happening right now</p>
      </div>
    </div>
  );
}
