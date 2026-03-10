/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * KROK 4: DASHBOARD (STATYSTYKI) - PANEL ADMINISTRATORA
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * PLIK: frontend/src/pages/admin/DashboardSection.tsx
 * FAZA: 7 - Panel Administratora (Frontend)
 * 
 * CO TO ROBI?
 * ═══════════════════════════════════════════════════════════════════════════════
 * DashboardSection to główny pulpit administracyjny systemu ShareBook.
 * Wyświetla kluczowe metryki (KPI - Key Performance Indicators) pozwalające
 * administratorowi na szybką ocenę zdrowia i aktywności platformy.
 * 
 * WYŚWIETLANE STATYSTYKI:
 * ┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
 * │   UŻYTKOWNICY   │    KSIĄŻKI      │  WYPOŻYCZENIA   │   OCZEKUJĄCE    │
 * │                 │                 │                 │     PROŚBY      │
 * ├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
 * │  Ikona: Users   │ Ikona: BookOpen │Ikona: GitPullReq│  Ikona: Clock   │
 * │  Liczba total   │  Liczba total   │  Liczba total   │  Liczba total   │
 * │  "Zarejestrowani│  "W katalogu"   │ "Wszystkie"     │"Oczekujące na  │
 * │   użytkownicy"  │                 │                 │   akceptację"   │
 * └─────────────────┴─────────────────┴─────────────────┴─────────────────┘
 * 
 * ARCHITEKTURA KOMPONENTU:
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 *                    ┌─────────────────────────────────────┐
 *                    │        DashboardSection             │
 *                    │          (główny komponent)         │
 *                    └─────────────────┬───────────────────┘
 *                                      │
 *          ┌───────────────────────────┼───────────────────────────┐
 *          │                           │                           │
 *          ▼                           ▼                           ▼
 * ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
 │   StatCard      │        │  Loading State  │        │   Error State   │
 │  (podkomponent) │        │  (skeleton UI)  │        │  (error UI 403) │
 * └─────────────────┘        └─────────────────┘        └─────────────────┘
 *          │                           │                           │
 *          ▼                           ▼                           ▼
 * ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
 * │  Card (shadcn)  │        │  animate-pulse  │        │  Czerwony box   │
 * │  Ikona (lucide) │        │  szare karty    │        │  z komunikatem  │
 * │  Liczba + opis  │        │  symulujące UI  │        │  + redirect     │
 * └─────────────────┘        └─────────────────┘        └─────────────────┘
 * 
 * PRZEPŁYW DANYCH:
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 *  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
 *  │   Mount     │────▶│  useEffect  │────▶│adminApi.get │────▶│   Backend   │
 *  │ komponentu  │     │  fetchStats │     │  Dashboard  │     │  /admin/    │
 *  └─────────────┘     └─────────────┘     └──────┬──────┘     │  dashboard  │
 *                                                 │            └──────┬──────┘
 *                                                 │                   │
 *  ┌─────────────┐     ┌─────────────┐     ┌──────▼──────┐     ┌──────▼──────┐
 *  │  Render UI  │◀────│  setStats   │◀────│   Odpowiedź │◀────│  JSON ze    │
 *  │  z danymi   │     │  setLoading │     │   sukces    │     │ statystykami│
 *  └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
 * 
 * OBSLUGA BŁĘDÓW:
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Kod błędu 403 (Forbidden):
 * ─────────────────────────────────────────────────────────────────────────────
 * Jeśli użytkownik nie ma roli "admin", backend zwraca HTTP 403.
 * W takim przypadku:
 * 1. Wyświetlamy komunikat o braku uprawnień
 * 2. Można przekierować na stronę główną (opcjonalnie)
 * 3. Logujemy błąd do konsoli
 * 
 * Kod błędu 401 (Unauthorized):
 * ─────────────────────────────────────────────────────────────────────────────
 * Jeśli token wygasł, backend zwraca HTTP 401.
 * Interceptor w client.ts powinien obsłużyć przekierowanie do logowania.
 * 
 * Kod błędu 500 (Server Error):
 * ─────────────────────────────────────────────────────────────────────────────
 * Błąd serwera - wyświetlamy ogólny komunikat i sugerujemy retry.
 * 
 * NETWORK ERROR:
 * ─────────────────────────────────────────────────────────────────────────────
 * Brak połączenia z internetem - wyświetlamy odpowiedni komunikat.
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

// ═══════════════════════════════════════════════════════════════════════════════
// IMPORTY IKON Z LUCIDE-REACT
// ═══════════════════════════════════════════════════════════════════════════════
// Lucide to nowoczesna biblioteka ikon, następca Feather Icons.
// Każda ikona to komponent React, który można stylizować przez propsy (className, size, itp.)
// 
// Users       - ikona grupy ludzi (reprezentuje użytkowników)
// BookOpen    - ikona otwartej książki (reprezentuje katalog książek)
// GitPullRequest - ikona PR (reprezentuje wypożyczenia/przepływ)
// Clock       - ikona zegara (reprezentuje oczekujące prośby)
import { Users, BookOpen, GitPullRequest, Clock } from 'lucide-react';

// ═══════════════════════════════════════════════════════════════════════════════
// IMPORTY KOMPONENTÓW UI Z SHADCN/UI
// ═══════════════════════════════════════════════════════════════════════════════
// shadcn/ui to biblioteka komponentów UI oparta na Radix UI + Tailwind CSS.
// Komponenty są "headless" (logika w Radix) + "styled" (wygląd w Tailwind).
// 
// Card        - kontener z cieniem, obramowaniem, zaokrągleniem
// CardHeader  - górna część karty (tytuł + akcje)
// CardTitle   - stylizowany tytuł karty
// CardContent - główna zawartość karty (padding, typografia)
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

// ═══════════════════════════════════════════════════════════════════════════════
// IMPORTY API
// ═══════════════════════════════════════════════════════════════════════════════
// adminApi    - obiekt z metodami do endpointów administracyjnych
// AdminDashboardStats - interfejs TypeScript definiujący strukturę odpowiedzi
import { adminApi, type AdminDashboardStats } from '@/api/admin';

// ═══════════════════════════════════════════════════════════════════════════════
// INTERFEJS PROPS DLA STATCARD
// ═══════════════════════════════════════════════════════════════════════════════
/**
 * StatCardProps - definicja właściwości komponentu StatCard
 * 
 * @property title       - tytuł karty (np. "Użytkownicy")
 * @property value       - wartość liczbowa do wyświetlenia (np. 42)
 * @property description - opis/podtytuł (np. "Zarejestrowani użytkownicy")
 * @property icon        - komponent ikony z lucide-react (np. Users)
 * 
 * DLACZEGO icon: React.ElementType?
 * ─────────────────────────────────────────────────────────────────────────────
 * Lucide eksportuje ikony jako komponenty React. Przekazujemy je jako referencję
 * do komponentu (nie jako JSX), aby móc wewnątrz StatCard użyć:
 *   <Icon className="..." />
 * 
 * To wzorzec "render props" - pozwala na dynamiczne renderowanie różnych ikon
 * w zależności od danych.
 */
interface StatCardProps {
  title: string;
  value: number;
  description: string;
  icon: React.ElementType;
}

// ═══════════════════════════════════════════════════════════════════════════════
// KOMPONENT STATCARD (PODKOMPONENT)
// ═══════════════════════════════════════════════════════════════════════════════
/**
 * StatCard - karta wyświetlająca pojedynczą statystykę
 * 
 * CO TO ROBI?
 * ═══════════════════════════════════════════════════════════════════════════════
 * Renderuje kartę z:
 * - Ikoną w kolorowym kółku (tło primary/10, ikona primary)
 * - Dużą liczbą (text-3xl font-bold)
 * - Podtytułem opisującym znaczenie liczby
 * 
 * STRUKTURA WIZUALNA:
 * ═══════════════════════════════════════════════════════════════════════════════
 * ┌─────────────────────────────────────────────────────────────────────────────┐
 * │  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐   │
 * │  │ TYTUŁ (text-sm, muted)          │  │        ┌─────────────┐          │   │
 * │  │ np. "Użytkownicy"               │  │        │   IKONA     │          │   │
 * │  │                                 │  │        │  (w kółku)  │          │   │
 * │  │                                 │  │        └─────────────┘          │   │
 * │  └─────────────────────────────────┘  └─────────────────────────────────┘   │
 * │                                                                             │
 * │  ┌─────────────────────────────────────────────────────────────────────┐    │
 * │  │ WARTOŚĆ (text-3xl, bold)                                            │    │
 * │  │ np. "1 234" (sformatowana przez toLocaleString('pl-PL'))           │    │
 * │  └─────────────────────────────────────────────────────────────────────┘    │
 * │                                                                             │
 * │  OPIS (text-xs, muted) - np. "Zarejestrowani użytkownicy"                   │
 * └─────────────────────────────────────────────────────────────────────────────┘
 * 
 * FORMATOWANIE LICZB:
 * ═══════════════════════════════════════════════════════════════════════════════
 * Używamy toLocaleString('pl-PL') aby:
 * - Używać polskich separatorów tysięcy (spacja, nie przecinek)
 * - Używać polskiego separatora dziesiętnego (przecinek, nie kropka)
 * 
 * Przykłady:
 *   1234  → "1 234"
 *   1234567 → "1 234 567"
 *   1234.56 → "1 234,56"
 * 
 * @param props - właściwości zgodne z interfejsem StatCardProps
 * @returns JSX.Element - gotowa karta ze statystyką
 */
function StatCard({ title, value, description, icon: Icon }: StatCardProps) {
  return (
    <Card>
      {/* CardHeader - górna część z tytułem i ikoną */}
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        {/* Tytuł karty - mały, wyszarzony tekst */}
        <CardTitle className="text-sm font-medium text-muted">
          {title}
        </CardTitle>
        {/* Kontener na ikonę - kolorowe tło z zaokrągleniem */}
        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
          {/* Ikona przekazana jako prop - renderujemy ją tutaj */}
          <Icon className="w-5 h-5 text-primary" />
        </div>
      </CardHeader>
      
      {/* CardContent - główna zawartość z liczbą i opisem */}
      <CardContent>
        {/* Wartość główna - duża, pogrubiona liczba */}
        <div className="text-3xl font-bold">
          {/* Formatowanie liczby zgodnie z polskimi standardami */}
          {value.toLocaleString('pl-PL')}
        </div>
        {/* Opis - mały tekst wyjaśniający co oznacza liczba */}
        <p className="text-xs text-muted mt-1">{description}</p>
      </CardContent>
    </Card>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// GŁÓWNY KOMPONENT DASHBOARDSECTION
// ═══════════════════════════════════════════════════════════════════════════════
/**
 * DashboardSection - główny komponent dashboardu administratora
 * 
 * CO TO ROBI?
 * ═══════════════════════════════════════════════════════════════════════════════
 * 1. Zarządza stanem (stats, loading, error)
 * 2. Pobiera dane z API przy montowaniu komponentu (useEffect)
 * 3. Renderuje odpowiedni UI w zależności od stanu:
 *    - loading → skeleton screen
 *    - error   → komunikat błędu (z obsługą 403)
 *    - success → siatka kart ze statystykami
 * 
 * STANY KOMPONENTU:
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
 * │   stats     │     │   loading   │     │    error    │
 * ├─────────────┤     ├─────────────┤     ├─────────────┤
 * │ null        │     │ true        │     │ null        │ ← początkowy
 * │ AdminDash   │     │ false       │     │ string      │ ← po fetch
 * │ boardStats  │     │             │     │             │
 * │ | null      │     │             │     │             │
 * └─────────────┘     └─────────────┘     └─────────────┘
 * 
 * PRZEPŁYW STANÓW W CZASIE:
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Timeline:  [Mount] ──▶ [Fetch] ──▶ [Success] / [Error]
 *            ───────────  ─────────   ────────────
 * stats:     null         null        data / null
 * loading:   true         true        false
 * error:     null         null        null / message
 * 
 * OBSŁUGA BŁĘDU 403 (FORBIDDEN):
 * ═══════════════════════════════════════════════════════════════════════════════
 * Jeśli użytkownik próbuje uzyskać dostęp do /admin/dashboard bez uprawnień
 * administratora, backend zwraca HTTP 403.
 * 
 * W takim przypadku:
 * 1. Wyświetlamy czerwony komunikat o braku dostępu
 * 2. Po 3 sekundach przekierowujemy na stronę główną (/)
 * 3. Zapobiega to "utknięciu" na stronie bez uprawnień
 * 
 * DLACZEGU useEffect Z PUSTĄ TABLICĄ ZALEŻNOŚCI []?
 * ═══════════════════════════════════════════════════════════════════════════════
 * Pusta tablica [] oznacza "uruchom tylko raz, przy montowaniu komponentu".
 * To odpowiednik componentDidMount z klasowych komponentów React.
 * 
 * Nie chcemy pobierać statystyk przy każdej aktualizacji komponentu,
 * tylko raz - gdy użytkownik wchodzi na stronę dashboardu.
 */
export function DashboardSection() {
  // ═══════════════════════════════════════════════════════════════════════════
  // STANY KOMPONENTU (useState)
  // ═══════════════════════════════════════════════════════════════════════════
  
  /**
   * stats - przechowuje pobrane statystyki
   * Typ: AdminDashboardStats | null
   * - null na początku (dane jeszcze nie pobrane)
   - AdminDashboardStats po udanym fetchu
   */
  const [stats, setStats] = useState<AdminDashboardStats | null>(null);
  
  /**
   * loading - flaga informująca czy trwa pobieranie danych
   * Typ: boolean
   * - true podczas oczekiwania na odpowiedź API
   * - false po zakończeniu (sukces lub błąd)
   */
  const [loading, setLoading] = useState(true);
  
  /**
   * error - przechowuje komunikat błędu
   * Typ: string | null
   * - null gdy brak błędu
   * - string z komunikatem gdy wystąpił błąd
   */
  const [error, setError] = useState<string | null>(null);

  // Hook nawigacji z react-router - używany do przekierowania przy błędzie 403
  const navigate = useNavigate();

  // ═══════════════════════════════════════════════════════════════════════════
  // EFEKT - POBIERANIE DANYCH PRZY MONTOWANIU
  // ═══════════════════════════════════════════════════════════════════════════
  useEffect(() => {
    /**
     * fetchStats - asynchroniczna funkcja pobierająca statystyki
     * 
     * KROKI:
     * 1. Ustaw loading = true (pokaż skeleton)
     * 2. Wywołaj adminApi.getDashboard()
     * 3. Jeśli sukces → zapisz dane, wyczyść error
     * 4. Jeśli błąd → zapisz komunikat, obsłuż 403
     * 5. Niezależnie od wyniku → loading = false
     */
    const fetchStats = async () => {
      try {
        // Rozpoczynamy ładowanie - pokaż skeleton
        setLoading(true);
        
        // Wywołanie API - GET /admin/dashboard
        // Oczekiwana odpowiedź: { data: AdminDashboardStats }
        const response = await adminApi.getDashboard();
        
        // Sprawdzenie czy odpowiedź zawiera dane
        if (response.data) {
          setStats(response.data);
          // Wyczyść ewentualny poprzedni błąd
          setError(null);
        }
      } catch (err: unknown) {
        // Obsługa błędów - sprawdzamy typ błędu
        
        // Sprawdzenie czy to błąd HTTP 403 (Forbidden)
        // W axios błąd 403 jest w err.response.status
        // W naszym apiClient może to być inaczej w zależności od implementacji
        const errorObj = err as { response?: { status?: number }; message?: string };
        
        if (errorObj.response?.status === 403) {
          // Błąd 403 - użytkownik nie jest adminem
          setError('Brak uprawnień. Ta sekcja jest dostępna tylko dla administratorów.');
          
          // Opcjonalnie: przekierowanie po 3 sekundach
          // Użytkownik ma czas przeczytać komunikat
          setTimeout(() => {
            navigate('/');
          }, 3000);
        } else if (errorObj.response?.status === 401) {
          // Błąd 401 - sesja wygasła
          setError('Sesja wygasła. Zaloguj się ponownie.');
        } else if (errorObj.message?.includes('Network Error')) {
          // Błąd sieci - brak połączenia
          setError('Brak połączenia z serwerem. Sprawdź internet.');
        } else {
          // Inny błąd - ogólny komunikat
          setError(err instanceof Error ? err.message : 'Błąd pobierania statystyk');
        }
        
        // Logowanie błędu do konsoli (dla debugowania)
        console.error('Dashboard fetch error:', err);
      } finally {
        // Zawsze kończymy ładowanie, niezależnie od wyniku
        setLoading(false);
      }
    };

    // Wywołanie funkcji pobierającej
    fetchStats();
  }, []); // Pusta tablica = tylko przy montowaniu

  // ═══════════════════════════════════════════════════════════════════════════
  // RENDEROWANIE - STAN ŁADOWANIA (LOADING)
  // ═══════════════════════════════════════════════════════════════════════════
  /**
   * Skeleton Screen - stan podczas pobierania danych
   * 
   * DLACZEGO SKELETON A NIE SPINNER?
   * ═══════════════════════════════════════════════════════════════════════════
   * Skeleton (szkielet UI) jest lepszy niż spinner ponieważ:
   * 1. Pokazuje strukturę finalnego UI - użytkownik wie czego się spodziewać
   * 2. Daje poczucie szybkości (perceived performance)
   * 3. Mniej frustrujący niż obracający się kręciołek
   * 
   * IMPLEMENTACJA:
   * - Używamy komponentu Card z klasą animate-pulse
   * - Tło bg-gray-100 (jasnoszare) symuluje miejsce na treść
   * - Wysokość h-32 odpowiada wysokości prawdziwej karty
   * 
   * UKŁAD:
   * ┌─────────────────────────────────────────────────────────────────────────────┐
   * │  Dashboard                                                                  │
   * │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
   * │  │  ████████   │ │  ████████   │ │  ████████   │ │  ████████   │  pulse... │
   * │  │  ████████   │ │  ████████   │ │  ████████   │ │  ████████   │           │
   * │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
   * └─────────────────────────────────────────────────────────────────────────────┘
   */
  if (loading) {
    return (
      <div className="space-y-6">
        {/* Nagłówek */}
        <h1 className="text-2xl font-bold">Dashboard</h1>
        
        {/* Siatka 4 skeletonów (odpowiada 4 statystykom) */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="h-32 animate-pulse bg-gray-100" />
          ))}
        </div>
      </div>
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // RENDEROWANIE - STAN BŁĘDU (ERROR)
  // ═══════════════════════════════════════════════════════════════════════════
  /**
   * Error State - stan po wystąpieniu błędu
   * 
   * WYGLĄD:
   * Czerwone obramowanie (border-red-200) + czerwone tło (bg-red-50) +
   * czerwony tekst (text-red-600) + zaokrąglenie (rounded-xl)
   * 
   * OBSŁUGA 403:
   * Jeśli error zawiera informację o braku uprawnień, wyświetlamy dodatkową
   * informację o przekierowaniu.
   */
  if (error) {
    const isForbidden = error.includes('Brak uprawnień');
    
    return (
      <div className="space-y-6">
        {/* Nagłówek pozostaje widoczny */}
        <h1 className="text-2xl font-bold">Dashboard</h1>
        
        {/* Komunikat błędu */}
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600">
          <div className="flex items-start gap-3">
            {/* Ikona ostrzeżenia */}
            <svg 
              className="w-5 h-5 mt-0.5 flex-shrink-0" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
              />
            </svg>
            <div>
              {/* Główny komunikat */}
              <p className="font-medium">{error}</p>
              
              {/* Dodatkowa informacja dla błędu 403 */}
              {isForbidden && (
                <p className="text-sm mt-2 text-red-500">
                  Za chwilę zostaniesz przekierowany na stronę główną...
                </p>
              )}
              
              {/* Przycisk ponowienia próby (nie dla 403) */}
              {!isForbidden && (
                <button
                  onClick={() => window.location.reload()}
                  className="mt-3 text-sm underline hover:no-underline"
                >
                  Odśwież stronę
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // PRZYGOTOWANIE DANYCH DO WYŚWIETLENIA
  // ═══════════════════════════════════════════════════════════════════════════
  /**
   * Fallback dla stats - zabezpieczenie przed null
   * 
   * Nawet jeśli stats jest null (teoretycznie nie powinno tak być po loading=false
   * i error=null, ale TypeScript tego nie wie), wyświetlimy zera zamiast crashować.
   */
  const currentStats = stats || {
    total_users: 0,
    total_books: 0,
    total_loans: 0,
    pending_requests: 0,
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // RENDEROWANIE - STAN SUKCESU (SUCCESS)
  // ═══════════════════════════════════════════════════════════════════════════
  /**
   * Normalny stan - wyświetlenie dashboardu ze statystykami
   * 
   * UKŁAD:
   * ═══════════════════════════════════════════════════════════════════════════
   * 
   * ┌─────────────────────────────────────────────────────────────────────────────┐
   * │  Dashboard                                                                  │
   * │  Przegląd aktywności platformy                                              │
   * ├─────────────────────────────────────────────────────────────────────────────┤
   * │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌────────────┐ │
   * │  │ UŻYTKOWNICY     │ │ KSIĄŻKI         │ │ WYPOŻYCZENIA    │ │ OCZEKUJĄCE │ │
   * │  │ [icon]          │ │ [icon]          │ │ [icon]          │ │ [icon]     │ │
   * │  │                 │ │                 │ │                 │ │            │ │
   * │  │ 1 234           │ │ 567             │ │ 89              │ │ 12         │ │
   * │  │ Zarejestrowani  │ │ W katalogu      │ │ Wszystkie       │ │ Oczekujące │ │
   * │  │ użytkownicy     │ │                 │ │                 │ │ na akcept. │ │
   * │  └─────────────────┘ └─────────────────┘ └─────────────────┘ └────────────┘ │
   * └─────────────────────────────────────────────────────────────────────────────┘
   * 
   * RESPONSYWNOŚĆ SIATKI:
   * ═══════════════════════════════════════════════════════════════════════════
   * - grid-cols-1      : Mobile (< 768px)    - 1 kolumna (karty pod sobą)
   * - md:grid-cols-2   : Tablet (768px+)     - 2 kolumny
   * - lg:grid-cols-4   : Desktop (1024px+)   - 4 kolumny (wszystkie w rzędzie)
   * 
   * gap-4 = odstęp 1rem (16px) między kartami
   */
  return (
    <div className="space-y-6">
      {/* Nagłówek sekcji */}
      <div>
        <h1 className="text-2xl font-serif font-bold">Dashboard</h1>
        <p className="text-muted mt-1">Przegląd aktywności platformy</p>
      </div>

      {/* Siatka 4 kart ze statystykami */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Karta 1: Użytkownicy */}
        <StatCard
          title="Użytkownicy"
          value={currentStats.total_users}
          description="Zarejestrowani użytkownicy"
          icon={Users}
        />
        
        {/* Karta 2: Książki */}
        <StatCard
          title="Książki"
          value={currentStats.total_books}
          description="Książki w katalogu"
          icon={BookOpen}
        />
        
        {/* Karta 3: Wypożyczenia */}
        <StatCard
          title="Wypożyczenia"
          value={currentStats.total_loans}
          description="Wszystkie wypożyczenia"
          icon={GitPullRequest}
        />
        
        {/* Karta 4: Oczekujące prośby */}
        <StatCard
          title="Oczekujące"
          value={currentStats.pending_requests}
          description="Prośby oczekujące na akceptację"
          icon={Clock}
        />
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// KONIEC PLIKU
// ═══════════════════════════════════════════════════════════════════════════════
// 
// EKSPORT:
// - DashboardSection (domyślny export dla tego komponentu)
// - StatCard (można użyć zewnętrznie jeśli potrzeba)
//
// UŻYCIE W ROUTERZE:
// ═══════════════════════════════════════════════════════════════════════════════
// W AdminPanelPage.tsx:
// 
// import { DashboardSection } from './DashboardSection';
// 
// <Routes>
//   <Route path="dashboard" element={<DashboardSection />} />
//   <Route path="users" element={<UsersSection />} />
//   <Route path="books" element={<BooksSection />} />
// </Routes>
//
// UŻYCIE W API (admin.ts):
// ═══════════════════════════════════════════════════════════════════════════════
// 
// export interface AdminDashboardStats {
//   total_users: number;
//   total_books: number;
//   total_loans: number;
//   pending_requests: number;
// }
//
// export const adminApi = {
//   getDashboard: () => api.get<{ data: AdminDashboardStats }>('/admin/dashboard'),
//   // ...
// };
//
// TESTY (przykładowe):
// ═══════════════════════════════════════════════════════════════════════════════
// 
// describe('DashboardSection', () => {
//   it('renders loading state initially', () => {
//     render(<DashboardSection />);
//     expect(screen.getByText('Dashboard')).toBeInTheDocument();
//     expect(screen.getAllByRole('generic', { class: 'animate-pulse' })).toHaveLength(4);
//   });
//
//   it('renders stats after fetch', async () => {
//     mockApi.getDashboard.mockResolvedValue({
//       data: { total_users: 100, total_books: 50, total_loans: 25, pending_requests: 5 }
//     });
//     render(<DashboardSection />);
//     await waitFor(() => expect(screen.getByText('100')).toBeInTheDocument());
//   });
//
//   it('handles 403 error', async () => {
//     mockApi.getDashboard.mockRejectedValue({ response: { status: 403 } });
//     render(<DashboardSection />);
//     await waitFor(() => expect(screen.getByText(/brak uprawnień/i)).toBeInTheDocument());
//   });
// });
