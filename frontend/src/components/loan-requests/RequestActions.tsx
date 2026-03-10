import { memo } from 'react';
import { Check, X, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { LoanRequest } from '@/types';

interface RequestActionsProps {
  request: LoanRequest;
  onAccept: () => Promise<void>;
  onReject: () => Promise<void>;
  isLoading: boolean;
}

const statusLabels: Record<string, string> = {
  pending: 'Oczekuje',
  reserved: 'Zarezerwowana',
  accepted: 'Zaakceptowana',
  rejected: 'Odrzucona',
  cancelled: 'Anulowana'
};

function RequestActionsComponent({
  request,
  onAccept,
  onReject,
  isLoading
}: RequestActionsProps) {
  const isPending = request.status === 'pending';
  const isFinal = ['accepted', 'rejected', 'cancelled'].includes(request.status);

  if (isFinal) {
    return (
      <div className="flex items-center justify-center p-4 bg-stone-50 rounded-lg">
        <span className="text-sm text-book-muted">
          Prośba {statusLabels[request.status].toLowerCase()} - konwersacja zakończona
        </span>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Action buttons */}
      <div className="flex gap-2">
        {isPending && (
          <Button
            onClick={onAccept}
            disabled={isLoading}
            className="flex-1 bg-green-600 hover:bg-green-700 text-white"
            size="sm"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <Check className="w-4 h-4 mr-1" />
                Akceptuj
              </>
            )}
          </Button>
        )}
        
        {isPending && (
          <Button
            onClick={onReject}
            disabled={isLoading}
            variant="outline"
            className="flex-1 border-red-200 text-red-600 hover:bg-red-50"
            size="sm"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <X className="w-4 h-4 mr-1" />
                Odrzuć
              </>
            )}
          </Button>
        )}
      </div>

      <p className="text-xs text-book-muted text-center">
        Akceptacja spowoduje wypożyczenie książki temu użytkownikowi.
      </p>
    </div>
  );
}

export const RequestActions = memo(RequestActionsComponent);
