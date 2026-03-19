import { useState, useEffect } from 'react';
import { BookX, Loader2, Tag, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
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
import type { Book } from '@/types';

// Status options matching /browse filters
const statusOptions: { value: string; label: string; color: string }[] = [
  { value: 'available', label: 'Dostępna', color: 'text-green-600' },
  { value: 'reserved', label: 'Zarezerwowana', color: 'text-purple-600' },
  { value: 'borrowed', label: 'Wypożyczona', color: 'text-amber-600' },
  { value: 'unavailable', label: 'Niedostępna', color: 'text-gray-600' },
];

interface BookManagementModalProps {
  book: Book | null;
  isOpen: boolean;
  onClose: () => void;
  onStatusChange?: (bookId: string, status: string) => Promise<void>;
  onDelete: (bookId: string) => Promise<void>;
  isLoading?: boolean;
}

export function BookManagementModal({
  book,
  isOpen,
  onClose,
  onStatusChange,
  onDelete,
  isLoading = false,
}: BookManagementModalProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isChangingStatus, setIsChangingStatus] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState(book?.status || '');
  const [hasStatusChanged, setHasStatusChanged] = useState(false);

  if (!book) return null;

  // Reset selected status when modal opens or book changes
  useEffect(() => {
    if (isOpen && book) {
      setSelectedStatus(book.status);
      setHasStatusChanged(false);
    }
  }, [isOpen, book]);

  const handleStatusChange = (value: string) => {
    setSelectedStatus(value);
    setHasStatusChanged(value !== book.status);
  };

  const handleSaveStatus = async () => {
    if (!onStatusChange || !hasStatusChanged) return;
    setIsChangingStatus(true);
    try {
      await onStatusChange(book.id, selectedStatus);
      setHasStatusChanged(false);
    } finally {
      setIsChangingStatus(false);
    }
  }

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(book.id);
      setShowDeleteDialog(false);
      onClose();
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="font-serif">Zarządzaj książką</DialogTitle>
            <DialogDescription>
              {book.title} - {book.author}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-4">
            {/* Change Status */}
            {onStatusChange && (
              <div className="flex items-center justify-between p-4 bg-stone-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Tag className="w-5 h-5 text-book-gold" />
                  <div>
                    <p className="font-medium text-book-brown">Status książki</p>
                    <p className="text-xs text-book-muted">
                      Zmień aktualny status książki
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Select
                    value={selectedStatus}
                    onValueChange={handleStatusChange}
                    disabled={isChangingStatus || isLoading}
                  >
                    <SelectTrigger className="w-[140px] h-9 text-sm">
                      <SelectValue placeholder="Wybierz status" />
                    </SelectTrigger>
                    <SelectContent>
                      {statusOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value} className="text-sm">
                          <span className={option.color}>{option.label}</span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {hasStatusChanged && (
                    <Button
                      size="sm"
                      onClick={handleSaveStatus}
                      disabled={isChangingStatus}
                      className="h-9 px-3 bg-book-brown hover:bg-book-brown/90"
                    >
                      {isChangingStatus ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <>
                          <Save className="w-4 h-4 mr-1" />
                          Zapisz
                        </>
                      )}
                    </Button>
                  )}
                </div>
              </div>
            )}

            {/* Delete Book */}
            <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg border border-red-100">
              <div className="flex items-center gap-3">
                <BookX className="w-5 h-5 text-red-500" />
                <div>
                  <p className="font-medium text-red-700">Usuń książkę</p>
                  <p className="text-xs text-red-600">
                    Tej akcji nie można cofnąć
                  </p>
                </div>
              </div>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => setShowDeleteDialog(true)}
                disabled={isLoading}
              >
                Usuń
              </Button>
            </div>
          </div>

          <div className="flex justify-end">
            <Button variant="outline" onClick={onClose}>
              Zamknij
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Usunąć książkę?</AlertDialogTitle>
            <AlertDialogDescription>
              Czy na pewno chcesz usunąć „{book.title}"? Tej akcji nie można cofnąć.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Anuluj</AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDelete}
              className="bg-red-600 hover:bg-red-700"
              disabled={isDeleting}
            >
              {isDeleting ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : null}
              Usuń
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
