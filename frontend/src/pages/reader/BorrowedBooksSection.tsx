import { useMemo, useCallback, memo } from 'react';
import { BookOpen, Calendar, User, ArrowLeft, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { 
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { useBorrowedBooks, useReturnBook } from '@/hooks/useUserBooks';

import { format, isPast } from 'date-fns';
import { pl } from 'date-fns/locale';
import type { BorrowedBook } from '@/types';
import { LazyBookCover } from '@/components/books/LazyBookCover';

function formatDate(dateString: string): string {
  return format(new Date(dateString), 'dd.MM.yyyy');
}

function formatRelative(dateString: string): string {
  const date = new Date(dateString);
  if (isPast(date)) {
    return 'Zaległa';
  }
  return format(date, 'dd MMM', { locale: pl });
}

function isOverdue(dateString: string): boolean {
  return new Date(dateString) < new Date();
}

interface BorrowedBookCardProps {
  book: BorrowedBook;
  onReturn: (bookId: string) => Promise<void>;
  isReturning: boolean;
}

const BorrowedBookCard = memo(function BorrowedBookCard({ book, onReturn, isReturning }: BorrowedBookCardProps) {
  const overdue = isOverdue(book.due_date || '');

  const handleReturn = useCallback(async () => {
    await onReturn(book.id);
  }, [onReturn, book.id]);

  return (
    <Card className="overflow-hidden hover:shadow-md transition-shadow">
      <div className="flex flex-col sm:flex-row">
        {/* Cover */}
        <div className="w-full sm:w-32 h-48 sm:h-auto flex-shrink-0 p-3">
          <LazyBookCover 
            coverUrl={book.book?.cover_url} 
            title={book.book?.title || 'Książka'}
            className="w-full h-full rounded-md overflow-hidden"
          />
        </div>

        {/* Content */}
        <div className="flex-1 p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
            <div className="flex-1">
              <h3 className="font-serif font-semibold text-book-brown text-lg mb-1">
                {book.book?.title}
              </h3>
              <p className="text-book-gray mb-3">{book.book?.author}</p>

              {/* Owner */}
              <div className="flex items-center gap-2 text-sm text-book-muted mb-3">
                <User className="w-4 h-4" />
                <span>Właściciel: </span>
                <span className="font-medium text-book-brown">{book.owner?.name || 'Nieznany'}</span>
              </div>

              {/* Dates */}
              <div className="flex flex-wrap gap-4 text-sm">
                <div className="flex items-center gap-1 text-book-muted">
                  <Calendar className="w-4 h-4" />
                  <span>Wypożyczono: {formatDate(book.borrowed_at || '')}</span>
                </div>
                <div className={`flex items-center gap-1 ${overdue ? 'text-red-600 font-medium' : 'text-book-muted'}`}>
                  <BookOpen className="w-4 h-4" />
                  <span>Termin zwrotu: {formatDate(book.due_date || '')}</span>
                  <Badge variant={overdue ? 'destructive' : 'secondary'} className="text-xs">
                    {formatRelative(book.due_date || '')}
                  </Badge>
                </div>
              </div>
            </div>

            {/* Return Button */}
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button 
                  variant={overdue ? 'destructive' : 'outline'}
                  className={overdue ? '' : 'border-book-gold text-book-gold hover:bg-book-gold/10'}
                  disabled={isReturning}
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Zwróć książkę
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Zwrócić książkę?</AlertDialogTitle>
                  <AlertDialogDescription>
                    Czy na pewno chcesz zwrócić "{book.book?.title}"? 
                    Właściciel zostanie powiadomiony o zwrocie.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Anuluj</AlertDialogCancel>
                  <AlertDialogAction 
                    onClick={handleReturn}
                    className="bg-book-gold hover:bg-book-gold-hover"
                    disabled={isReturning}
                  >
                    {isReturning ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      'Zwróć książkę'
                    )}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>
      </div>
    </Card>
  );
});

export function BorrowedBooksSection() {
  const { data: borrowedBooks = [], isLoading, error, refetch } = useBorrowedBooks();
  const returnBook = useReturnBook();

  // Sort by due date (overdue first, then by date)
  const sortedBooks = useMemo(() => {
    return [...borrowedBooks].sort((a, b) => {
      const aOverdue = isOverdue(a.due_date || '');
      const bOverdue = isOverdue(b.due_date || '');
      
      if (aOverdue && !bOverdue) return -1;
      if (!aOverdue && bOverdue) return 1;
      
      return new Date(a.due_date || '').getTime() - new Date(b.due_date || '').getTime();
    });
  }, [borrowedBooks]);

  const overdueCount = useMemo(() => {
    return borrowedBooks.filter(b => isOverdue(b.due_date || '')).length;
  }, [borrowedBooks]);

  const handleReturn = useCallback(async (bookId: string) => {
    try {
      console.log('[BorrowedBooks] Returning book:', bookId);
      await returnBook.mutateAsync(bookId);
      console.log('[BorrowedBooks] Return mutation completed');
      toast.success('Książka została zwrócona pomyślnie');
      
      // Wymuś odświeżenie listy
      console.log('[BorrowedBooks] Refetching list...');
      await refetch();
      console.log('[BorrowedBooks] Refetch completed');
    } catch (error) {
      console.error('[BorrowedBooks] Return error:', error);
      toast.error(error instanceof Error ? error.message : 'Nie udało się zwrócić książki');
    }
  }, [returnBook, refetch]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-serif font-bold text-book-brown">Wypożyczone od innych</h1>
        <p className="text-book-muted mt-1">
          Książki, które wypożyczyłeś od innych użytkowników
        </p>
      </div>

      {/* Stats */}
      {borrowedBooks.length > 0 && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-xl p-4 border border-stone-200/60">
            <p className="text-2xl font-bold text-book-brown">{borrowedBooks.length}</p>
            <p className="text-xs text-book-muted">Aktualnie wypożyczonych</p>
          </div>
          <div className="bg-white rounded-xl p-4 border border-stone-200/60">
            <p className={`text-2xl font-bold ${overdueCount > 0 ? 'text-red-600' : 'text-green-600'}`}>
              {overdueCount}
            </p>
            <p className="text-xs text-book-muted">Zaległych do zwrotu</p>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm">
          {error instanceof Error ? error.message : String(error)}
        </div>
      )}

      {/* Books List */}
      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl h-40 animate-pulse" />
          ))}
        </div>
      ) : borrowedBooks.length === 0 ? (
        <div className="bg-white rounded-xl p-12 border border-stone-200/60 text-center">
          <BookOpen className="w-12 h-12 text-stone-300 mx-auto mb-4" />
          <h3 className="font-serif font-semibold text-book-brown mb-2">
            Brak wypożyczonych książek
          </h3>
          <p className="text-book-muted text-sm">
            Nie masz aktualnie żadnych książek wypożyczonych od innych. 
            Przeglądaj dostępne pozycje i wypożycz coś dla siebie!
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {sortedBooks.map((book) => (
            <BorrowedBookCard 
              key={book.id} 
              book={book} 
              onReturn={handleReturn}
              isReturning={returnBook.isPending}
            />
          ))}
        </div>
      )}
    </div>
  );
}
