import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { aiApi } from '@/api/ai';
import { useNavigate } from 'react-router-dom';
import { Users, BookOpen, GitPullRequest, Clock } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { adminApi, type AdminDashboardStats } from '@/api/admin';

interface StatCardProps {
  title: string;
  value: number;
  description: string;
  icon: React.ElementType;
}

function StatCard({ title, value, description, icon: Icon }: StatCardProps) {
  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <h3 className="text-3xl font-bold mt-2">{value.toLocaleString('pl-PL')}</h3>
          <p className="text-sm text-muted-foreground mt-1">{description}</p>
        </div>
        <div className="p-3 bg-primary/10 rounded-lg">
          <Icon className="w-5 h-5 text-primary" />
        </div>
      </div>
    </Card>
  );
}

function AdminRAGSection() {
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<{ success: boolean; indexed: number } | null>(null);

  const handleSync = async () => {
    setIsSyncing(true);
    setSyncResult(null);
    try {
      const result = await aiApi.sync();
      setSyncResult({ success: true, indexed: result.indexed_books });
    } catch (e) {
      setSyncResult({ success: false, indexed: 0 });
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="mt-8 p-6 border rounded-xl bg-slate-50">
      <h2 className="text-lg font-semibold mb-4">Baza wiedzy AI</h2>
      <div className="flex items-center gap-4">
        <Button 
          onClick={handleSync} 
          disabled={isSyncing}
          variant="default"
        >
          {isSyncing ? 'Synchronizacja...' : 'Zsynchronizuj bazę wiedzy'}
        </Button>
        {syncResult && (
          <span className={syncResult.success ? 'text-green-600' : 'text-red-600'}>
            {syncResult.success 
              ? `Zsynchronizowano ${syncResult.indexed} książek` 
              : 'Błąd synchronizacji'}
          </span>
        )}
      </div>
    </div>
  );
}

export function DashboardSection() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<AdminDashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await adminApi.getDashboard();
        const data = response.data;
        setStats(data);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Nieznany błąd';
        setError(message);
        if (message.includes('403') || message.includes('Brak uprawnień')) {
          setTimeout(() => navigate('/'), 3000);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [navigate]);

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="h-32 animate-pulse bg-gray-100" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    const isForbidden = error.includes('Brak uprawnień');
    
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="font-medium">{error}</p>
              {isForbidden && (
                <p className="text-sm mt-2 text-red-500">
                  Za chwilę zostaniesz przekierowany na stronę główną...
                </p>
              )}
              {!isForbidden && (
                <button onClick={() => window.location.reload()} className="mt-3 text-sm underline hover:no-underline">
                  Odśwież stronę
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const currentStats = stats || {
    total_users: 0,
    total_books: 0,
    total_loans: 0,
    pending_requests: 0,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-serif font-bold">Dashboard</h1>
        <p className="text-muted mt-1">Przegląd aktywności platformy</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Użytkownicy"
          value={currentStats.total_users}
          description="Zarejestrowani użytkownicy"
          icon={Users}
        />
        <StatCard
          title="Książki"
          value={currentStats.total_books}
          description="Książki w katalogu"
          icon={BookOpen}
        />
        <StatCard
          title="Wypożyczenia"
          value={currentStats.total_loans}
          description="Wszystkie wypożyczenia"
          icon={GitPullRequest}
        />
        <StatCard
          title="Oczekujące"
          value={currentStats.pending_requests}
          description="Prośby oczekujące na akceptację"
          icon={Clock}
        />
      </div>

      <AdminRAGSection />
    </div>
  );
}
