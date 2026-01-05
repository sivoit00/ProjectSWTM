import { useNavigate } from "react-router-dom";
import { api } from "../../../services/api";
import { ConversationListEmpty } from "./conversationList/ConversationListEmpty";
import { ConversationRow } from "./conversationList/ConversationRow";
import { ConversationRowMenu } from "./conversationList/ConversationRowMenu";
import { useConversationListController } from "../hooks/useConversationListController";

interface ChatSidebarSectionProps {
  userId: string;
  onNewChat?: () => void;
}

export function ChatSidebarSection({ userId, onNewChat }: ChatSidebarSectionProps) {
  const navigate = useNavigate();

  const {
    rows,
    editingTitle,
    setEditingTitle,
    handleSelectConversation,
    startEditing,
    saveEditing,
    cancelEditing,
    toggleMenu,
    handleDeleteConversation,
  } = useConversationListController({
    userId,
    chatApi: api.chat,
    navigate,
    enableGlobalNewChatHandler: Boolean(onNewChat),
  });

  return (
    <div>
      <div className="space-y-0.5">
        {rows.length === 0 ? (
          <ConversationListEmpty />
        ) : (
          rows.map((r) => (
            <ConversationRow
              key={r.id}
              id={r.id}
              label={r.label}
              isSelected={r.isSelected}
              isEditing={r.isEditing}
              editingTitle={editingTitle}
              menuOpen={r.menuOpen}
              onSelect={() => handleSelectConversation(r.id)}
              onToggleMenu={() => toggleMenu(r.id)}
              onEditingTitleChange={setEditingTitle}
              onSaveEditing={() => saveEditing(r.id)}
              onCancelEditing={cancelEditing}
              renderMenu={() => (
                <ConversationRowMenu
                  onRename={() => startEditing(r.id)}
                  onDelete={() => handleDeleteConversation(r.id)}
                />
              )}
            />
          ))
        )}
      </div>
    </div>
  );
}

