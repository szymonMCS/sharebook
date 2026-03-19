import { useEffect, useState } from 'react';
import { BookOpen, ChevronLeft, ChevronRight, Search, Plus, User, BookX } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
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
import { adminApi, type AdminUserBook } from '@/api/admin';
import { useDebounce } from '@/hooks/useDebounce';

export function UserBooksSection() {
  const [userBooks, setUserBooks] = useState<AdminUserBook[]>([]);
  const [filteredUserBooks, setFilteredUserBooks] = useState<AdminUserBook[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedSearch = useDebounce(searchQuery, 300);
  
  const [userBookToDelete, setUserBookToDelete] = useState<AdminUserBook | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  
  // Add dialog state
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [newUserBook, setNewUserBook] = useState({
    user_id: '',
    book_id: '',
    condition: 'good',
    is_lendable: true
  });

  const fetchUserBooks = async (currentPage: number) => {
    try {
      setLoading(true);
      const response = await adminApi.getUserBooks({ page: currentPage, per_page: 20 });
      if (response.data) {
        setUserBooks(response.data.data);
        setTotalPages(response.data.total_pages);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Błąd pobierania książek użytkowników');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUserBooks(page);
  }, [page]);

  useEffect(() => {
    if (debouncedSearch.trim() === '') {
      setFilteredUserBooks(userBooks);
    } else {
      const query = debouncedSearch.toLowerCase();
      setFilteredUserBooks(
        userBooks.filter(
          (ub) =>
            ub.book_title.toLowerCase().includes(query) ||
            ub.book_author?.toLowerCase().includes(query) ||
            ub.user_name.toLowerCase().includes(query) ||
            ub.user_email.toLowerCase().includes(query) ||
            ub.book_isbn?.toLowerCase().includes(query)
        )
      );
    }
  }, [debouncedSearch, userBooks]);

  const handleDelete = async () => {
    if (!userBookToDelete) return;

    try {
      setIsDeleting(true);
      await adminApi.removeBookFromUser(userBookToDelete.user_book_id);
      setUserBooks((prev) => prev.filter((ub) => ub.user_book_id !== userBookToDelete.user_book_id));
      setFilteredUserBooks((prev) => prev.filter((ub) => ub.user_book_id !== userBookToDelete.user_book_id));
      setUserBookToDelete(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Błąd usuwania książki');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleAddUserBook = async () => {
    if (!newUserBook.user_id.trim() || !newUserBook.book_id.trim()) {
      setError('User ID i Book ID są wymagane');
      return;
    }

    try {
      setIsAdding(true);
      await adminApi.addBookToUser(
        newUserBook.user_id,
        newUserBook.book_id,
        newUserBook.condition,
        newUserBook.is_lendable
      );
      setNewUserBook({ user_id: '', book_id: '', condition: 'good', is_lendable: true });
      setIsAddDialogOpen(false);
      fetchUserBooks(page);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Błąd dodawania książki');
    } finally {
      setIsAdding(false);
    }
  };

  const handleStatusChange = async (userBookId: string, newStatus: string) => {
    try {
      await adminApi.updateUserBookStatus(userBookId, newStatus);
      setUserBooks((prev) =>
        prev.map((ub) => (ub.user_book_id === userBookId ? { ...ub, status: newStatus as AdminUserBook['status'] } : ub))
      );
      setFilteredUserBooks((prev) =>
        prev.map((ub) => (ub.user_book_id === userBookId ? { ...ub, status: newStatus as AdminUserBook['status'] } : ub))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Błąd aktualizacji statusu');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-serif font-bold text-book-brown">Książki użytkowników</h1>
          <p className="text-book-muted mt-1">Zarządzaj kopiami książek w bibliotekach użytkowników</p>
        </div>
        <Button onClick={() => setIsAddDialogOpen(true)} className="gap-2">
          <Plus className="w-4 h-4" />
          Dodaj książkę użytkownikowi
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
              <User className="w-5 h-5" />
              Wszystkie kopie użytkowników
            </CardTitle>
            <div className="relative w-full sm:w-72">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-book-muted" />
              <Input
                placeholder="Szukaj książek lub użytkowników..."
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
          ) : filteredUserBooks.length === 0 ? (
            <div className="text-center py-12">
              <BookOpen className="w-12 h-12 text-stone-300 mx-auto mb-4" />
              <h3 className="font-serif font-semibold text-book-brown mb-2">
                {searchQuery ? 'Nie znaleziono książek' : 'Brak książek użytkowników'}
              </h3>
              <p className="text-book-muted text-sm">
                {searchQuery
                  ? 'Spróbuj zmienić kryteria wyszukiwania'
                  : 'Nie znaleziono żadnych książek w bibliotekach użytkowników'}
              </p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Książka</TableHead>
                      <TableHead>Użytkownik</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Warunek</TableHead>
                      <TableHead className="text-right">Akcje</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredUserBooks.map((userBook) => (
                      <TableRow key={userBook.user_book_id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-14 bg-stone-100 rounded overflow-hidden flex-shrink-0">
                              {userBook.book_cover_url ? (
                                <img
                                  src={userBook.book_cover_url}
                                  alt={userBook.book_title}
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
                                {userBook.book_title}
                              </p>
                              <p className="text-xs text-book-muted">{userBook.book_author || '-'}</p>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <User className="w-4 h-4 text-book-muted" />
                            <div>
                              <p className="text-sm text-book-brown">{userBook.user_name}</p>
                              <p className="text-xs text-book-muted">{userBook.user_email}</p>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Select
                            value={userBook.status}
                            onValueChange={(value) => handleStatusChange(userBook.user_book_id, value)}
                          >
                            <SelectTrigger className="w-36">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="available">Dostępna</SelectItem>
                              <SelectItem value="reserved">Zarezerwowana</SelectItem>
                              <SelectItem value="borrowed">Wypożyczona</SelectItem>
                              <SelectItem value="unavailable">Niedostępna</SelectItem>
                            </SelectContent>
                          </Select>
                        </TableCell>
                        <TableCell>
                          <Badge variant={userBook.is_lendable ? 'default' : 'secondary'}>
                            {userBook.condition || 'good'}
                          </Badge>
                          {userBook.has_active_loan && (
                            <Badge variant="destructive" className="ml-2">
                              Wypożyczona
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => setUserBookToDelete(userBook)}
                            disabled={userBook.has_active_loan}
                            title={userBook.has_active_loan ? 'Nie można usunąć - aktywne wypożyczenie' : 'Usuń książkę'}
                          >
                            <BookX className="w-4 h-4" />
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

      {/* Delete Dialog */}
      <AlertDialog open={!!userBookToDelete} onOpenChange={() => setUserBookToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Usunąć książkę użytkownika?</AlertDialogTitle>
            <AlertDialogDescription>
              Czy na pewno chcesz usunąć książkę <strong>"{userBookToDelete?.book_title}"</strong> z biblioteki użytkownika <strong>{userBookToDelete?.user_name}</strong>?
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

      {/* Add Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Dodaj książkę użytkownikowi</DialogTitle>
            <DialogDescription>
              Dodaj istniejącą książkę z katalogu do biblioteki użytkownika.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="user_id">ID Użytkownika *</Label>
              <Input
                id="user_id"
                placeholder="np. 550e8400-e29b-41d4-a716-446655440000"
                value={newUserBook.user_id}
                onChange={(e) => setNewUserBook({ ...newUserBook, user_id: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="book_id">ID Książki *</Label>
              <Input
                id="book_id"
                placeholder="np. 550e8400-e29b-41d4-a716-446655440000"
                value={newUserBook.book_id}
                onChange={(e) => setNewUserBook({ ...newUserBook, book_id: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="condition">Stan książki</Label>
              <Select
                value={newUserBook.condition}
                onValueChange={(value) => setNewUserBook({ ...newUserBook, condition: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="new">Nowa</SelectItem>
                  <SelectItem value="like_new">Jak nowa</SelectItem>
                  <SelectItem value="good">Dobra</SelectItem>
                  <SelectItem value="fair">Średnia</SelectItem>
                  <SelectItem value="poor">Słaba</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_lendable"
                checked={newUserBook.is_lendable}
                onChange={(e) => setNewUserBook({ ...newUserBook, is_lendable: e.target.checked })}
                className="rounded border-stone-300"
              />
              <Label htmlFor="is_lendable">Można wypożyczać</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
              Anuluj
            </Button>
            <Button onClick={handleAddUserBook} disabled={isAdding}>
              {isAdding ? 'Dodawanie...' : 'Dodaj książkę'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
