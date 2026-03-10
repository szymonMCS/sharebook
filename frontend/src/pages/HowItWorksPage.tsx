import { Navbar } from '@/components/layout/Navbar';
import { FloatingBooks, GradientOrbs } from '@/components/layout/FloatingBooks';
import { Footer } from '@/components/layout/Footer';
import { Upload, Search, MessageCircle, BookOpen, Truck, Star } from 'lucide-react';

export function HowItWorksPage() {
  const steps = [
    {
      number: '01',
      icon: Upload,
      title: 'Dodaj swoje książki',
      description: 'Zeskanuj kod ISBN lub wprowadź dane ręcznie. Twoje książki trafią do Twojej wirtualnej biblioteczki.',
    },
    {
      number: '02',
      icon: Search,
      title: 'Przeglądaj oferty',
      description: 'Używaj filtrów lub zaufaj naszemu AI Bibliotekarzowi, który znajdzie książki dopasowane do Twoich gustów.',
    },
    {
      number: '03',
      icon: MessageCircle,
      title: 'Nawiąż kontakt',
      description: 'Znajdź właściciela interesującej Cię książki i napisz do niego. Ustalcie szczegóły wymiany.',
    },
    {
      number: '04',
      icon: Truck,
      title: 'Wymień się',
      description: 'Spotkajcie się osobiście lub wyślijcie książki pocztą. To prostsze niż myślisz!',
    },
    {
      number: '05',
      icon: BookOpen,
      title: 'Czytaj i dziel się',
      description: 'Ciesz się nową lekturą. Gdy skończysz, możesz ją zatrzymać lub przekazać dalej.',
    },
  ];

  const features = [
    {
      icon: Star,
      title: 'Za darmo',
      description: 'Korzystanie z platformy jest całkowicie bezpłatne. Płacisz tylko za przesyłkę, jeśli wybierzesz wysyłkę.',
    },
    {
      icon: BookOpen,
      title: 'Bez limitów',
      description: 'Dodawaj dowolną liczbę książek i wymieniaj się tyle razy, ile chcesz.',
    },
    {
      icon: Search,
      title: 'Spersonalizowane',
      description: 'Nasz AI Bibliotekarz uczy się Twoich preferencji i poleca coraz lepsze książki.',
    },
  ];

  return (
    <div className="min-h-screen bg-warm-beige relative">
      <FloatingBooks />
      <GradientOrbs />
      <Navbar />
      
      <main className="relative z-10 pt-20">
        {/* Hero Section */}
        <section className="py-20 lg:py-32">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="font-serif text-4xl md:text-6xl font-bold text-book-brown mb-6">
              Jak to <span className="text-book-gold">działa?</span>
            </h1>
            <p className="text-xl text-book-gray max-w-3xl mx-auto leading-relaxed">
              Wymiana książek w Sharebook jest prosta i przyjemna. 
              Zobacz, jak w 5 krokach możesz znaleźć swoją nową ulubioną lekturę.
            </p>
          </div>
        </section>

        {/* Steps Section */}
        <section className="py-20 bg-white/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="space-y-16">
              {steps.map((step, index) => (
                <div
                  key={step.number}
                  className={`flex flex-col md:flex-row items-center gap-8 ${
                    index % 2 === 1 ? 'md:flex-row-reverse' : ''
                  }`}
                >
                  <div className="flex-1">
                    <div className="text-8xl font-bold text-book-gold/20 mb-4">
                      {step.number}
                    </div>
                    <div className="w-14 h-14 rounded-xl bg-book-gold/10 flex items-center justify-center mb-6">
                      <step.icon className="w-7 h-7 text-book-gold" />
                    </div>
                    <h3 className="font-serif text-2xl font-bold text-book-brown mb-4">
                      {step.title}
                    </h3>
                    <p className="text-book-gray text-lg leading-relaxed">
                      {step.description}
                    </p>
                  </div>
                  <div className="flex-1">
                    <div className="bg-gradient-to-br from-book-gold/10 to-book-brown/5 rounded-2xl p-12 aspect-video flex items-center justify-center">
                      <step.icon className="w-24 h-24 text-book-gold/40" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="font-serif text-3xl md:text-4xl font-bold text-book-brown mb-4">
                Dlaczego warto?
              </h2>
              <p className="text-book-gray max-w-2xl mx-auto">
                Sharebook to więcej niż platforma - to społeczność miłośników książek.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {features.map((feature) => (
                <div
                  key={feature.title}
                  className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-shadow text-center"
                >
                  <div className="w-16 h-16 rounded-full bg-book-gold/10 flex items-center justify-center mx-auto mb-6">
                    <feature.icon className="w-8 h-8 text-book-gold" />
                  </div>
                  <h3 className="font-serif text-xl font-semibold text-book-brown mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-book-gray leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FAQ Teaser */}
        <section className="py-20 bg-book-brown text-white">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="font-serif text-3xl md:text-4xl font-bold mb-6">
              Masz pytania?
            </h2>
            <p className="text-white/80 mb-8 text-lg">
              Sprawdź naszą sekcję FAQ lub skontaktuj się z nami bezpośrednio.
              Chętnie pomożemy!
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/faq"
                className="inline-block bg-white/10 hover:bg-white/20 text-white px-8 py-4 rounded-full font-medium transition-all"
              >
                Przejdź do FAQ
              </a>
              <a
                href="/contact"
                className="inline-block bg-book-gold hover:bg-book-gold-hover text-white px-8 py-4 rounded-full font-medium transition-all"
              >
                Skontaktuj się
              </a>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
