import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  User, 
  Mail, 
  Calendar, 
  Shield, 
  ArrowLeft, 
  Lock,
  Loader2,
  MapPin
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Navbar } from '@/components/layout/Navbar';
import { FloatingBooks, GradientOrbs } from '@/components/layout/FloatingBooks';
import { useAuth } from '@/components/auth/AuthContext';
import { EditProfileForm } from './EditProfileForm';
import { ChangePasswordForm } from './ChangePasswordForm';

function ProfileInfo({ label, value, icon: Icon }: { label: string; value: string; icon: React.ElementType }) {
  return (
    <div className="flex items-start gap-4 p-4 rounded-xl bg-stone-50/50 border border-stone-100 min-w-0">
      <div className="w-10 h-10 rounded-lg bg-book-gold/10 flex items-center justify-center shrink-0">
        <Icon className="w-5 h-5 text-book-gold" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm text-book-muted mb-1">{label}</p>
        <p className="font-medium text-book-brown break-words">{value || '-'}</p>
      </div>
    </div>
  );
}

export function ProfilePage() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');

  if (authLoading) {
    return (
      <div className="min-h-screen bg-warm-beige flex items-center justify-center">
        <div className="flex items-center gap-2 text-book-gold">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span className="text-book-brown">Ładowanie...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-warm-beige flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-book-brown">Wymagane logowanie</CardTitle>
            <CardDescription>Zaloguj się, aby zobaczyć swój profil</CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => navigate('/login')} 
              className="w-full bg-book-gold hover:bg-book-gold-hover"
            >
              Zaloguj się
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pl-PL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-warm-beige relative">
      <FloatingBooks />
      <GradientOrbs />
      <Navbar />

      <main className="relative z-10 pt-16 lg:pt-20">
        <div className="max-w-4xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="mb-8">
            <Button
              variant="ghost"
              size="sm"
              className="mb-4 text-book-gray hover:text-book-brown"
              onClick={() => navigate(-1)}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Wróć
            </Button>
            
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h1 className="text-3xl font-serif font-bold text-book-brown mb-2">
                  Twój Profil
                </h1>
                <p className="text-book-muted">
                  Zarządzaj swoimi danymi i ustawieniami konta
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-book-gold/20 flex items-center justify-center">
                  <User className="w-6 h-6 text-book-gold" />
                </div>
                <div>
                  <p className="font-medium text-book-brown">
                    {user.first_name} {user.last_name}
                  </p>
                  <p className="text-sm text-book-muted">{user.email}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-3 bg-white/50">
              <TabsTrigger value="overview" className="data-[state=active]:bg-book-gold data-[state=active]:text-white">
                Przegląd
              </TabsTrigger>
              <TabsTrigger value="edit" className="data-[state=active]:bg-book-gold data-[state=active]:text-white">
                Edytuj profil
              </TabsTrigger>
              <TabsTrigger value="password" className="data-[state=active]:bg-book-gold data-[state=active]:text-white">
                Zmień hasło
              </TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview">
              <Card>
                <CardHeader>
                  <CardTitle className="text-book-brown">Informacje o koncie</CardTitle>
                  <CardDescription>
                    Podstawowe informacje o Twoim profilu
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    <ProfileInfo 
                      label="Imię"
                      value={user.first_name}
                      icon={User}
                    />
                    <ProfileInfo 
                      label="Nazwisko"
                      value={user.last_name}
                      icon={User}
                    />
                    <ProfileInfo 
                      label="Email"
                      value={user.email}
                      icon={Mail}
                    />
                    <ProfileInfo 
                      label="Rola"
                      value={user.role === 'admin' ? 'Administrator' : 'Użytkownik'}
                      icon={Shield}
                    />
                    <ProfileInfo 
                      label="Lokalizacja"
                      value={user.location || 'Nie podano'}
                      icon={MapPin}
                    />
                    <ProfileInfo 
                      label="Data dołączenia"
                      value={formatDate(user.created_at)}
                      icon={Calendar}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Edit Profile Tab */}
            <TabsContent value="edit">
              <Card>
                <CardHeader>
                  <CardTitle className="text-book-brown">Edytuj profil</CardTitle>
                  <CardDescription>
                    Zaktualizuj swoje dane osobowe
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <EditProfileForm 
                    user={user} 
                    onSuccess={() => setActiveTab('overview')}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            {/* Change Password Tab */}
            <TabsContent value="password">
              <Card>
                <CardHeader>
                  <CardTitle className="text-book-brown flex items-center gap-2">
                    <Lock className="w-5 h-5" />
                    Zmień hasło
                  </CardTitle>
                  <CardDescription>
                    Ustaw nowe hasło dla swojego konta
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ChangePasswordForm />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
}
