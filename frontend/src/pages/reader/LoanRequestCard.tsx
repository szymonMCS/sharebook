import { memo } from 'react';
import { 
  Check, 
  X, 
  Clock, 
  AlertCircle, 
  User,
  MessageSquare,
  ChevronRight
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2 } from 'lucide-react';

import type { LoanRequest } from '@/types';
import { LazyBookCover } from '@/components/books/LazyBookCover';

interface LoanRequestCardProps {
  request: LoanRequest;
  type: 'incoming' | 'outgoing';
  onAccept?: () => void;
  onReject?: () => void;
  onCancel?: () => void;
  onClick?: () => void;
  isLoading?: boolean;
  unreadCount?: number;
}

const loanStatusConfig = {
  pending: { 
    label: 'Oczekuje', 
    color: 'bg-amber-100 text-amber-800 border-amber-200',
    icon: Clock
  },
  reserved: { 
    label: 'Zarezerwowana', 
    color: 'bg-purple-100 text-purple-800 border-purple-200',
    icon: Clock
  },
  accepted: { 
    label: 'Zaakceptowana', 
    color: 'bg-green-100 text-green-800 border-green-200',
    icon: Check
  },
  rejected: { 
    label: 'Odrzucona', 
    color: 'bg-red-100 text-red-800 border-red-200',
    icon: X
  },
  cancelled: { 
    label: 'Anulowana', 
    color: 'bg-gray-100 text-gray-800 border-gray-200',
    icon: AlertCircle
  },
};

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('pl-PL', { 
    day: 'numeric', 
    month: 'short', 
    hour: '2-digit', 
    minute: '2-digit' 
  });
}

function LoanRequestCardComponent({ 
  request, 
  type, 
  onAccept: _onAccept, 
  onReject: _onReject, 
  onCancel,
  onClick,
  isLoading = false,
  unreadCount = 0
}: LoanRequestCardProps) {
  const status = loanStatusConfig[request.status];
  const StatusIcon = status.icon;
  const isPending = request.status === 'pending' || request.status === 'reserved';

  const otherPerson = type === 'incoming' 
    ? { name: request.borrower_name, avatar: request.borrower_avatar }
    : { name: request.owner_name, avatar: request.owner_avatar };

  return (
    <Card 
      className="overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex gap-4">
          {/* Book Cover */}
          <div className="w-16 h-24 flex-shrink-0 rounded-lg overflow-hidden bg-stone-100">
            <LazyBookCover 
              coverUrl={request.book_cover_url} 
              title={request.book_title}
              className="w-full h-full"
            />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div>
                <h4 className="font-serif font-semibold text-book-brown line-clamp-1">
                  {request.book_title}
                </h4>
                <p className="text-xs text-book-muted">
                  {type === 'incoming' ? 'Prośba od:' : 'Właściciel:'}
                </p>
              </div>
              <div className="flex items-center gap-2">
                {unreadCount > 0 && (
                  <Badge className="bg-book-gold text-white">
                    {unreadCount} nowych
                  </Badge>
                )}
                <Badge variant="outline" className={status.color}>
                  <StatusIcon className="w-3 h-3 mr-1" />
                  {status.label}
                </Badge>
              </div>
            </div>

            {/* Person Info */}
            <div className="flex items-center gap-2 mt-2">
              {otherPerson.avatar ? (
                <img 
                  src={otherPerson.avatar} 
                  alt={otherPerson.name}
                  className="w-6 h-6 rounded-full"
                />
              ) : (
                <div className="w-6 h-6 rounded-full bg-stone-200 flex items-center justify-center">
                  <User className="w-3 h-3 text-stone-500" />
                </div>
              )}
              <span className="text-sm font-medium text-book-brown">
                {otherPerson.name}
              </span>
              <span className="text-xs text-book-muted">
                • {formatDate(request.created_at)}
              </span>
            </div>

            {/* Message */}
            {request.message && (
              <div className="mt-3 p-2 bg-stone-50 rounded-lg text-sm text-book-gray">
                <MessageSquare className="w-3 h-3 inline mr-1 text-book-muted" />
                {request.message}
              </div>
            )}

            {/* Reason (if rejected) */}
            {request.reason && request.status === 'rejected' && (
              <div className="mt-2 p-2 bg-red-50 rounded-lg text-sm text-red-600">
                <AlertCircle className="w-3 h-3 inline mr-1" />
                Powód: {request.reason}
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2 mt-3">
              {isPending && type === 'outgoing' && (
                <Button
                  size="sm"
                  variant="outline"
                  className="border-gray-200 text-gray-600 hover:bg-gray-50"
                  onClick={(e) => {
                    e.stopPropagation();
                    onCancel?.();
                  }}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    'Anuluj prośbę'
                  )}
                </Button>
              )}
              
              <Button
                size="sm"
                variant="outline"
                className="flex-1 border-book-brown text-book-brown hover:bg-book-brown/5"
                onClick={onClick}
              >
                <MessageSquare className="w-4 h-4 mr-1" />
                {unreadCount > 0 ? `Otwórz (${unreadCount})` : 'Otwórz konwersację'}
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export const LoanRequestCard = memo(LoanRequestCardComponent);
