import { Navbar } from '@/components/layout/Navbar';
import { FloatingBooks, GradientOrbs } from '@/components/layout/FloatingBooks';
import { Footer } from '@/components/layout/Footer';
import { BookOpen, Users, Sparkles, Heart, Shield, Globe } from 'lucide-react';
import { useAuth } from '@/components/auth/AuthContext';

export function AboutPage() {
  const { isAuthenticated } = useAuth();
  const values = [
    {
      icon: Users,
      title: 'Społeczność',
      description: 'Łączymy miłośników książek, tworząc sieć wymiany i odkrywania nowych tytułów.',
    },
    {
      icon: Sparkles,
      title: 'AI Bibliotekarz',
      description: 'Nasza sztuczna inteligencja pomaga znaleźć idealną książkę dopasowaną do Twoich preferencji.',
    },
    {
      icon: Shield,
      title: 'Bezpieczeństwo',
      description: 'Dbamy o bezpieczeństwo Twoich danych i transakcji wymiany książek.',
    },
    {
      icon: Heart,
      title: 'Pasja',
      description: 'Kochamy książki i wierzymy, że każda historia zasługuje na nowego czytelnika.',
    },
    {
      icon: Globe,
      title: 'Dostępność',
      description: 'Udostępniamy książki szerokiemu gronu czytelników, niezależnie od budżetu.',
    },
    {
      icon: BookOpen,
      title: 'Różnorodność',
      description: 'Od klasyki po współczesność - znajdziesz u nas książki z każdej kategorii.',
    },
  ];

  return (
    <div className="min-h-screen bg-warm-beige relative">
      <FloatingBooks />
      <GradientOrbs />
      <Navbar />
      
      <main className="relative z-10 pt-20">

        <section className="py-20 lg:py-32">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="font-serif text-4xl md:text-6xl font-bold text-book-brown mb-6">
              O <span className="text-book-gold">Sharebook</span>
            </h1>
            <p className="text-xl text-book-gray max-w-3xl mx-auto leading-relaxed">
              Jesteśmy platformą, która rewolucjonizuje sposób, w jaki ludzie dzielą się 
              książkami. Naszą misją jest stworzenie globalnej społeczności czytelników, 
              gdzie każda książka znajdzie nowego właściciela.
            </p>
          </div>
        </section>


        <section className="py-16 bg-white/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="font-serif text-3xl font-bold text-book-brown mb-4">
                  Nasza Misja
                </h2>
                <p className="text-book-gray mb-4 leading-relaxed">
                  Wierzymy, że książki powinny być dostępne dla każdego. W czasach, 
                  gdy wiele tomów zalega na półkach, a inni nie mogą sobie pozwolić 
                  na nowe zakupy, tworzymy most między posiadaczami a poszukiwaczami.
                </p>
                <p className="text-book-gray leading-relaxed">
                  Nasza platforma łączy technologię z pasją do czytania, 
                  oferując inteligentne dopasowanie książek do preferencji użytkowników.
                </p>
              </div>
              <div className="bg-gradient-to-br from-book-gold/10 to-book-brown/5 rounded-2xl p-8">
                <div className="text-center">
                  <div className="text-5xl font-bold text-book-gold mb-2">10,000+</div>
                  <div className="text-book-brown mb-6">Aktywnych użytkowników</div>
                  <div className="text-5xl font-bold text-book-gold mb-2">50,000+</div>
                  <div className="text-book-brown mb-6">Wymienionych książek</div>
                  <div className="text-5xl font-bold text-book-gold mb-2">98%</div>
                  <div className="text-book-brown">Zadowolonych użytkowników</div>
                </div>
              </div>
            </div>
          </div>
        </section>


        <section className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="font-serif text-3xl md:text-4xl font-bold text-book-brown mb-4">
                Nasze Wartości
              </h2>
              <p className="text-book-gray max-w-2xl mx-auto">
                To, co nas wyróżnia i kieruje naszymi działaniami każdego dnia.
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {values.map((value) => (
                <div
                  key={value.title}
                  className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-shadow"
                >
                  <div className="w-14 h-14 rounded-xl bg-book-gold/10 flex items-center justify-center mb-6">
                    <value.icon className="w-7 h-7 text-book-gold" />
                  </div>
                  <h3 className="font-serif text-xl font-semibold text-book-brown mb-3">
                    {value.title}
                  </h3>
                  <p className="text-book-gray leading-relaxed">
                    {value.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>


        <section className="py-20 bg-book-brown text-white">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="font-serif text-3xl md:text-4xl font-bold mb-6">
              Dołącz do naszej społeczności
            </h2>
            <p className="text-white/80 mb-8 text-lg">
              Zacznij dzielić się swoimi książkami już dziś. 
              To nic nie kosztuje, a może przynieść wiele radości.
            </p>
            {!isAuthenticated && (
              <a
                href="/register"
                className="inline-block bg-book-gold hover:bg-book-gold-hover text-white px-8 py-4 rounded-full font-medium transition-all"
              >
                Rozpocznij przygodę
              </a>
            )}
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
