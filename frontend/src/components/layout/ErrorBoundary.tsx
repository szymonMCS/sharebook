import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw, BookX } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

/**
 * ErrorBoundary - komponent klasy łapiący błędy React w całej aplikacji
 * 
 * Użycie:
 * ```tsx
 * <ErrorBoundary>
 *   <YourComponent />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends Component<Props, State> {
  state: State = {
    hasError: false,
  };

  static getDerivedStateFromError(error: Error): State {
    // Zaktualizuj stan, aby następny render pokazał fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Logowanie błędów do konsoli
    console.error('ErrorBoundary caught an error:', error);
    console.error('Error details:', errorInfo.componentStack);

    this.setState({
      error,
      errorInfo,
    });

    // Opcjonalnie: wysłanie błędu do usługi zewnętrznej (Sentry, LogRocket itp.)
    // reportError(error, errorInfo);
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: undefined,
      errorInfo: undefined,
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Jeśli przekazano customowy fallback, użyj go
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const { error, errorInfo } = this.state;
      const isDevelopment = import.meta.env.DEV;

      return (
        <div className="min-h-screen bg-warm-beige flex items-center justify-center p-4">
          <div className="w-full max-w-2xl bg-white rounded-2xl shadow-book p-8 md:p-12 animate-fade-in-up">
            {/* Ikona błędu */}
            <div className="flex justify-center mb-6">
              <div className="w-20 h-20 rounded-full bg-red-50 flex items-center justify-center">
                <BookX className="w-10 h-10 text-red-500" />
              </div>
            </div>

            {/* Nagłówek */}
            <div className="text-center mb-8">
              <div className="flex items-center justify-center gap-2 mb-3">
                <AlertTriangle className="w-5 h-5 text-amber-500" />
                <span className="text-sm font-medium text-amber-600 uppercase tracking-wide">
                  Ups! Coś poszło nie tak
                </span>
              </div>
              <h1 className="font-serif text-3xl md:text-4xl font-bold text-book-brown mb-3">
                Wystąpił nieoczekiwany błąd
              </h1>
              <p className="text-book-gray max-w-md mx-auto">
                Przepraszamy za niedogodności. Nasz system napotkał problem podczas wyświetlania tej strony.
              </p>
            </div>

            {/* Szczegóły błędu - tylko w development */}
            {isDevelopment && error && (
              <div className="mb-8 space-y-4">
                <div className="bg-stone-50 rounded-lg p-4 border border-stone-200">
                  <h3 className="text-sm font-semibold text-book-brown mb-2">
                    Komunikat błędu:
                  </h3>
                  <p className="text-sm text-red-600 font-mono bg-white p-3 rounded border border-stone-200 overflow-x-auto">
                    {error.message}
                  </p>
                </div>

                {errorInfo && (
                  <div className="bg-stone-50 rounded-lg p-4 border border-stone-200">
                    <h3 className="text-sm font-semibold text-book-brown mb-2">
                      Stack trace:
                    </h3>
                    <pre className="text-xs text-book-gray font-mono bg-white p-3 rounded border border-stone-200 overflow-x-auto whitespace-pre-wrap max-h-64 overflow-y-auto">
                      {errorInfo.componentStack}
                    </pre>
                  </div>
                )}

                {error.stack && (
                  <div className="bg-stone-50 rounded-lg p-4 border border-stone-200">
                    <h3 className="text-sm font-semibold text-book-brown mb-2">
                      Full stack trace:
                    </h3>
                    <pre className="text-xs text-book-gray font-mono bg-white p-3 rounded border border-stone-200 overflow-x-auto whitespace-pre-wrap max-h-64 overflow-y-auto">
                      {error.stack}
                    </pre>
                  </div>
                )}
              </div>
            )}

            {/* Uproszczony komunikat w produkcji */}
            {!isDevelopment && (
              <div className="mb-8 bg-amber-50 rounded-lg p-4 border border-amber-200">
                <p className="text-sm text-amber-800 text-center">
                  Jeśli problem będzie się powtarzał, skontaktuj się z naszym zespołem wsparcia.
                </p>
              </div>
            )}

            {/* Przyciski akcji */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button
                onClick={this.handleReset}
                variant="outline"
                className="border-stone-300 text-book-brown hover:bg-stone-100"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Spróbuj ponownie
              </Button>
              <Button
                onClick={this.handleReload}
                className="bg-book-gold hover:bg-book-gold-hover text-white"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Odśwież stronę
              </Button>
            </div>

            {/* Stopka */}
            <div className="mt-8 pt-6 border-t border-stone-200 text-center">
              <p className="text-xs text-book-muted">
                ShareBook - Dziel się książkami, odkrywaj nowe historie
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
