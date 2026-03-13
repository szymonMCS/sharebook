import { useEffect, useState } from 'react';
import { ArrowRight, BookOpen, Sparkles, Users, Library } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/components/auth/AuthContext';

// Floating book icon component
function FloatingIcon({ 
  icon: Icon, 
  className, 
  delay = 0 
}: { 
  icon: typeof BookOpen; 
  className?: string; 
  delay?: number;
}) {
  return (
    <div 
      className={`absolute text-book-gold/10 animate-float ${className}`}
      style={{ animationDelay: `${delay}s` }}
    >
      <Icon strokeWidth={1} size={48} />
    </div>
  );
}

// Stats counter component
function StatCounter({ 
  value, 
  label, 
  icon: Icon 
}: { 
  value: string; 
  label: string; 
  icon: typeof BookOpen;
}) {
  return (
    <div className="flex items-center gap-3 px-6 py-4 bg-white/60 backdrop-blur-sm rounded-xl border border-stone-200/50">
      <div className="w-12 h-12 rounded-full bg-book-gold/10 flex items-center justify-center">
        <Icon className="w-6 h-6 text-book-gold" />
      </div>
      <div>
        <div className="font-serif text-2xl font-bold text-book-brown">{value}</div>
        <div className="text-sm text-book-gray">{label}</div>
      </div>
    </div>
  );
}

export function HeroSection() {
  const { isAuthenticated } = useAuth();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const scrollToBooks = () => {
    const booksSection = document.getElementById('featured-books');
    booksSection?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-warm-beige via-warm-cream to-warm-beige" />
      
      {/* Floating icons */}
      <FloatingIcon icon={BookOpen} className="top-20 left-[10%]" delay={0} />
      <FloatingIcon icon={Library} className="top-40 right-[15%]" delay={1} />
      <FloatingIcon icon={Sparkles} className="bottom-32 left-[20%]" delay={2} />
      <FloatingIcon icon={Users} className="top-60 left-[5%]" delay={1.5} />
      <FloatingIcon icon={BookOpen} className="bottom-40 right-[10%]" delay={0.5} />
      
      {/* Decorative circles */}
      <div 
        className="absolute top-20 right-20 w-64 h-64 rounded-full border border-book-gold/10 animate-pulse-soft"
      />
      <div 
        className="absolute bottom-20 left-20 w-48 h-48 rounded-full border border-book-gold/10 animate-pulse-soft"
        style={{ animationDelay: '2s' }}
      />
      <div 
        className="absolute top-1/3 right-1/4 w-32 h-32 rounded-full bg-book-gold/5 animate-float-slow"
      />
      
      {/* Main content */}
      <div className="relative z-10 text-center px-4 max-w-5xl mx-auto pt-20">
        {/* Badge */}
        <div 
          className={`inline-flex items-center gap-2 px-4 py-2 bg-book-gold/10 rounded-full mb-6 transition-all duration-700 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
          }`}
        >
          <Sparkles className="w-4 h-4 text-book-gold" />
          <span className="text-sm font-medium text-book-gold">
            Twoja Wirtualna Biblioteczka
          </span>
        </div>
        
        {/* Main headline */}
        <h1 
          className={`font-serif text-5xl md:text-6xl lg:text-7xl font-bold text-book-brown mb-6 leading-tight transition-all duration-700 delay-100 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          Dziel się książkami
          <br />
          <span className="text-book-gold">z przyjaciółmi</span>
        </h1>
        
        {/* Subtitle */}
        <p 
          className={`text-lg md:text-xl text-book-gray mb-10 max-w-2xl mx-auto leading-relaxed transition-all duration-700 delay-200 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          Dodaj swoje książki do wirtualnej półki, wypożyczaj od znajomych
          i odkrywaj nowe historie z pomocą naszego{' '}
          <span className="text-book-gold font-medium">AI bibliotekarza</span>.
        </p>
        
        {/* CTA Buttons */}
        <div 
          className={`flex flex-col sm:flex-row gap-4 justify-center mb-16 transition-all duration-700 delay-300 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          {isAuthenticated ? (
            <Button
              size="lg"
              className="bg-book-gold hover:bg-book-gold-hover text-white px-8 py-6 text-lg rounded-full shadow-lg shadow-book-gold/25 transition-all hover:shadow-xl hover:shadow-book-gold/30"
              onClick={scrollToBooks}
            >
              Przeglądaj książki
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          ) : (
            <>
              <Button
                size="lg"
                className="bg-book-gold hover:bg-book-gold-hover text-white px-8 py-6 text-lg rounded-full shadow-lg shadow-book-gold/25 transition-all hover:shadow-xl hover:shadow-book-gold/30"
              >
                Rozpocznij przygodę
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-2 border-book-brown text-book-brown hover:bg-book-brown hover:text-white px-8 py-6 text-lg rounded-full transition-all"
                onClick={scrollToBooks}
              >
                <BookOpen className="w-5 h-5 mr-2" />
                Przeglądaj książki
              </Button>
            </>
          )}
        </div>
        
        {/* Stats */}
        <div 
          className={`flex flex-wrap justify-center gap-4 transition-all duration-700 delay-500 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <StatCounter value="1,234" label="Książek" icon={Library} />
          <StatCounter value="567" label="Czytelników" icon={Users} />
          <StatCounter value="89" label="Wypożyczeń" icon={BookOpen} />
        </div>
      </div>
      
      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-warm-beige to-transparent" />
    </section>
  );
}
