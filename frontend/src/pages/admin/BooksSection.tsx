import { useEffect, useState } from 'react';
import { BookOpen, Trash2, ChevronLeft, ChevronRight, Search, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
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
  
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [newBook, setNewBook] = useState({
    isbn: '',
    title: '',
    author: '',
    description: ''
  });

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
            book.isbn?.toLowerCase().includes(query)
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

  const handleAddBook = async () => {
    if (!newBook.isbn.trim()) {
      setError('ISBN jest wymagany');
      return;
    }

    try {
      setIsAdding(true);
      await adminApi.addBook({
        isbn: newBook.isbn,
        title: newBook.title || undefined,
        author: newBook.author || undefined,
        description: newBook.description || undefined
      });
      setNewBook({ isbn: '', title: '', author: '', description: '' });
      setIsAddDialogOpen(false);
      fetchBooks(page);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Błąd dodawania książki');
    } finally {
      setIsAdding(false);
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
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-serif font-bold text-book-brown">Książki</h1>
          <p className="text-book-muted mt-1">Zarządzaj wszystkimi książkami w systemie</p>
        </div>
        <Button onClick={() => setIsAddDialogOpen(true)} className="gap-2">
          <Plus className="w-4 h-4" />
          Dodaj książkę
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm">
          {error}
        </div>
      )}

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
                      <TableHead>ISBN</TableHead>
                      <TableHead className="text-right">Akcje</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredBooks.map((book) => (
                      <TableRow key={book.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-14 bg-stone-100 rounded overflow-hidden flex-shrink-0">
                              {book.cover_url ? (
                                <img
                                  src={book.cover_url}
                                  alt={book.title}
                                  className="w-full h-full object-cover"
                                  onError={(e) => {
                                    (e.target as HTMLImageElement).style.display = 'none';
                                  }}
                                />
                              ) : (
                                <div className="w-full h-full flex items-center justify-center text-stone-400 text-xs">
                                  Brak
                                </div>
                              )}
                            </div>
                            <div>
                              <p className="font-medium text-book-brown line-clamp-1">
                                {book.title}
                              </p>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="text-book-gray">{book.author || '-'}</TableCell>
                        <TableCell className="text-book-gray text-sm">{book.isbn || '-'}</TableCell>
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

      <AlertDialog open={!!bookToDelete} onOpenChange={() => setBookToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Usunąć książkę?</AlertDialogTitle>
            <AlertDialogDescription>
              Czy na pewno chcesz usunąć książkę <strong>"{bookToDelete?.title}"</strong>?
              <br />
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

      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Dodaj nową książkę</DialogTitle>
            <DialogDescription>
              Wprowadź dane książki. ISBN jest wymagany.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="isbn">ISBN *</Label>
              <Input
                id="isbn"
                placeholder="np. 978-83-0123-456-7"
                value={newBook.isbn}
                onChange={(e) => setNewBook({ ...newBook, isbn: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="title">Tytuł</Label>
              <Input
                id="title"
                placeholder="Tytuł książki"
                value={newBook.title}
                onChange={(e) => setNewBook({ ...newBook, title: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="author">Autor</Label>
              <Input
                id="author"
                placeholder="Imię i nazwisko autora"
                value={newBook.author}
                onChange={(e) => setNewBook({ ...newBook, author: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Opis</Label>
              <Input
                id="description"
                placeholder="Krótki opis książki"
                value={newBook.description}
                onChange={(e) => setNewBook({ ...newBook, description: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
              Anuluj
            </Button>
            <Button onClick={handleAddBook} disabled={isAdding}>
              {isAdding ? 'Dodawanie...' : 'Dodaj książkę'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
