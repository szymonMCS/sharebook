import { memo } from 'react';
import { User, Bot, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card } from '@/components/ui/card';
import type { BookRecommendation } from '@/types';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  recommendations?: BookRecommendation[];
}

function ChatMessageComponent({ role, content, recommendations }: ChatMessageProps) {
  const isUser = role === 'user';

  return (
    <div
      className={cn(
        'flex gap-3',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
          isUser ? 'bg-book-gold' : 'bg-gradient-to-br from-violet-500 to-purple-600'
        )}
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className={cn('flex flex-col gap-2 max-w-[85%]', isUser ? 'items-end' : 'items-start')}>
        {/* Text Message */}
        <div
          className={cn(
            'px-4 py-3 rounded-2xl text-sm leading-relaxed',
            isUser
              ? 'bg-book-gold text-white rounded-tr-sm'
              : 'bg-white border border-stone-200 text-book-brown rounded-tl-sm shadow-sm'
          )}
        >
          {content}
        </div>

        {/* Recommendations */}
        {recommendations && recommendations.length > 0 && (
          <div className="w-full mt-2">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-4 h-4 text-violet-500" />
              <span className="text-xs font-medium text-violet-600">
                Polecane książki
              </span>
            </div>
            <div className="grid gap-2">
              {recommendations.map((book) => (
                <Card
                  key={book.id}
                  className="p-3 bg-gradient-to-r from-violet-50 to-purple-50 border-violet-100 hover:shadow-md transition-shadow cursor-pointer"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-14 bg-white rounded overflow-hidden flex-shrink-0 shadow-sm">
                      <img
                        src={`https://covers.openlibrary.org/b/id/${book.id}-S.jpg`}
                        alt={book.title}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = '/placeholder-book.png';
                        }}
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-book-brown text-sm line-clamp-1">
                        {book.title}
                      </h4>
                      <p className="text-xs text-book-muted">{book.author}</p>
                      <div className="flex items-center gap-1 mt-1">
                        <div className="flex-1 h-1.5 bg-white rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-violet-500 to-purple-500 rounded-full"
                            style={{ width: `${book.score}%` }}
                          />
                        </div>
                        <span className="text-xs text-violet-600 font-medium">
                          {book.score}%
                        </span>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export const ChatMessage = memo(ChatMessageComponent);
