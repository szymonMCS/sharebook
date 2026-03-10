import { useEffect, useState } from 'react';
import { BookOpen, Trash2, ChevronLeft, ChevronRight, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { adminApi, type AdminBook } from '@/api/admin';

export function BooksSection() {
  const [books, setBooks] = useState<AdminBook[]>([]);
  const [filteredBooks, setFilteredBooks] = useState<AdminBook[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [bookToDelete, setBookToDelete] = useState<AdminBook | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchBooks = async (currentPage: number) => {
    try {
      setLoading(true);
      const response = await adminApi.getBooks(currentPage);
      if (response.data) {
        setBooks(response.data.data);
        setFilteredBooks(response.data.data);
        setTotalPages(response.data.total_pages);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Błąd pobierania książek');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks(page);
  }, [page]);

  // Filter books based on search query
  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredBooks(books);
    } else {
      const query = searchQuery.toLowerCase();
      setFilteredBooks(
        books.filter(
          (book) =>
            book.title.toLowerCase().includes(query) ||
            book.author.toLowerCase().includes(query) ||
            book.owner_name.toLowerCase().includes(query) ||
            book.owner_email.toLowerCase().includes(query)
        )
      );
    }
  }, [searchQuery, books]);

  const handleDelete = async () => {
    if (!bookToDelete) return;

    try {
      setIsDeleting(true);
      await adminApi.deleteBook(bookToDelete.id);
      setBooks((prev) => prev.filter((b) => b.id !== bookToDelete.id));
      setFilteredBooks((prev) => prev.filter((b) => b.id !== bookToDelete.id));
      setBookToDelete(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Błąd usuwania książki');
    } finally {
      setIsDeleting(false);
    }
  };

  const getStatusBadge = (status: AdminBook['status']) => {
    const config = {
      available: { label: 'Dostępna', className: 'bg-green-100 text-green-800 border-green-200' },
      lent: { label: 'Wypożyczona', className: 'bg-amber-100 text-amber-800 border-amber-200' },
      private: { label: 'Prywatna', className: 'bg-gray-100 text-gray-800 border-gray-200' },
    };

    const { label, className } = config[status];
    return (
      <Badge variant="outline" className={className}>
        {label}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-serif font-bold text-book-brown">Książki</h1>
          <p className="text-book-muted mt-1">Zarządzaj wszystkimi książkami w systemie</p>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm">
          {error}
        </div>
      )}

      {/* Books Table */}
      <Card className="bg-white border-stone-200/60">
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <CardTitle className="text-lg font-serif text-book-brown flex items-center gap-2">
              <BookOpen className="w-5 h-5" />
              Wszystkie książki
            </CardTitle>
            <div className="relative w-full sm:w-72">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-book-muted" />
              <Input
                placeholder="Szukaj książek..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-12 bg-stone-100 rounded animate-pulse" />
              ))}
            </div>
          ) : filteredBooks.length === 0 ? (
            <div className="text-center py-12">
              <BookOpen className="w-12 h-12 text-stone-300 mx-auto mb-4" />
              <h3 className="font-serif font-semibold text-book-brown mb-2">
                {searchQuery ? 'Nie znaleziono książek' : 'Brak książek'}
              </h3>
              <p className="text-book-muted text-sm">
                {searchQuery
                  ? 'Spróbuj zmienić kryteria wyszukiwania'
                  : 'Nie znaleziono żadnych książek w systemie'}
              </p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Książka</TableHead>
                      <TableHead>Autor</TableHead>
                      <TableHead>Właściciel</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Akcje</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredBooks.map((book) => (
                      <TableRow key={book.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-14 bg-stone-100 rounded overflow-hidden flex-shrink-0">
                              <img
                                src={`https://covers.openlibrary.org/b/id/${book.id}-S.jpg`}
                                alt={book.title}
                                className="w-full h-full object-cover"
                                onError={(e) => {
                                  (e.target as HTMLImageElement).src = '/placeholder-book.png';
                                }}
                              />
                            </div>
                            <div>
                              <p className="font-medium text-book-brown line-clamp-1">
                                {book.title}
                              </p>
                              {book.is_lendable && (
                                <Badge variant="outline" className="text-xs mt-1">
                                  Do pożyczenia
                                </Badge>
                              )}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="text-book-gray">{book.author}</TableCell>
                        <TableCell>
                          <div className="text-book-gray">
                            <p className="font-medium">{book.owner_name}</p>
                            <p className="text-xs text-book-muted">{book.owner_email}</p>
                          </div>
                        </TableCell>
                        <TableCell>{getStatusBadge(book.status)}</TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => setBookToDelete(book)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-6 pt-4 border-t border-stone-200">
                  <p className="text-sm text-book-muted">
                    Strona {page} z {totalPages}
                  </p>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                      disabled={page === totalPages}
                    >
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!bookToDelete} onOpenChange={() => setBookToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Usunąć książkę?</AlertDialogTitle>
            <AlertDialogDescription>
              Czy na pewno chcesz usunąć książkę <strong>"{bookToDelete?.title}"</strong>?
              <br />
              Autor: {bookToDelete?.author}
              <br />
              Właściciel: {bookToDelete?.owner_name}
              <br /><br />
              Tej akcji nie można cofnąć.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Anuluj</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700"
            >
              {isDeleting ? 'Usuwanie...' : 'Usuń'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
