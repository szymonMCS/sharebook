import { useState } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { Loader2, BookOpen, Check, X, AlertCircle, ScanBarcode, Sparkles } from 'lucide-react';
import { BookLoadingAnimation } from '@/components/loading/BookLoadingAnimation';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { booksApi } from '@/api/books';

interface AddBookDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onBookAdded?: () => void;
}

// ISBN validation helper - validates ISBN-10 and ISBN-13
const isValidISBN = (isbn: string): boolean => {
  // Remove hyphens and spaces
  const clean = isbn.replace(/[-\s]/g, '');
  
  // ISBN-13: 13 digits, must start with 978 or 979
  if (clean.length === 13) {
    if (!/^97[89]\d{10}$/.test(clean)) return false;
    // Checksum validation
    let sum = 0;
    for (let i = 0; i < 12; i++) {
      sum += parseInt(clean[i]) * (i % 2 === 0 ? 1 : 3);
    }
    const check = (10 - (sum % 10)) % 10;
    return check === parseInt(clean[12]);
  }
  
  // ISBN-10: 10 chars, last can be X
  if (clean.length === 10) {
    if (!/^\d{9}[\dX]$/i.test(clean)) return false;
    // Checksum validation
    let sum = 0;
    for (let i = 0; i < 9; i++) {
      sum += parseInt(clean[i]) * (10 - i);
    }
    const last = clean[9].toUpperCase();
    sum += last === 'X' ? 10 : parseInt(last);
    return sum % 11 === 0;
  }
  
  return false;
};

// Format ISBN for display (adds hyphens)
const formatISBN = (isbn: string): string => {
  const clean = isbn.replace(/[-\s]/g, '');
  if (clean.length === 13) {
    return `${clean.slice(0, 3)}-${clean.slice(3, 4)}-${clean.slice(4, 7)}-${clean.slice(7, 12)}-${clean.slice(12)}`;
  }
  if (clean.length === 10) {
    return `${clean.slice(0, 1)}-${clean.slice(1, 4)}-${clean.slice(4, 9)}-${clean.slice(9)}`;
  }
  return isbn;
};

export function AddBookDialog({ open, onOpenChange, onBookAdded }: AddBookDialogProps) {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Form state - ONLY ISBN and condition are required from user
  const [isbn, setIsbn] = useState('');
  const [condition, setCondition] = useState('');
  const [isbnTouched, setIsbnTouched] = useState(false);
  
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    // ISBN is REQUIRED and must be valid
    if (!isbn.trim()) {
      newErrors.isbn = 'ISBN jest wymagany';
    } else if (!isValidISBN(isbn)) {
      newErrors.isbn = 'Nieprawidłowy format ISBN (sprawdź cyfry)';
    }
    
    // Condition is required
    if (!condition) {
      newErrors.condition = 'Stan książki jest wymagany';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    setIsbnTouched(true);
    if (!validate()) return;
    
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    // Show processing animation immediately
    setIsProcessing(true);
    
    try {
      // Clean ISBN (remove hyphens and spaces)
      const cleanIsbn = isbn.replace(/[-\s]/g, '');
      
      await booksApi.addBook({
        isbn: cleanIsbn,
        condition,
        is_lendable: true,
      });
      
      // Keep animation for a moment after success, then stay in reader panel
      setTimeout(() => {
        resetForm();
        onOpenChange(false);
        onBookAdded?.();
        setIsProcessing(false);
        // Stay on my-books page to see the added book
        navigate('/reader/my-books');
      }, 2000);
      
    } catch (err) {
      setIsProcessing(false);
      setError(err instanceof Error ? err.message : 'Nie udało się dodać książki');
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setIsbn('');
    setCondition('');
    setIsbnTouched(false);
    setErrors({});
    setError(null);
    setSuccess(false);
    setIsProcessing(false);
  };

  const handleClose = () => {
    // Don't allow closing while processing
    if (isProcessing) return;
    resetForm();
    onOpenChange(false);
  };

  const isIsbnValid = isbn.trim() && isValidISBN(isbn);

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[450px]">
        <DialogHeader>
          <DialogTitle className="font-serif text-xl flex items-center gap-2">
            <ScanBarcode className="h-5 w-5" />
            Dodaj książkę do biblioteki
          </DialogTitle>
          <DialogDescription>
            Wpisz ISBN książki, a my pobierzemy wszystkie informacje automatycznie.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-5 py-4">
          {success && (
            <Alert className="bg-green-50 border-green-200">
              <Check className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-700">
                <strong>Książka dodana!</strong> Przekierowuję na stronę główną... 
                Dane książki (tytuł, autor, okładka) są pobierane w tle 
                i będą widoczne za około 10-15 sekund.
              </AlertDescription>
            </Alert>
          )}

          {error && (
            <Alert className="bg-red-50 border-red-200">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-700">
                {error}
              </AlertDescription>
            </Alert>
          )}

          {/* ISBN - REQUIRED FIELD - THE ONLY INPUT NEEDED */}
          <div className="space-y-2">
            <Label htmlFor="isbn" className="flex items-center gap-1 text-base">
              <ScanBarcode className="h-4 w-4" />
              Numer ISBN <span className="text-red-500">*</span>
            </Label>
            <Input
              id="isbn"
              value={isbn}
              onChange={(e) => setIsbn(e.target.value)}
              placeholder="np. 9788383357300"
              className={`font-mono text-lg ${errors.isbn && isbnTouched ? 'border-red-500' : isIsbnValid ? 'border-green-500' : ''}`}
              disabled={isLoading}
              maxLength={17}
            />
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">
                10 lub 13 cyfr (możesz wpisać z myślnikami)
              </span>
              {isIsbnValid && (
                <span className="text-green-600 font-medium">
                  ✓ {formatISBN(isbn.replace(/[-\s]/g, ''))}
                </span>
              )}
            </div>
            {errors.isbn && isbnTouched && (
              <p className="text-sm text-red-500">{errors.isbn}</p>
            )}
          </div>

          {/* Info Box - explaining automatic fetch */}
          {isIsbnValid && (
            <Alert className="bg-blue-50 border-blue-200">
              <Sparkles className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-700 text-sm">
                Wszystkie dodatkowe informacje o książce zostaną dodane automatycznie
              </AlertDescription>
            </Alert>
          )}

          {/* Condition - Required Select */}
          <div className="space-y-2">
            <Label htmlFor="condition" className="flex items-center gap-1">
              Stan książki <span className="text-red-500">*</span>
            </Label>
            <Select
              value={condition}
              onValueChange={setCondition}
              disabled={isLoading}
            >
              <SelectTrigger className={errors.condition ? 'border-red-500' : ''}>
                <SelectValue placeholder="Wybierz stan książki" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="new">Nowa</SelectItem>
                <SelectItem value="good">Dobra</SelectItem>
                <SelectItem value="fair">Średnia</SelectItem>
                <SelectItem value="poor">Słaba</SelectItem>
              </SelectContent>
            </Select>
            {errors.condition && (
              <p className="text-sm text-red-500">{errors.condition}</p>
            )}
          </div>

          {/* Helper text */}
          <div className="text-xs text-muted-foreground bg-muted/50 p-3 rounded-lg">
            <strong>Gdzie znaleźć ISBN?</strong><br />
            Numer ISBN znajdziesz na odwrocie okładki książki, nad kodem kreskowym. 
            Zazwyczaj ma 13 cyfr i zaczyna się od 978 lub 979.
          </div>
        </div>

        {!isProcessing && (
          <DialogFooter>
            <Button variant="outline" onClick={handleClose} disabled={isLoading}>
              <X className="h-4 w-4 mr-2" />
              Anuluj
            </Button>
            <Button 
              onClick={handleSubmit} 
              disabled={isLoading || isProcessing || success || !isIsbnValid}
              className="bg-book-gold hover:bg-book-gold-hover"
            >
              {isLoading || isProcessing ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <BookOpen className="h-4 w-4 mr-2" />
              )}
              Dodaj książkę
            </Button>
          </DialogFooter>
        )}
      </DialogContent>

      {/* Processing Animation Overlay - rendered via portal to cover everything */}
      {isProcessing && <ProcessingOverlay />}

    </Dialog>
  );
}

// Separate component for the overlay to use portal
function ProcessingOverlay() {
  return createPortal(
    <div className="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-black/95">
      <BookLoadingAnimation 
        message="Proszę czekać, trwa dodawanie książki..." 
        size="lg"
      />
      <p className="mt-6 text-sm text-stone-400 text-center max-w-xs">
        Pobieramy informacje o książce (tytuł, autor, okładka) i dodajemy ją do Twojej biblioteki.
      </p>
    </div>,
    document.body
  );
}
