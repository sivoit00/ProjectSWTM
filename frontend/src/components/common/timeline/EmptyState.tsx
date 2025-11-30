import { Clock } from "lucide-react";

export default function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-gray-500">
      <div className="relative">
        <Clock size={24} className="mb-2 opacity-40" />
        <div className="absolute -top-1 -right-1 w-2 h-2 bg-gray-700 rounded-full animate-ping"></div>
      </div>
      <p className="text-xs font-medium">Warte auf Aktivität</p>
      <p className="text-[10px] mt-1 text-gray-600">
        Agenten bereit für Ihre Anfrage
      </p>
    </div>
  );
}
