import { memo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, User as UserIcon, Calendar, HandHelping } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useAuth } from '@/components/auth/AuthContext';
import type { Book } from '@/types';
import { LazyBookCover } from '@/components/books/LazyBookCover';
import { statusConfig } from '@/lib/data';

interface BookCardProps {
  book: Book;
  onRequestBorrow: (book: Book) => void;
}

const BookCard = memo(function BookCard({ book, onRequestBorrow }: BookCardProps) {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const status = statusConfig[book.status];
  const isAvailable = book.status === 'available' && book.is_lendable && book.user_book_id;

  const handleCardClick = () => {
    navigate(`/books/${book.id}`);
  };

  const handleRequestClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (book.status === 'available' && book.is_lendable) {
      onRequestBorrow(book);
    }
  };

  return (
    <div 
      onClick={handleCardClick}
      className="group bg-white rounded-xl shadow-sm border border-stone-200/60 overflow-hidden hover:shadow-book transition-all duration-300 hover:-translate-y-1 cursor-pointer"
    >
      {/* Cover */}
      <div className="relative aspect-[3/4] overflow-hidden bg-stone-100">
        <LazyBookCover 
          coverUrl={book.cover_url} 
          title={book.title}
          className="w-full h-full group-hover:scale-105 transition-transform duration-500"
        />
        <div className="absolute top-3 left-3">
          <Badge variant="outline" className={status.className}>
            {status.label}
          </Badge>
        </div>
        {!book.is_lendable && (
          <div className="absolute top-3 right-3">
            <Badge variant="outline" className="bg-stone-100 text-stone-600 border-stone-200">
              Prywatna
            </Badge>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-4">
        <h3 className="font-serif font-semibold text-book-brown line-clamp-1 mb-1 group-hover:text-book-gold transition-colors">
          {book.title}
        </h3>
        <p className="text-sm text-book-gray line-clamp-1 mb-2">
          {book.author}
        </p>

        {/* Owner info */}
        {book.owner && (
          <div className="flex items-center gap-1.5 text-xs text-book-muted mb-3">
            <UserIcon className="w-3.5 h-3.5" />
            <span className="line-clamp-1">
              {book.owner.first_name} {book.owner.last_name}
            </span>
          </div>
        )}

        {/* Genre & Year */}
        <div className="flex items-center gap-2 mb-4">
          {book.genre && (
            <span className="text-xs px-2 py-0.5 bg-stone-100 text-book-gray rounded-full">
              {book.genre}
            </span>
          )}
          {book.published_date && (
            <span className="text-xs px-2 py-0.5 bg-stone-100 text-book-gray rounded-full flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {new Date(book.published_date).getFullYear()}
            </span>
          )}
        </div>

        {/* Action Button - only for authenticated users */}
        {isAuthenticated ? (
          <Button
            onClick={handleRequestClick}
            disabled={!isAvailable}
            className="w-full"
            variant={isAvailable ? 'default' : 'outline'}
            size="sm"
          >
            <HandHelping className="w-4 h-4 mr-2" />
            {isAvailable ? 'Poproś o wypożyczenie' : 'Niedostępna'}
          </Button>
        ) : (
          <Button
            onClick={() => navigate('/login')}
            className="w-full"
            variant="outline"
            size="sm"
          >
            Zaloguj się, aby wypożyczyć
          </Button>
        )}
      </div>
    </div>
  );
});

interface BookGridProps {
  books: Book[];
  isLoading: boolean;
  onRequestBorrow: (book: Book) => void;
}

export function BookGrid({ books, isLoading, onRequestBorrow }: BookGridProps) {
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  
  // Remove duplicates based on book id
  const uniqueBooks = books.filter((book, index, self) => 
    index === self.findIndex((b) => b.id === book.id)
  );

  const handleRequestClick = (book: Book) => {
    if (book.status === 'available' && book.is_lendable && book.user_book_id) {
      setSelectedBook(book);
    }
  };

  const handleConfirmRequest = () => {
    if (selectedBook) {
      onRequestBorrow(selectedBook);
      setSelectedBook(null);
    }
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="bg-white rounded-xl border border-stone-200/60 overflow-hidden">
            <Skeleton className="aspect-[3/4] w-full" />
            <div className="p-4 space-y-3">
              <Skeleton className="h-5 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
              <Skeleton className="h-9 w-full" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (uniqueBooks.length === 0) {
    return (
      <div className="bg-white rounded-xl p-12 border border-stone-200/60 text-center">
        <BookOpen className="w-16 h-16 text-stone-200 mx-auto mb-4" />
        <h3 className="font-serif font-semibold text-book-brown text-xl mb-2">
          Nie znaleziono książek
        </h3>
        <p className="text-book-muted max-w-md mx-auto">
          Spróbuj zmienić filtry wyszukiwania lub wróć później, gdy pojawią się nowe książki.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
        {uniqueBooks.map((book) => (
          <BookCard key={book.id} book={book} onRequestBorrow={handleRequestClick} />
        ))}
      </div>

      {/* Borrow Request Dialog */}
      <Dialog open={!!selectedBook} onOpenChange={() => setSelectedBook(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="font-serif">Poproś o wypożyczenie</DialogTitle>
            <DialogDescription>
              Wyślij prośbę o wypożyczenie książki do właściciela.
            </DialogDescription>
          </DialogHeader>

          {selectedBook && (
            <div className="flex gap-4 py-4">
              <LazyBookCover 
            coverUrl={selectedBook.cover_url} 
            title={selectedBook.title}
            className="w-20 h-28 rounded-lg shadow-sm"
          />
              <div>
                <h4 className="font-serif font-semibold text-book-brown">
                  {selectedBook.title}
                </h4>
                <p className="text-sm text-book-gray">{selectedBook.author}</p>
                {selectedBook.owner && (
                  <p className="text-sm text-book-muted mt-1">
                    Właściciel: {selectedBook.owner.first_name} {selectedBook.owner.last_name}
                  </p>
                )}
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedBook(null)}>
              Anuluj
            </Button>
            <Button
              onClick={handleConfirmRequest}
              className="bg-book-gold hover:bg-book-gold-hover text-white"
            >
              <HandHelping className="w-4 h-4 mr-2" />
              Wyślij prośbę
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
