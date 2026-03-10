import { useMemo, memo } from 'react';
import { BookOpen, Calendar, User } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useUserBooks } from '@/hooks/useUserBooks';

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

interface LentBookCardProps {
  book: BorrowedBook;
}

const LentBookCard = memo(function LentBookCard({ book }: LentBookCardProps) {
  const overdue = isOverdue(book.due_date || '');

  return (
    <Card className="overflow-hidden hover:shadow-md transition-shadow">
      <div className="flex flex-col sm:flex-row">
        {/* Cover */}
        <div className="w-full sm:w-32 h-48 sm:h-auto flex-shrink-0 p-3">
          <LazyBookCover 
            coverUrl={book.cover_url} 
            title={book.title || 'Książka'}
            className="w-full h-full rounded-md overflow-hidden"
          />
        </div>

        {/* Content */}
        <div className="flex-1 p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
            <div className="flex-1">
              <h3 className="font-serif font-semibold text-book-brown text-lg mb-1">
                {book.title}
              </h3>
              <p className="text-book-gray mb-3">{book.author}</p>

              {/* Borrower */}
              <div className="flex items-center gap-2 text-sm text-book-muted mb-3">
                <User className="w-4 h-4" />
                <span>Pożyczający: </span>
                <div className="flex items-center gap-1">
                  {book.owner_avatar && (
                    <img 
                      src={book.owner_avatar} 
                      alt={book.owner_name}
                      className="w-5 h-5 rounded-full"
                    />
                  )}
                  <span className="font-medium text-book-brown">{book.owner_name}</span>
                </div>
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

            {/* Status Badge */}
            <div className="flex-shrink-0">
              <Badge 
                variant={overdue ? 'destructive' : 'outline'} 
                className={overdue ? '' : 'border-amber-500 text-amber-600'}
              >
                {overdue ? 'Zaległa' : 'Wypożyczona'}
              </Badge>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
});

export function LentBooksSection() {
  const { lentBooks, isLoadingLent, lentError } = useUserBooks();

  // Sort by due date (overdue first, then by date)
  const sortedBooks = useMemo(() => {
    return [...lentBooks].sort((a, b) => {
      const aOverdue = isOverdue(a.due_date || '');
      const bOverdue = isOverdue(b.due_date || '');
      
      if (aOverdue && !bOverdue) return -1;
      if (!aOverdue && bOverdue) return 1;
      
      return new Date(a.due_date || '').getTime() - new Date(b.due_date || '').getTime();
    });
  }, [lentBooks]);

  const overdueCount = useMemo(() => {
    return lentBooks.filter(b => isOverdue(b.due_date || '')).length;
  }, [lentBooks]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-serif font-bold text-book-brown">Wypożyczone innym</h1>
        <p className="text-book-muted mt-1">
          Książki, które pożyczyłeś innym użytkownikom
        </p>
      </div>

      {/* Stats */}
      {lentBooks.length > 0 && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-xl p-4 border border-stone-200/60">
            <p className="text-2xl font-bold text-book-brown">{lentBooks.length}</p>
            <p className="text-xs text-book-muted">Aktualnie wypożyczonych</p>
          </div>
          <div className="bg-white rounded-xl p-4 border border-stone-200/60">
            <p className={`text-2xl font-bold ${overdueCount > 0 ? 'text-red-600' : 'text-green-600'}`}>
              {overdueCount}
            </p>
            <p className="text-xs text-book-muted">Zaległych zwrotów</p>
          </div>
        </div>
      )}

      {/* Error */}
      {lentError && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm">
          {lentError instanceof Error ? lentError.message : String(lentError)}
        </div>
      )}

      {/* Books List */}
      {isLoadingLent ? (
        <div className="space-y-4">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl h-40 animate-pulse" />
          ))}
        </div>
      ) : lentBooks.length === 0 ? (
        <div className="bg-white rounded-xl p-12 border border-stone-200/60 text-center">
          <BookOpen className="w-12 h-12 text-stone-300 mx-auto mb-4" />
          <h3 className="font-serif font-semibold text-book-brown mb-2">
            Brak wypożyczonych książek
          </h3>
          <p className="text-book-muted text-sm">
            Nie pożyczyłeś aktualnie żadnych książek innym użytkownikom. 
            Twoje książki będą tutaj widoczne, gdy ktoś je wypożyczy.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {sortedBooks.map((book) => (
            <LentBookCard key={book.id} book={book} />
          ))}
        </div>
      )}
    </div>
  );
}
