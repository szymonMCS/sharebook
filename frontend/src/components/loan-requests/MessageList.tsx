import { memo } from 'react';
import { User, Info } from 'lucide-react';
import type { Message } from '@/types';

interface MessageListProps {
  messages: Message[];
  currentUserId: string;
}

function formatMessageDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('pl-PL', { 
    day: 'numeric', 
    month: 'short',
    year: date.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
  }) + ', ' + date.toLocaleTimeString('pl-PL', {
    hour: '2-digit',
    minute: '2-digit'
  });
}

function MessageListComponent({ messages, currentUserId }: MessageListProps) {
  if (messages.length === 0) {
    return (
      <div className="text-center py-8 text-book-muted">
        <p className="text-sm">Brak wiadomości</p>
        <p className="text-xs mt-1">Rozpocznij konwersację wpisując wiadomość poniżej</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {messages.map((message, index) => {
        const isSystem = message.message_type === 'system';
        const isMine = message.sender_id === currentUserId;
        const showAvatar = !isSystem && (!isMine || index === 0 || messages[index - 1].sender_id !== message.sender_id);

        if (isSystem) {
          return (
            <div key={message.id} className="flex justify-center">
              <div className="flex items-center gap-2 px-4 py-2 bg-stone-100 rounded-full text-xs text-book-muted">
                <Info className="w-3 h-3" />
                <span>{message.content}</span>
              </div>
            </div>
          );
        }

        return (
          <div 
            key={message.id} 
            className={`flex ${isMine ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex gap-2 max-w-[85%] ${isMine ? 'flex-row-reverse' : ''}`}>
              {/* Avatar - only show for first message from sender */}
              {showAvatar ? (
                <div className="flex-shrink-0">
                  {message.sender_avatar ? (
                    <img 
                      src={message.sender_avatar} 
                      alt={message.sender_name}
                      className="w-8 h-8 rounded-full object-cover"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-stone-200 flex items-center justify-center">
                      <User className="w-4 h-4 text-stone-500" />
                    </div>
                  )}
                </div>
              ) : (
                <div className="w-8 flex-shrink-0" /> // Spacer
              )}

              {/* Message bubble */}
              <div className={`flex flex-col ${isMine ? 'items-end' : 'items-start'}`}>
                {showAvatar && (
                  <span className="text-xs text-book-muted mb-1 px-1">
                    {message.sender_name}
                  </span>
                )}
                <div 
                  className={`px-4 py-2 rounded-2xl text-sm ${
                    isMine 
                      ? 'bg-book-brown text-white rounded-tr-sm' 
                      : 'bg-stone-100 text-book-gray rounded-tl-sm'
                  }`}
                >
                  {message.content}
                </div>
                <span className="text-xs text-book-muted mt-1 px-1">
                  {formatMessageDate(message.created_at)}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export const MessageList = memo(MessageListComponent);
