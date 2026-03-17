import { useState, useMemo, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { BookOpen, ChevronLeft, ChevronRight } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';
import { GradientOrbs } from '@/components/layout/FloatingBooks';
import { BookFilters, type BrowseFilters } from '@/components/books/BookFilters';
import { BookGrid } from '@/components/books/BookGrid';
import { useCommunityBooks } from '@/hooks/useCommunityBooks';
import { useAuth } from '@/components/auth/AuthContext';
import { loansApi } from '@/api/loans';
import type { Book } from '@/types';

const ITEMS_PER_PAGE = 12;

function BrowsePageContent() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  // Initialize filters from URL
  const [filters, setFilters] = useState<BrowseFilters>({
    search: searchParams.get('search') || '',
    status: (searchParams.get('status') as BrowseFilters['status']) || 'all',
    author: searchParams.get('author') || '',
    authorSort: (searchParams.get('authorSort') as 'az' | 'za') || 'az',
  });

  const [currentPage, setCurrentPage] = useState(() => {
    const page = parseInt(searchParams.get('page') || '1', 10);
    return isNaN(page) || page < 1 ? 1 : page;
  });

  // Fetch books with pagination and filters from backend
  const { data, isLoading, error } = useCommunityBooks({
    ...filters,
    page: currentPage,
    per_page: ITEMS_PER_PAGE,
  });

  const books = data?.data || [];
  const pagination = data?.meta?.pagination;

  // Extract unique authors for filter (from current page only for performance)
  const authors = useMemo(() => {
    const authorSet = new Set<string>();
    books.forEach((book) => {
      if (book.author) {
        authorSet.add(book.author);
      }
    });
    return Array.from(authorSet).sort();
  }, [books]);

  // Update URL when filters change
  const handleFiltersChange = useCallback(
    (newFilters: BrowseFilters) => {
      setFilters(newFilters);
      setCurrentPage(1);

      const params = new URLSearchParams();
      if (newFilters.search) params.set('search', newFilters.search);
      if (newFilters.status !== 'all') params.set('status', newFilters.status);
      if (newFilters.author) params.set('author', newFilters.author);
      if (newFilters.authorSort && newFilters.authorSort !== 'az') params.set('authorSort', newFilters.authorSort);
      params.set('page', '1');
      setSearchParams(params);
    },
    [setSearchParams]
  );

  // Handle borrow request
  const handleRequestBorrow = useCallback(
    async (book: Book) => {
      if (!isAuthenticated) {
        navigate('/login', { state: { from: `/books/${book.id}` } });
        return;
      }

      if (!book.user_book_id) {
        toast.error('Błąd', {
          description: 'Nie można wysłać prośby o wypożyczenie - brak ID książki.',
        });
        return;
      }

      try {
        const response = await loansApi.createRequest(book.user_book_id);
        if (response.success) {
          toast.success('Prośba wysłana', {
            description: `Wysłano prośbę o wypożyczenie "${book.title}"`,
          });
          navigate('/reader/requests');
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Nie udało się wysłać prośby. Spróbuj ponownie.';
        toast.error('Błąd', {
          description: errorMessage,
        });
      }
    },
    [isAuthenticated, navigate]
  );

  // Handle page change
  const goToPage = useCallback((page: number) => {
    setCurrentPage(page);
    
    // Update URL
    const params = new URLSearchParams(searchParams);
    params.set('page', String(page));
    setSearchParams(params);
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [searchParams, setSearchParams]);

  // Calculate total pages from backend pagination
  const totalPages = pagination?.total_pages || 1;
  const totalBooks = pagination?.total || 0;
  const hasNext = pagination?.has_next ?? false;
  const hasPrev = pagination?.has_prev ?? false;

  return (
    <div className="min-h-screen bg-warm-beige">
      <GradientOrbs />
      <Navbar />

      <main className="relative z-10 pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-book-gold/10 flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-book-gold" />
              </div>
              <div>
                <h1 className="font-serif text-3xl sm:text-4xl font-bold text-book-brown">
                  Przeglądaj książki
                </h1>
                <p className="text-book-muted mt-1">
                  Odkryj książki dostępne do wypożyczenia od społeczności
                </p>
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="mb-8">
            <BookFilters
              filters={filters}
              onFiltersChange={handleFiltersChange}
              authors={authors}
            />
          </div>

          {/* Results count */}
          <div className="flex items-center justify-between mb-6">
            {isLoading ? (
              <Skeleton className="h-6 w-32" />
            ) : (
              <p className="text-book-muted">
                Znaleziono <span className="font-semibold text-book-brown">{totalBooks}</span> książek
                {totalPages > 1 && (
                  <span className="text-sm ml-1">
                    (strona {currentPage} z {totalPages})
                  </span>
                )}
              </p>
            )}
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm mb-6">
              {error.message || 'Wystąpił błąd podczas ładowania książek.'}
            </div>
          )}

          {/* Book Grid */}
          <BookGrid
            books={books}
            isLoading={isLoading}
            onRequestBorrow={handleRequestBorrow}
          />

          {/* Pagination */}
          {!isLoading && totalPages > 1 && (
            <div className="mt-8 flex items-center justify-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => goToPage(currentPage - 1)}
                disabled={!hasPrev}
              >
                <ChevronLeft className="w-4 h-4 mr-1" />
                Poprzednia
              </Button>

              <div className="flex items-center gap-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1)
                  .filter((page) => {
                    // Show first, last, current, and pages around current
                    return (
                      page === 1 ||
                      page === totalPages ||
                      Math.abs(page - currentPage) <= 1
                    );
                  })
                  .map((page, index, array) => {
                    // Add ellipsis where needed
                    const showEllipsis = index > 0 && page - array[index - 1] > 1;
                    return (
                      <div key={page} className="flex items-center">
                        {showEllipsis && (
                          <span className="px-2 text-book-muted">...</span>
                        )}
                        <Button
                          variant={currentPage === page ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => goToPage(page)}
                          className={
                            currentPage === page
                              ? 'bg-book-gold hover:bg-book-gold-hover text-white'
                              : ''
                          }
                        >
                          {page}
                        </Button>
                      </div>
                    );
                  })}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => goToPage(currentPage + 1)}
                disabled={!hasNext}
              >
                Następna
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

export function BrowsePage() {
  return <BrowsePageContent />;
}

export default BrowsePage;
