import { useEffect, useState } from 'react';
import { Users, Trash2, ChevronLeft, ChevronRight, User as UserIcon, Shield, Key, RefreshCw } from 'lucide-react';
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { adminApi, type AdminUser } from '@/api/admin';
import { format } from 'date-fns';
import { pl } from 'date-fns/locale';
import { toast } from 'sonner';

export function UsersSection() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [userToDelete, setUserToDelete] = useState<AdminUser | null>(null);
  const [userToReset, setUserToReset] = useState<AdminUser | null>(null);
  const [userToChangeRole, setUserToChangeRole] = useState<AdminUser | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [isChangingRole, setIsChangingRole] = useState(false);
  const [tempPassword, setTempPassword] = useState<string | null>(null);
  const [newRole, setNewRole] = useState<string>('');

  const fetchUsers = async (currentPage: number) => {
    try {
      setLoading(true);
      const response = await adminApi.getUsers(currentPage);
      if (response.data) {
        setUsers(response.data.data);
        setTotalPages(response.data.total_pages);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Błąd pobierania użytkowników');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers(page);
  }, [page]);

  const handleDelete = async () => {
    if (!userToDelete) return;

    try {
      setIsDeleting(true);
      await adminApi.deleteUser(userToDelete.id);
      setUsers((prev) => prev.filter((u) => u.id !== userToDelete.id));
      setUserToDelete(null);
      toast.success('Użytkownik usunięty');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Błąd usuwania użytkownika');
      toast.error(err instanceof Error ? err.message : 'Błąd usuwania użytkownika');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleResetPassword = async () => {
    if (!userToReset) return;

    try {
      setIsResetting(true);
      const response = await adminApi.resetUserPassword(userToReset.id);
      if (response.data?.temp_password) {
        setTempPassword(response.data.temp_password);
        toast.success('Hasło zresetowane');
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Błąd resetowania hasła');
    } finally {
      setIsResetting(false);
    }
  };

  const handleChangeRole = async () => {
    if (!userToChangeRole || !newRole) return;

    try {
      setIsChangingRole(true);
      await adminApi.updateUserRole(userToChangeRole.id, newRole as 'admin' | 'reader');
      setUsers((prev) =>
        prev.map((u) =>
          u.id === userToChangeRole.id ? { ...u, role: newRole as 'admin' | 'reader' } : u
        )
      );
      setUserToChangeRole(null);
      setNewRole('');
      toast.success('Rola zmieniona');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Błąd zmiany roli');
    } finally {
      setIsChangingRole(false);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'dd.MM.yyyy', { locale: pl });
    } catch {
      return dateString;
    }
  };

  const copyPassword = () => {
    if (tempPassword) {
      navigator.clipboard.writeText(tempPassword);
      toast.success('Hasło skopiowane do schowka');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-serif font-bold text-book-brown">Użytkownicy</h1>
          <p className="text-book-muted mt-1">Zarządzaj użytkownikami platformy</p>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm">
          {error}
        </div>
      )}

      {/* Users Table */}
      <Card className="bg-white border-stone-200/60">
        <CardHeader>
          <CardTitle className="text-lg font-serif text-book-brown flex items-center gap-2">
            <Users className="w-5 h-5" />
            Lista użytkowników
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-12 bg-stone-100 rounded animate-pulse" />
              ))}
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-12">
              <Users className="w-12 h-12 text-stone-300 mx-auto mb-4" />
              <h3 className="font-serif font-semibold text-book-brown mb-2">
                Brak użytkowników
              </h3>
              <p className="text-book-muted text-sm">
                Nie znaleziono żadnych użytkowników w systemie
              </p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Użytkownik</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Rola</TableHead>
                      <TableHead>Data rejestracji</TableHead>
                      <TableHead className="text-right">Akcje</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {users.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-book-gold/10 flex items-center justify-center">
                              <UserIcon className="w-4 h-4 text-book-gold" />
                            </div>
                            <div>
                              <p className="font-medium text-book-brown">
                                {user.first_name} {user.last_name}
                              </p>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="text-book-gray">{user.email}</TableCell>
                        <TableCell>
                          {user.role === 'admin' ? (
                            <Badge className="bg-red-100 text-red-800 hover:bg-red-100">
                              <Shield className="w-3 h-3 mr-1" />
                              Admin
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="text-book-gray">
                              Użytkownik
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell className="text-book-gray">
                          {formatDate(user.created_at)}
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                              onClick={() => {
                                setUserToReset(user);
                                setTempPassword(null);
                              }}
                              title="Resetuj hasło"
                            >
                              <Key className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-amber-600 hover:text-amber-700 hover:bg-amber-50"
                              onClick={() => {
                                setUserToChangeRole(user);
                                setNewRole(user.role);
                              }}
                              title="Zmień rolę"
                            >
                              <RefreshCw className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => setUserToDelete(user)}
                              title="Usuń użytkownika"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
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
      <AlertDialog open={!!userToDelete} onOpenChange={() => setUserToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Usunąć użytkownika?</AlertDialogTitle>
            <AlertDialogDescription>
              Czy na pewno chcesz usunąć użytkownika{' '}
              <strong>{userToDelete?.first_name} {userToDelete?.last_name}</strong>?
              <br />
              Ta akcja usunie również wszystkie jego książki i nie można jej cofnąć.
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

      {/* Reset Password Dialog */}
      <Dialog open={!!userToReset} onOpenChange={() => {
        setUserToReset(null);
        setTempPassword(null);
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Resetuj hasło</DialogTitle>
            <DialogDescription>
              Zresetuj hasło dla użytkownika{' '}
              <strong>{userToReset?.first_name} {userToReset?.last_name}</strong>
            </DialogDescription>
          </DialogHeader>
          
          {tempPassword ? (
            <div className="space-y-4">
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <p className="text-sm text-amber-800 mb-2">Tymczasowe hasło:</p>
                <div className="flex items-center gap-2">
                  <Input 
                    value={tempPassword} 
                    readOnly 
                    className="font-mono bg-white"
                  />
                  <Button onClick={copyPassword} variant="outline" size="sm">
                    Kopiuj
                  </Button>
                </div>
                <p className="text-xs text-amber-600 mt-2">
                  Hasło zostało zresetowane. Użytkownik powinien zmienić je po zalogowaniu.
                </p>
              </div>
            </div>
          ) : (
            <p className="text-book-muted">
              Kliknij przycisk poniżej, aby wygenerować nowe tymczasowe hasło dla tego użytkownika.
            </p>
          )}
          
          <DialogFooter>
            {!tempPassword && (
              <>
                <Button variant="outline" onClick={() => setUserToReset(null)}>
                  Anuluj
                </Button>
                <Button 
                  onClick={handleResetPassword} 
                  disabled={isResetting}
                  className="bg-book-gold hover:bg-book-gold-hover"
                >
                  {isResetting ? 'Resetowanie...' : 'Resetuj hasło'}
                </Button>
              </>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Change Role Dialog */}
      <Dialog open={!!userToChangeRole} onOpenChange={() => {
        setUserToChangeRole(null);
        setNewRole('');
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Zmień rolę</DialogTitle>
            <DialogDescription>
              Zmień rolę dla użytkownika{' '}
              <strong>{userToChangeRole?.first_name} {userToChangeRole?.last_name}</strong>
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <Select value={newRole} onValueChange={setNewRole}>
              <SelectTrigger>
                <SelectValue placeholder="Wybierz rolę" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="reader">Użytkownik (reader)</SelectItem>
                <SelectItem value="admin">Administrator (admin)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setUserToChangeRole(null)}>
              Anuluj
            </Button>
            <Button 
              onClick={handleChangeRole} 
              disabled={isChangingRole || !newRole || newRole === userToChangeRole?.role}
              className="bg-book-gold hover:bg-book-gold-hover"
            >
              {isChangingRole ? 'Zapisywanie...' : 'Zmień rolę'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
