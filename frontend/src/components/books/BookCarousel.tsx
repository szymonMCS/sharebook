import { useRef, useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { BookCard } from './BookCard';
import type { Book } from '@/types';

interface BookCarouselProps {
  title: string;
  books: Book[];
  showViewAll?: boolean;
  onViewAll?: () => void;
  onBorrow?: (book: Book) => void;
  onReserve?: (book: Book) => void;
  onBookClick?: (book: Book) => void;
}

export function BookCarousel({ 
  title, 
  books, 
  showViewAll = true,
  onViewAll,
  onBorrow,
  onReserve,
  onBookClick
}: BookCarouselProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  const checkScrollability = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10);
    }
  };

  useEffect(() => {
    checkScrollability();
    const scrollEl = scrollRef.current;
    if (scrollEl) {
      scrollEl.addEventListener('scroll', checkScrollability);
      return () => scrollEl.removeEventListener('scroll', checkScrollability);
    }
  }, [books]);

  const scrollLeft = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollBy({ left: -320, behavior: 'smooth' });
    }
  };

  const scrollRight = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollBy({ left: 320, behavior: 'smooth' });
    }
  };

  if (books.length === 0) {
    return null;
  }

  return (
    <section className="py-12">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="font-serif text-3xl font-semibold text-book-brown">
            {title}
          </h2>
          <div className="w-16 h-1 bg-book-gold mt-2 rounded-full" />
        </div>
        
        <div className="flex items-center gap-4">
          {showViewAll && (
            <button 
              onClick={onViewAll}
              className="text-sm text-book-gold hover:text-book-gold-hover font-medium transition-colors"
            >
              Zobacz wszystkie →
            </button>
          )}
          
          <div className="flex gap-2">
            <button
              onClick={scrollLeft}
              disabled={!canScrollLeft}
              className={`p-3 rounded-full border border-stone-300 transition-all duration-300 ${
                canScrollLeft 
                  ? 'hover:bg-book-gold hover:border-book-gold hover:text-white text-book-brown' 
                  : 'opacity-40 cursor-not-allowed text-stone-400'
              }`}
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              onClick={scrollRight}
              disabled={!canScrollRight}
              className={`p-3 rounded-full border border-stone-300 transition-all duration-300 ${
                canScrollRight 
                  ? 'hover:bg-book-gold hover:border-book-gold hover:text-white text-book-brown' 
                  : 'opacity-40 cursor-not-allowed text-stone-400'
              }`}
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Carousel */}
      <div
        ref={scrollRef}
        className="flex gap-6 overflow-x-auto scrollbar-hide pb-4 snap-x snap-mandatory"
      >
        {books.map((book, index) => (
          <div
            key={book.user_book_id || book.id}
            className="flex-shrink-0 w-64 snap-start"
            style={{
              animationDelay: `${index * 100}ms`,
            }}
          >
            <BookCard 
              book={book} 
              onBorrow={onBorrow ? () => onBorrow(book) : undefined}
              onReserve={onReserve ? () => onReserve(book) : undefined}
              onClick={onBookClick ? () => onBookClick(book) : undefined}
            />
          </div>
        ))}
      </div>
    </section>
  );
}

// Alternative: Grid view for books
interface BookGridProps {
  books: Book[];
  columns?: 2 | 3 | 4 | 5;
  onBorrow?: (book: Book) => void;
  onReserve?: (book: Book) => void;
}

export function BookGrid({ books, columns = 4, onBorrow, onReserve }: BookGridProps) {
  const gridCols = {
    2: 'grid-cols-2',
    3: 'grid-cols-2 md:grid-cols-3',
    4: 'grid-cols-2 md:grid-cols-3 lg:grid-cols-4',
    5: 'grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5',
  };

  if (books.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-stone-100 flex items-center justify-center">
          <span className="text-4xl">📚</span>
        </div>
        <h3 className="font-serif text-xl text-book-brown mb-2">
          Brak książek
        </h3>
        <p className="text-book-gray">
          Nie znaleziono książek spełniających kryteria
        </p>
      </div>
    );
  }

  return (
    <div className={`grid ${gridCols[columns]} gap-6`}>
      {books.map((book, index) => (
        <div
          key={book.user_book_id || book.id}
          className="animate-fade-in-up"
          style={{ animationDelay: `${index * 50}ms` }}
        >
          <BookCard 
            book={book} 
            onBorrow={() => onBorrow?.(book)}
            onReserve={() => onReserve?.(book)}
          />
        </div>
      ))}
    </div>
  );
}
