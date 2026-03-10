import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/components/auth/AuthContext';
import { BookOpen, Loader2 } from 'lucide-react';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();

  // Redirect if already logged in
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/reader');
    }
  }, [isAuthenticated, navigate]);

  const validateForm = (): boolean => {
    if (!email.trim()) {
      setError('Adres email jest wymagany');
      return false;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Podaj poprawny adres email');
      return false;
    }
    if (!password) {
      setError('Hasło jest wymagane');
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
      await login(email, password);
      navigate('/reader');
    } catch (err: any) {
      if (err.message) {
        const backendError = err.message.toLowerCase();
        if (backendError.includes('incorrect') || backendError.includes('unauthorized')) {
          setError('Nieprawidłowy email lub hasło');
        } else if (backendError.includes('user not found')) {
          setError('Nie znaleziono użytkownika z tym adresem email');
        } else {
          setError(err.message);
        }
      } else {
        setError('Logowanie nie powiodło się. Spróbuj ponownie później');
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
            <CardTitle className="text-book-brown">Zaloguj się</CardTitle>
            <CardDescription>Wprowadź swoje dane, aby uzyskać dostęp do konta</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Hasło</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              {error && (
                <p className="text-sm text-red-500">{error}</p>
              )}

              <Button type="submit" className="w-full bg-book-gold hover:bg-book-gold-hover" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Logowanie...
                  </>
                ) : (
                  'Zaloguj się'
                )}
              </Button>
            </form>

            <p className="mt-4 text-center text-sm text-muted-foreground">
              Nie masz konta?{' '}
              <Link to="/register" className="text-book-gold hover:underline">
                Zarejestruj się
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
