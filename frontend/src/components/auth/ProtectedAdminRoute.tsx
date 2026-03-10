import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '@/components/auth/AuthContext';
import { Loader2, ShieldAlert } from 'lucide-react';

export function ProtectedAdminRoute() {
  const { isAuthenticated, isAdmin, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-book-gold" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!isAdmin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-warm-beige">
        <div className="bg-white rounded-2xl shadow-lg border border-stone-200 p-8 max-w-md text-center">
          <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
            <ShieldAlert className="w-8 h-8 text-red-600" />
          </div>
          <h1 className="text-2xl font-serif font-bold text-book-brown mb-2">
            Brak dostępu
          </h1>
          <p className="text-book-muted mb-6">
            Nie masz uprawnień administratora. Wróć do panelu czytelnika.
          </p>
          <a
            href="/reader"
            className="inline-flex items-center justify-center px-6 py-3 rounded-xl bg-book-gold text-white font-medium hover:bg-book-gold-hover transition-colors"
          >
            Przejdź do Panelu Czytelnika
          </a>
        </div>
      </div>
    );
  }

  return <Outlet />;
}
