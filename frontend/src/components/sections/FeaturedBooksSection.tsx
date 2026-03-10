import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { BookCarousel } from '@/components/books/BookCarousel';
import { booksApi } from '@/api/books';
import { useQuery } from '@tanstack/react-query';
import type { Book } from '@/types';

// Map CommunityBook to Book type
function mapCommunityBookToBook(communityBook: any): Book {
  return {
    id: communityBook.id,
    title: communityBook.title,
    author: communityBook.author,
    isbn: communityBook.isbn,
    description: communityBook.description,
    cover_url: communityBook.cover_url,
    status: communityBook.status as any,
    is_lendable: communityBook.is_lendable,
    owner_id: communityBook.owner_id,
    owner: communityBook.owner_name ? {
      id: String(communityBook.owner_id),
      first_name: communityBook.owner_name.split(' ')[0] || '',
      last_name: communityBook.owner_name.split(' ')[1] || '',
      location: null,
    } : undefined,
    genre: undefined, // CommunityBook doesn't have genre yet
    publisher: communityBook.publisher || null,
    publication_year: communityBook.publication_year || null,
    created_at: communityBook.created_at,
    updated_at: communityBook.updated_at,
  };
}

// Shuffle array using Fisher-Yates algorithm
function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

export function FeaturedBooksSection() {
  const navigate = useNavigate();

  // Fetch real books from API with caching
  const { data: communityBooksData, isLoading, error } = useQuery({
    queryKey: ['communityBooks', 1, 20],
    queryFn: () => booksApi.getCommunityBooks(1, 20),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    gcTime: 10 * 60 * 1000,   // Keep in garbage collector for 10 minutes
    refetchOnWindowFocus: false, // Don't refetch when user returns to tab
  });

  const books = useMemo(() => {
    // API returns { success: true, data: CommunityBook[], message: ... }
    const booksArray = communityBooksData?.data;
    if (!booksArray || !Array.isArray(booksArray)) return [];
    return booksArray.map(mapCommunityBookToBook);
  }, [communityBooksData]);

  // Get 15 random books
  const randomBooks = useMemo(() => {
    return shuffleArray(books).slice(0, 15);
  }, [books]);

  const handleBookClick = (book: Book) => {
    navigate(`/books/${book.id}`);
  };

  return (
    <section id="featured-books" className="py-20 section-padding">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-12">
          <span className="inline-block px-4 py-1 bg-book-gold/10 text-book-gold text-sm font-medium rounded-full mb-4">
            Odkrywaj
          </span>
          <h2 className="font-serif text-4xl md:text-5xl font-bold text-book-brown mb-4">
            Polecane książki
          </h2>
          <p className="text-book-gray max-w-2xl mx-auto">
            Przeglądaj dostępne książki w naszej społeczności. 
            Znajdź coś dla siebie i wypożycz od znajomych.
          </p>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-20">
            <Loader2 className="w-10 h-10 animate-spin text-book-gold" />
            <span className="ml-3 text-book-gray">Ładowanie książek...</span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="text-center py-12">
            <p className="text-red-500 mb-2">Błąd podczas ładowania książek</p>
            <p className="text-book-muted text-sm">Spróbuj odświeżyć stronę</p>
          </div>
        )}

        {/* Books Carousel */}
        {!isLoading && !error && (
          <BookCarousel
            title="Dostępne do wypożyczenia"
            books={randomBooks}
            showViewAll={false}
            onBookClick={handleBookClick}
          />
        )}

        {/* View All Button */}
        {!isLoading && !error && randomBooks.length > 0 && (
          <div className="text-center mt-8">
            <Button
              onClick={() => navigate('/browse')}
              className="bg-book-gold hover:bg-book-gold-hover text-white px-8 py-6 text-lg"
            >
              Zobacz wszystkie książki
            </Button>
          </div>
        )}
      </div>
    </section>
  );
}
