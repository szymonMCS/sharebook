import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  BookOpen, 
  Calendar, 
  User, 
  MapPin, 
  Star,
  Heart,
  Share2,
  Loader2,
  AlertCircle,
  MessageSquare
} from 'lucide-react';
import { LazyBookCover } from '@/components/books/LazyBookCover';
import { BookManagementModal } from '@/components/books/BookManagementModal';
import { BookLoadingAnimation } from '@/components/loading/BookLoadingAnimation';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';
import { Progress } from '@/components/ui/progress';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { booksApi } from '@/api/books';
import { loansApi } from '@/api/loans';
import { toast } from 'sonner';
import { useAuth } from '@/components/auth/AuthContext';
import { useUpdateBookStatus, useDeleteBook } from '@/hooks/useUserBooks';
import { useBookCoverWS } from '@/hooks/useBookCoverWS';
import type { Book } from '@/types';

import { statusConfig } from '@/lib/data';

type LoadingStage = 'idle' | 'checking-auth' | 'fetching-private' | 'fetching-public' | 'connecting-ws' | 'done' | 'error';


export function BookDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  const updateBookStatusMutation = useUpdateBookStatus();
  const deleteBookMutation = useDeleteBook();
  
  const [book, setBook] = useState<Book | null>(null);
  const [loadingStage, setLoadingStage] = useState<LoadingStage>('idle');
  const [error, setError] = useState<string | null>(null);
  const [isEnriching, setIsEnriching] = useState(false);

  const handleEnrichBook = useCallback(async (bookId: string) => {
    setIsEnriching(true);
    try {
      const response = await booksApi.enrichBook(bookId);
      if (response.status === 'processing') {
        toast.info('Rozpoczęto wzbogacanie danych książki. To może potrwać kilka sekund.');
      }
    } catch (err) {
      toast.error('Błąd podczas wzbogacania książki');
    } finally {
      setIsEnriching(false);
    }
  }, []);
  
  const stageProgress: Record<LoadingStage, number> = {
    'idle': 0,
    'checking-auth': 10,
    'fetching-private': 30,
    'fetching-public': 50,
    'connecting-ws': 80,
    'done': 100,
    'error': 0
  };
  
  const stageMessages: Record<LoadingStage, string> = {
    'idle': 'Inicjalizacja...',
    'checking-auth': 'Sprawdzanie autentykacji...',
    'fetching-private': 'Pobieranie danych książki (prywatne)...',
    'fetching-public': 'Pobieranie danych książki (publiczne)...',
    'connecting-ws': 'Łączenie z serwerem WebSocket...',
    'done': 'Gotowe!',
    'error': 'Błąd ładowania'
  };
  const [isRequesting, setIsRequesting] = useState(false);
  const [requestSuccess, setRequestSuccess] = useState(false);
  const [isManagementModalOpen, setIsManagementModalOpen] = useState(false);
  const [isManaging, setIsManaging] = useState(false);
  const [isMessageModalOpen, setIsMessageModalOpen] = useState(false);
  const [requestMessage, setRequestMessage] = useState('');

  const loadBook = useCallback(async (bookId: string) => {
    setLoadingStage('checking-auth');
    setError(null);
    
    try {
      let response;
      
      if (isAuthenticated) {
        setLoadingStage('fetching-private');
        try {
          response = await booksApi.getMyBookCopy(bookId);
        } catch {
          setLoadingStage('fetching-public');
          response = await booksApi.getBook(bookId);
        }
      } else {
        setLoadingStage('fetching-public');
        response = await booksApi.getBook(bookId);
      }
      
      setBook(response.data);
      
      if (response.data.title === 'Wczytywanie...' || response.data.title === '') {
        handleEnrichBook(response.data.id);
      }
      
      setLoadingStage('done');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Wystąpił błąd podczas ładowania książki');
      setLoadingStage('error');
    }
  }, [isAuthenticated, handleEnrichBook]);

  useEffect(() => {
    if (id) {
      loadBook(id);
    }
  }, [id, loadBook]);

  const { latestCoverUrl, bookEnriched } = useBookCoverWS(book?.book_id || book?.id || '');

  const isBookEnriching = book && (book.title === 'Wczytywanie...' || book.title === '');

  const coverUrl = latestCoverUrl || book?.cover_url;

  useEffect(() => {
    if ((bookEnriched || latestCoverUrl) && id) {
      loadBook(id);
    }
  }, [bookEnriched, latestCoverUrl, id, loadBook]);

  const handleBorrowRequest = () => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: `/books/${id}` } });
      return;
    }

    if (!book || book.owner_id === user?.id) return;

    setIsMessageModalOpen(true);
  };

  const handleSubmitRequest = async () => {
    if (!book) return;

    setIsRequesting(true);
    try {
      const response = await loansApi.createRequest(book.id, requestMessage.trim() || undefined);
      if (response.success) {
        setRequestSuccess(true);
        setIsMessageModalOpen(false);
        setRequestMessage('');
        navigate('/reader/requests');
      }
    } catch (err) {
      setError('Nie udało się wysłać prośby o wypożyczenie');
    } finally {
      setIsRequesting(false);
    }
  };



  const handleDeleteBook = async (bookId: string) => {
    setIsManaging(true);
    try {
      await deleteBookMutation.mutateAsync(bookId);
      toast.success('Książka została usunięta z biblioteki');
      navigate('/reader/my-books');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Błąd usuwania książki';
      toast.error(errorMsg);
      console.error('Delete error:', err);
    } finally {
      setIsManaging(false);
    }
  };

  const handleStatusChange = async (bookId: string, newStatus: string) => {
    setIsManaging(true);
    try {
      await updateBookStatusMutation.mutateAsync({ id: bookId, status: newStatus });
      setBook(prev => prev ? { ...prev, status: newStatus as Book['status'] } : null);
      if (id) {
        try {
          await loadBook(id);
        } catch (refreshErr) {
          console.error('Error refreshing book data:', refreshErr);
        }
      }
      toast.success('Status książki został zmieniony');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Błąd zmiany statusu');
      toast.error(err instanceof Error ? err.message : 'Błąd zmiany statusu');
    } finally {
      setIsManaging(false);
    }
  };

  if (loadingStage !== 'done' && loadingStage !== 'error' && !book) {
    return (
      <div className="min-h-screen bg-warm-beige">
        <Navbar />
        <div className="pt-32 pb-16 px-4">
          <div className="max-w-md mx-auto text-center">
            <BookLoadingAnimation 
              message={stageMessages[loadingStage]}
              size="md"
            />
            <div className="mt-8 space-y-2">
              <Progress value={stageProgress[loadingStage]} className="h-2" />
              <p className="text-sm text-book-gray">
                {stageProgress[loadingStage]}% - {stageMessages[loadingStage]}
              </p>
            </div>
            <p className="mt-4 text-xs text-stone-400">
              ID: {id}
            </p>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  if (error || !book) {
    return (
      <div className="min-h-screen bg-warm-beige">
        <Navbar />
        <div className="pt-32 pb-16 px-4">
          <div className="max-w-4xl mx-auto text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h1 className="font-serif text-2xl font-bold text-book-brown mb-2">
              {error || 'Książka nie została znaleziona'}
            </h1>
            <p className="text-book-gray mb-6">
              Spróbuj wrócić do listy książek lub sprawdź czy adres URL jest poprawny.
            </p>
            <Button asChild className="bg-book-gold hover:bg-book-gold-hover text-white">
              <Link to="/browse">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Wróć do przeglądania
              </Link>
            </Button>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  const bookStatus = statusConfig[book.status] || { 
    label: 'Nieznany', 
    color: 'bg-gray-100 text-gray-800 border-gray-200',
    className: 'bg-gray-100 text-gray-800 border-gray-200',
    icon: BookOpen
  };
  const isOwner = isAuthenticated && user?.id === book.owner_id;
  const isAvailable = book.status === 'available';

  return (
    <div className="min-h-screen bg-warm-beige relative">
      <Navbar className={isBookEnriching ? 'opacity-0 pointer-events-none' : ''} />
      
      {isBookEnriching && (
        <div className="fixed inset-0 bg-stone-900/95 z-50 flex flex-col items-center justify-center px-4">
          <BookLoadingAnimation 
            message="Wczytywanie informacji o książce..."
            size="lg"
          />
          <div className="mt-8 w-full max-w-xs space-y-3">
            <Progress value={75} className="h-2 bg-stone-700" />
            <p className="text-stone-400 text-sm text-center">
              Wzbogacanie danych książki...
            </p>
          </div>
          <p className="mt-4 text-stone-500 text-sm text-center max-w-md">
            Szukamy szczegółów książki w naszej bazie i zewnętrznych źródłach.
          </p>
          <Button
            variant="outline"
            onClick={() => navigate('/reader/my-books')}
            className="mt-6 border-stone-500 text-stone-200 bg-stone-800 hover:bg-stone-700 hover:text-white"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Wróć do moich książek
          </Button>
        </div>
      )}
      
      <main className="pt-24 pb-16 px-4">
        <div className="max-w-6xl mx-auto">

          <Button
            variant="ghost"
            onClick={() => navigate(isOwner ? '/reader/my-books' : '/browse')}
            className="mb-6 text-book-gray hover:text-book-brown"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            {isOwner ? 'Wróć do moich książek' : 'Wróć do przeglądania'}
          </Button>

          <div className="grid md:grid-cols-3 gap-8">

            <div className="md:col-span-1">
              <div className="aspect-[2/3] rounded-2xl overflow-hidden shadow-book bg-stone-100 sticky top-28">
                <LazyBookCover
                  coverUrl={coverUrl}
                  title={book.title}
                  className="h-full"
                />
              </div>
            </div>


            <div className="md:col-span-2 space-y-6">

              <div>
                <div className="flex items-center gap-3 mb-3">
                  <Badge className={bookStatus.color}>
                    {bookStatus.label}
                  </Badge>
                  {book.genre && (
                    <Badge variant="outline" className="text-book-gray">
                      {book.genre}
                    </Badge>
                  )}
                </div>
                
                <h1 className="font-serif text-3xl md:text-4xl font-bold text-book-brown mb-2">
                  {book.title}
                </h1>
                
                <p className="text-xl text-book-gray">
                  {book.author}
                </p>
              </div>


              <div className="flex flex-wrap gap-3">
                {isAvailable && !isOwner && isAuthenticated && (
                  <Button
                    size="lg"
                    className="bg-book-gold hover:bg-book-gold-hover text-white"
                    onClick={handleBorrowRequest}
                    disabled={isRequesting || requestSuccess}
                  >
                    {isRequesting ? (
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    ) : requestSuccess ? (
                      <>
                        <Star className="w-5 h-5 mr-2" />
                        Wysłano prośbę
                      </>
                    ) : (
                      <>
                        <BookOpen className="w-5 h-5 mr-2" />
                        Chcę wypożyczyć
                      </>
                    )}
                  </Button>
                )}
                
                {!isAuthenticated && (
                  <Button
                    size="lg"
                    variant="outline"
                    onClick={() => navigate('/login', { state: { from: `/books/${id}` } })}
                  >
                    <BookOpen className="w-5 h-5 mr-2" />
                    Zaloguj się, aby wypożyczyć
                  </Button>
                )}
                

                
                {isOwner && (
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={() => setIsManagementModalOpen(true)}
                  >
                    Zarządzaj książką
                  </Button>
                )}

                <Button
                  variant="outline"
                  size="icon"
                  className="h-12 w-12"
                >
                  <Heart className="w-5 h-5" />
                </Button>
                
                <Button
                  variant="outline"
                  size="icon"
                  className="h-12 w-12"
                >
                  <Share2 className="w-5 h-5" />
                </Button>
              </div>

              {requestSuccess && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-green-800">
                  <p className="font-medium">Prośba o wypożyczenie została wysłana!</p>
                  <p className="text-sm mt-1">
                    Właściciel książki zostanie powiadomiony i rozpatrzy Twoją prośbę.
                  </p>
                </div>
              )}


              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-6 border-y border-stone-200">
                {book.isbn && (
                  <div>
                    <p className="text-sm text-book-muted mb-1">ISBN</p>
                    <p className="font-medium text-book-brown">{book.isbn}</p>
                  </div>
                )}
                {book.publication_year && (
                  <div>
                    <p className="text-sm text-book-muted mb-1">Rok wydania</p>
                    <p className="font-medium text-book-brown">{book.publication_year}</p>
                  </div>
                )}
                {book.page_count && (
                  <div>
                    <p className="text-sm text-book-muted mb-1">Liczba stron</p>
                    <p className="font-medium text-book-brown">{book.page_count}</p>
                  </div>
                )}
                {book.language && (
                  <div>
                    <p className="text-sm text-book-muted mb-1">Język</p>
                    <p className="font-medium text-book-brown">{book.language}</p>
                  </div>
                )}
              </div>


              {book.description && (
                <div>
                  <h2 className="font-serif text-xl font-semibold text-book-brown mb-3">
                    Opis
                  </h2>
                  <p className="text-book-gray leading-relaxed whitespace-pre-line">
                    {book.description}
                  </p>
                </div>
              )}


              <div className="bg-white rounded-xl p-6 shadow-sm border border-stone-200">
                <h2 className="font-serif text-lg font-semibold text-book-brown mb-4">
                  Informacje o właścicielu
                </h2>
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-full bg-book-gold/20 flex items-center justify-center">
                    <User className="w-7 h-7 text-book-gold" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-book-brown">
                      {book.owner?.first_name && book.owner?.last_name 
                        ? `${book.owner.first_name} ${book.owner.last_name}`
                        : book.owner?.username || 'Użytkownik'}
                    </p>
                    <div className="flex items-center gap-4 text-sm text-book-gray mt-1">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        {book.owner?.location || 'Lokalizacja niepodana'}
                      </span>
                    </div>
                  </div>

                </div>
              </div>


              <div className="bg-stone-50 rounded-xl p-6">
                <h2 className="font-serif text-lg font-semibold text-book-brown mb-4">
                  Warunki wypożyczenia
                </h2>
                <div className="space-y-3">
                  <div className="flex items-center gap-3 text-book-gray">
                    <Calendar className="w-5 h-5 text-book-gold" />
                    <span>Okres wypożyczenia: do 30 dni</span>
                  </div>
                  <div className="flex items-center gap-3 text-book-gray">
                    <MapPin className="w-5 h-5 text-book-gold" />
                    <span>Odbiór osobisty lub wysyłka (do ustalenia)</span>
                  </div>
                  <div className="flex items-center gap-3 text-book-gray">
                    <Star className="w-5 h-5 text-book-gold" />
                    <span>Stan: {book.condition || 'Nie podano'}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer />


      <BookManagementModal
        book={book}
        isOpen={isManagementModalOpen}
        onClose={() => setIsManagementModalOpen(false)}
        onStatusChange={handleStatusChange}
        onDelete={handleDeleteBook}
        isLoading={isManaging}
      />


      <Dialog open={isMessageModalOpen} onOpenChange={setIsMessageModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              Prośba o wypożyczenie
            </DialogTitle>
            <DialogDescription>
              {book && (
                <>
                  Wyślij prośbę o wypożyczenie książki <strong>"{book.title}"</strong>
                </>
              )}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-book-brown">
                Wiadomość do właściciela (opcjonalnie)
              </label>
              <Textarea
                placeholder="Np. Cześć! Bardzo chciałbym przeczytać tę książkę. Kiedy moglibyśmy się spotkać?"
                value={requestMessage}
                onChange={(e) => setRequestMessage(e.target.value)}
                rows={4}
                className="resize-none"
              />
              <p className="text-xs text-book-muted">
                Dodaj krótką wiadomość, aby zwiększyć szanse na pozytywną odpowiedź.
              </p>
            </div>
          </div>

          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => setIsMessageModalOpen(false)}
              className="flex-1"
              disabled={isRequesting}
            >
              Anuluj
            </Button>
            <Button
              onClick={handleSubmitRequest}
              disabled={isRequesting}
              className="flex-1 bg-book-brown hover:bg-book-brown/90"
            >
              {isRequesting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Wysyłanie...
                </>
              ) : (
                'Wyślij prośbę'
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
