import { useEffect, useRef } from 'react';
import { X, RefreshCw, Clock } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useLoanRequestMessages } from '@/hooks/useLoanRequestMessages';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { RequestActions } from './RequestActions';
import { LazyBookCover } from '@/components/books/LazyBookCover';
import type { LoanRequest } from '@/types';

interface RequestThreadProps {
  request: LoanRequest | null;
  isOpen: boolean;
  onClose: () => void;
  currentUserId: string;
  type: 'incoming' | 'outgoing';
  onAccept?: () => Promise<void>;
  onReject?: () => Promise<void>;
  isProcessing?: boolean;
}

export function RequestThread({
  request,
  isOpen,
  onClose,
  currentUserId,
  type,
  onAccept,
  onReject,
  isProcessing = false
}: RequestThreadProps) {
  const {
    thread,
    isLoading,
    error,
    sendMessage,
    refreshMessages
  } = useLoanRequestMessages(request?.id || null);
  
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Refresh messages when dialog opens
  useEffect(() => {
    if (isOpen && request) {
      refreshMessages();
    }
  }, [isOpen, request, refreshMessages]);
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current && thread?.messages.length) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-slot="scroll-area-viewport"]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [thread?.messages.length]);

  if (!request) return null;

  const isOwner = type === 'incoming';
  const isFinalStatus = ['accepted', 'rejected', 'cancelled'].includes(request.status);

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-2xl h-[80vh] flex flex-col p-0">
        {/* Header */}
        <DialogHeader className="px-6 py-4 border-b shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* Book cover thumbnail */}
              <LazyBookCover 
                coverUrl={request.book_cover_url} 
                title={request.book_title}
                className="w-12 h-16"
              />
              
              <div>
                <DialogTitle className="text-lg font-serif text-book-brown">
                  {request.book_title}
                </DialogTitle>
                <DialogDescription className="sr-only">
                  Szczegóły prośby o wypożyczenie książki {request.book_title}
                </DialogDescription>
                <p className="text-sm text-book-muted flex items-center gap-1">
                  {isOwner 
                    ? `Prośba od: ${request.borrower_name}` 
                    : `Właściciel: ${request.owner_name}`
                  }
                  <span className="mx-1">•</span>
                  <Clock className="w-3 h-3" />
                  {new Date(request.created_at).toLocaleDateString('pl-PL')}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="icon"
                onClick={refreshMessages}
                disabled={isLoading}
                className="shrink-0"
                title="Odśwież wiadomości"
              >
                <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="shrink-0"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </DialogHeader>

        {/* Messages area */}
        <ScrollArea ref={scrollAreaRef} className="flex-1 px-6 py-4">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4 text-red-600 text-sm">
              {error}
            </div>
          )}

          {isLoading && !thread ? (
            <div className="flex items-center justify-center h-32">
              <RefreshCw className="w-6 h-6 animate-spin text-book-muted" />
            </div>
          ) : (
            <MessageList 
              messages={thread?.messages || []} 
              currentUserId={currentUserId}
            />
          )}
        </ScrollArea>

        {/* Actions (for owner) or Status (for borrower) */}
        {isOwner && !isFinalStatus && (
          <div className="px-6 py-3 border-t bg-stone-50 shrink-0">
            <RequestActions
              request={request}
              onAccept={async () => {
                await onAccept?.();
                await refreshMessages();
              }}
              onReject={async () => {
                await onReject?.();
                await refreshMessages();
              }}
              isLoading={isProcessing}
            />
          </div>
        )}

        {!isOwner && !isFinalStatus && (
          <div className="px-6 py-3 border-t bg-stone-50 shrink-0 text-center">
            <p className="text-sm text-book-muted">
              Status: <span className="font-medium text-book-brown">
                {request.status === 'pending' && 'Oczekuje na decyzję właściciela'}
              </span>
            </p>
          </div>
        )}

        {isFinalStatus && (
          <div className="px-6 py-3 border-t bg-stone-50 shrink-0 text-center">
            <p className="text-sm text-book-muted">
              Prośba {request.status === 'accepted' ? 'zaakceptowana' : 
                      request.status === 'rejected' ? 'odrzucona' : 'anulowana'}
              {' - '}konwersacja zakończona
            </p>
          </div>
        )}

        {/* Message input */}
        {!isFinalStatus && (
          <div className="px-6 py-4 border-t shrink-0">
            <MessageInput
              onSend={sendMessage}
              isLoading={isLoading}
              placeholder="Napisz wiadomość..."
              disabled={isFinalStatus}
            />
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
