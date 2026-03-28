import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/components/auth/AuthContext';
import { BookOpen, Loader2 } from 'lucide-react';

export function RegisterPage() {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    location: '',
    phone: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { register, isAuthenticated } = useAuth();

  // Redirect if already logged in
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/reader');
    }
  }, [isAuthenticated, navigate]);

  const validateForm = (): boolean => {
    // Walidacja imienia
    if (!formData.firstName.trim()) {
      setError('Imię jest wymagane');
      return false;
    }
    if (formData.firstName.trim().length < 2) {
      setError('Imię musi mieć co najmniej 2 znaki');
      return false;
    }

    // Walidacja nazwiska
    if (!formData.lastName.trim()) {
      setError('Nazwisko jest wymagane');
      return false;
    }
    if (formData.lastName.trim().length < 2) {
      setError('Nazwisko musi mieć co najmniej 2 znaki');
      return false;
    }

    // Walidacja email
    if (!formData.email.trim()) {
      setError('Adres email jest wymagany');
      return false;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Podaj poprawny adres email');
      return false;
    }

    // Walidacja hasła
    if (!formData.password) {
      setError('Hasło jest wymagane');
      return false;
    }
    if (formData.password.length < 8) {
      setError('Hasło musi mieć co najmniej 8 znaków');
      return false;
    }
    if (!formData.confirmPassword) {
      setError('Potwierdzenie hasła jest wymagane');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Hasła nie są identyczne');
      return false;
    }

    // Walidacja lokalizacji
    if (!formData.location.trim()) {
      setError('Lokalizacja jest wymagana');
      return false;
    }

    // Walidacja telefonu
    if (!formData.phone.trim()) {
      setError('Numer telefonu jest wymagany');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      await register({
        email: formData.email,
        password: formData.password,
        first_name: formData.firstName,
        last_name: formData.lastName,
        location: formData.location,
        phone: formData.phone,
      });
      navigate('/reader');
    } catch (err: any) {
      if (err.message) {
        // Konwersja komunikatów błędów z backendu na polskie
        const backendError = err.message.toLowerCase();
        if (backendError.includes('already registered') || backendError.includes('already exists') || backendError.includes('duplicate')) {
          setError('Użytkownik z tym adresem email już istnieje');
        } else if (backendError.includes('hasło jest za słabe') || backendError.includes('password')) {
          // Komunikat o słabym haśle z walidatora zxcvbn (już po polsku z backendu)
          setError(err.message);
        } else if (backendError.includes('invalid email')) {
          setError('Nieprawidłowy adres email');
        } else if (backendError.includes('validation') || backendError.includes('field required')) {
          setError('Nieprawidłowe dane. Sprawdź wprowadzone informacje i uzupełnij wszystkie wymagane pola');
        } else if (backendError.includes('internal server error')) {
          setError('Wystąpił błąd serwera. Spróbuj ponownie później');
        } else {
          // Jeśli nie znamy błędu, wyświetl go bezpośrednio (może być już po polsku)
          setError(err.message);
        }
      } else {
        setError('Rejestracja nie powiodła się. Spróbuj ponownie później');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-warm-beige flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="flex justify-center mb-6">
          <Link to="/" className="flex items-center gap-2 text-book-gold hover:text-book-gold-hover transition-colors">
            <BookOpen className="h-8 w-8" />
            <span className="text-2xl font-bold text-book-brown">Sharebook</span>
          </Link>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-book-brown">Utwórz konto</CardTitle>
            <CardDescription>Dołącz do naszej społeczności miłośników książek</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="firstName">Imię</Label>
                  <Input
                    id="firstName"
                    value={formData.firstName}
                    onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName">Nazwisko</Label>
                  <Input
                    id="lastName"
                    value={formData.lastName}
                    onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="name@example.com"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Hasło</Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Potwierdź hasło</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="location">Lokalizacja (miasto)</Label>
                <Input
                  id="location"
                  type="text"
                  placeholder="np. Warszawa"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  required
                />
                <p className="text-xs text-book-muted">
                  Podaj miasto, w którym będziesz wymieniać się książkami
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Telefon</Label>
                <Input
                  id="phone"
                  type="tel"
                  placeholder="np. +48 123 456 789"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  required
                />
                <p className="text-xs text-book-muted">
                  Podaj numer telefonu do kontaktu
                </p>
              </div>

              {error && (
                <p className="text-sm text-red-500">{error}</p>
              )}

              <Button type="submit" className="w-full bg-book-gold hover:bg-book-gold-hover" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Tworzenie konta...
                  </>
                ) : (
                  'Utwórz konto'
                )}
              </Button>
            </form>

            <p className="mt-4 text-center text-sm text-muted-foreground">
              Masz już konto?{' '}
              <Link to="/login" className="text-book-gold hover:underline">
                Zaloguj się
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
