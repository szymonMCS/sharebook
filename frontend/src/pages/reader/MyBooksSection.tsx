import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Settings2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

import { AddBookDialog } from './AddBookDialog';

import { useMyBooks } from '@/hooks/useUserBooks';
import { LazyBookCover } from '@/components/books/LazyBookCover';
import type { UserLibraryItem } from '@/types';

// Status badge component
const BookStatusBadge = ({ status }: { status: string }) => {
  const config: Record<string, { label: string; className: string }> = {
    available: { label: 'Dostępna', className: 'bg-green-100 text-green-800 border-green-200' },
    lent: { label: 'Wypożyczona', className: 'bg-amber-100 text-amber-800 border-amber-200' },
    borrowed: { label: 'Wypożyczona', className: 'bg-amber-100 text-amber-800 border-amber-200' },
    reserved: { label: 'Zarezerwowana', className: 'bg-purple-100 text-purple-800 border-purple-200' },
    unavailable: { label: 'Niedostępna', className: 'bg-gray-100 text-gray-800 border-gray-200' },
  };

  const { label, className } = config[status] || { label: status, className: 'bg-gray-100 text-gray-800' };
  return (
    <Badge variant="outline" className={className}>
      {label}
    </Badge>
  );
};

interface UserBookCardProps {
  item: UserLibraryItem;
}

const UserBookCard = ({ item }: UserBookCardProps) => {
  const navigate = useNavigate();
  const { book, status, is_lendable } = item;
  
  const handleCardClick = () => {
    // Navigate to book details using user_book.id (not book.id) to handle multiple copies
    navigate(`/books/${item.id}`);
  };

  return (
    <div 
      className="group bg-white rounded-xl shadow-sm border border-stone-200/60 overflow-hidden hover:shadow-md transition-all cursor-pointer"
      onClick={handleCardClick}
    >
      {/* Cover */}
      <div className="relative aspect-[3/4] overflow-hidden bg-stone-100">
        <LazyBookCover 
          coverUrl={book.cover_url} 
          title={book.title}
          className="w-full h-full group-hover:scale-105 transition-transform duration-300"
        />
        <div className="absolute top-3 left-3">
          <BookStatusBadge status={status} />
        </div>
        {!is_lendable && (
          <div className="absolute top-3 right-3">
            <Badge variant="outline" className="bg-stone-100 text-stone-600">
              Prywatna
            </Badge>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-4">
        <h3 className="font-serif font-semibold text-book-brown line-clamp-1 mb-1">
          {book.title}
        </h3>
        <p className="text-sm text-book-gray line-clamp-1">
          {book.author || 'Autor nieznany'}
        </p>
        {/* Status hint */}
        <div className="mt-3 pt-3 border-t border-stone-100">
          <span className="text-xs text-book-muted">
            Kliknij, aby zarządzać książką
          </span>
        </div>
      </div>
    </div>
  );
};

export function MyBooksSection() {
  const [showAddDialog, setShowAddDialog] = useState(false);
  
  const { 
    data: books = [], 
    isLoading, 
    refetch
  } = useMyBooks();

  // Stats - count both 'lent' and 'borrowed' as borrowed
  const stats = useMemo(() => {
    const total = books.length;
    const available = books.filter((b: UserLibraryItem) => b.status === 'available').length;
    const lent = books.filter((b: UserLibraryItem) => b.status === 'lent' || b.status === 'borrowed').length;
    return { total, available, lent };
  }, [books]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-serif font-bold text-book-brown">Moje książki</h1>
          <p className="text-book-muted mt-1">Zarządzaj swoją biblioteczką</p>
        </div>
        <Button 
          onClick={() => setShowAddDialog(true)}
          className="bg-book-gold hover:bg-book-gold-hover text-white"
        >
          <Plus className="w-4 h-4 mr-2" />
          Dodaj książkę
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-4 border border-stone-200/60">
          <p className="text-2xl font-bold text-book-brown">{stats.total}</p>
          <p className="text-xs text-book-muted">Wszystkich</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-stone-200/60">
          <p className="text-2xl font-bold text-green-600">{stats.available}</p>
          <p className="text-xs text-book-muted">Dostępnych</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-stone-200/60">
          <p className="text-2xl font-bold text-amber-600">{stats.lent}</p>
          <p className="text-xs text-book-muted">Wypożyczonych</p>
        </div>
      </div>

      {/* Error -->
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm">
          {error instanceof Error ? error.message : String(error)}
        </div>
      )}

      {/* Books Grid */}
      {isLoading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl h-64 animate-pulse" />
          ))}
        </div>
      ) : books.length === 0 ? (
        <div className="bg-white rounded-xl p-12 border border-stone-200/60 text-center">
          <Settings2 className="w-12 h-12 text-stone-300 mx-auto mb-4" />
          <h3 className="font-serif font-semibold text-book-brown mb-2">
            Brak książek
          </h3>
          <p className="text-book-muted text-sm mb-4">
            Dodaj swoje pierwsze książki do biblioteczki
          </p>
          <Button 
            onClick={() => setShowAddDialog(true)}
            className="bg-book-gold hover:bg-book-gold-hover text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            Dodaj książkę
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {books.map((item: UserLibraryItem) => (
            <UserBookCard 
              key={item.id} 
              item={item} 
            />
          ))}
        </div>
      )}

      {/* Add Book Dialog */}
      <AddBookDialog 
        open={showAddDialog} 
        onOpenChange={setShowAddDialog}
        onBookAdded={refetch}
      />
    </div>
  );
}
