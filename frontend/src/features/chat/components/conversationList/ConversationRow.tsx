import React from "react";
import { MoreVertical } from "lucide-react";

interface ConversationRowProps {
  id: string;
  label: string;
  isSelected: boolean;
  isEditing: boolean;
  editingTitle: string;
  menuOpen: boolean;
  onSelect: () => void;
  onToggleMenu: () => void;
  onEditingTitleChange: (value: string) => void;
  onSaveEditing: () => void;
  onCancelEditing: () => void;
  renderMenu: () => React.ReactNode;
}

export function ConversationRow({
  label,
  isSelected,
  isEditing,
  editingTitle,
  menuOpen,
  onSelect,
  onToggleMenu,
  onEditingTitleChange,
  onSaveEditing,
  onCancelEditing,
  renderMenu,
}: ConversationRowProps) {
  return (
    <div
      className={`group relative flex items-start gap-2 px-3 py-2.5 rounded-lg transition-colors cursor-pointer ${
        isSelected ? "bg-gray-200 dark:bg-gray-700/70" : "hover:bg-gray-100 dark:hover:bg-gray-700/30"
      }`}
      onClick={() => !isEditing && onSelect()}
    >
      <div className="flex-1 min-w-0">
        {isEditing ? (
          <input
            className="w-full bg-white text-gray-900 border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700"
            autoFocus
            value={editingTitle}
            onChange={(e) => onEditingTitleChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") onSaveEditing();
              if (e.key === "Escape") onCancelEditing();
            }}
            onBlur={onSaveEditing}
            onClick={(e) => e.stopPropagation()}
          />
        ) : (
          <div className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
            {label}
          </div>
        )}
      </div>

      {!isEditing && (
        <div className="relative">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleMenu();
            }}
            className={`p-1.5 rounded-md transition-opacity ${
              menuOpen || isSelected ? "opacity-100" : "opacity-0 group-hover:opacity-100"
            } hover:bg-gray-200 dark:hover:bg-gray-600/50`}
          >
            <MoreVertical size={16} className="text-gray-600 dark:text-gray-300" />
          </button>

          {menuOpen && (
            <div onClick={(e) => e.stopPropagation()}>
              {renderMenu()}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
