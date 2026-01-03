import { Pencil, Trash2 } from "lucide-react";

interface ConversationRowMenuProps {
  onRename: () => void;
  onDelete: () => void;
}

export function ConversationRowMenu({ onRename, onDelete }: ConversationRowMenuProps) {
  return (
    <div className="absolute right-0 top-8 w-36 bg-white border border-gray-200 rounded-lg shadow-xl z-50 overflow-hidden dark:bg-gray-800 dark:border-gray-600">
      <button
        onClick={onRename}
        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-900 hover:bg-gray-100 transition-colors dark:text-gray-200 dark:hover:bg-gray-700"
      >
        <Pencil size={14} />
        <span>Umbenennen</span>
      </button>
      <button
        onClick={onDelete}
        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-gray-100 transition-colors dark:text-red-400 dark:hover:bg-gray-700"
      >
        <Trash2 size={14} />
        <span>Löschen</span>
      </button>
    </div>
  );
}
