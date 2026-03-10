import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookPlus, Search, HandHeart, MessageCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '@/components/auth/AuthContext';

interface Step {
  icon: typeof BookPlus;
  title: string;
  description: string;
  color: string;
}

const steps: Step[] = [
  {
    icon: BookPlus,
    title: 'Dodaj swoje książki',
    description: 'Stwórz wirtualną biblioteczkę ze swoimi książkami. Dodawaj tytuły ręcznie lub importuj z API.',
    color: 'bg-blue-100 text-blue-600',
  },
  {
    icon: Search,
    title: 'Przeglądaj kolekcje',
    description: 'Odkrywaj książki innych użytkowników. Filtruj po gatunkach, autorach i dostępności.',
    color: 'bg-green-100 text-green-600',
  },
  {
    icon: HandHeart,
    title: 'Wypożyczaj i dziel się',
    description: 'Wypożyczaj książki od znajomych i pożyczaj swoje. Śledź terminy zwrotów.',
    color: 'bg-amber-100 text-amber-600',
  },
  {
    icon: MessageCircle,
    title: 'AI Bibliotekarz',
    description: 'Pytaj naszego AI o rekomendacje. Opisz nastrój lub temat, a my znajdziemy idealną książkę.',
    color: 'bg-purple-100 text-purple-600',
  },
];

function StepCard({ step, index, isVisible }: { step: Step; index: number; isVisible: boolean }) {
  const Icon = step.icon;
  
  return (
    <div 
      className={`relative transition-all duration-700 ${
        isVisible 
          ? 'opacity-100 translate-y-0' 
          : 'opacity-0 translate-y-12'
      }`}
      style={{ transitionDelay: `${index * 150}ms` }}
    >
      {/* Step number */}
      <div className="absolute -top-4 -left-4 w-10 h-10 rounded-full bg-book-gold text-white flex items-center justify-center font-serif font-bold text-lg z-10">
        {index + 1}
      </div>
      
      <div className="bg-white rounded-2xl p-8 shadow-sm border border-stone-200/60 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 h-full">
        {/* Icon */}
        <div className={`w-16 h-16 rounded-xl ${step.color} flex items-center justify-center mb-6`}>
          <Icon className="w-8 h-8" />
        </div>
        
        {/* Content */}
        <h3 className="font-serif text-xl font-semibold text-book-brown mb-3">
          {step.title}
        </h3>
        <p className="text-book-gray leading-relaxed">
          {step.description}
        </p>
      </div>
      
      {/* Connector arrow (hidden on mobile and last item) */}
      {index < steps.length - 1 && (
        <div className="hidden lg:block absolute top-1/2 -right-6 transform -translate-y-1/2 z-10">
          <ArrowRight className="w-6 h-6 text-book-gold/40" />
        </div>
      )}
    </div>
  );
}

export function HowItWorksSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const [isVisible, setIsVisible] = useState(false);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.2 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <section ref={sectionRef} className="py-20 section-padding bg-white/50">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 bg-book-gold/10 text-book-gold text-sm font-medium rounded-full mb-4">
            Jak to działa
          </span>
          <h2 className="font-serif text-4xl md:text-5xl font-bold text-book-brown mb-4">
            Zacznij w 4 prostych krokach
          </h2>
          <p className="text-book-gray max-w-2xl mx-auto">
            ShareBook to prosty sposób na dzielenie się książkami z przyjaciółmi. 
            Oto jak zacząć swoją przygodę.
          </p>
        </div>

        {/* Steps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <StepCard 
              key={step.title} 
              step={step} 
              index={index} 
              isVisible={isVisible}
            />
          ))}
        </div>

        {/* CTA - only show for non-authenticated users */}
        {!isAuthenticated && (
          <div 
            className={`text-center mt-16 transition-all duration-700 delay-700 ${
              isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
            }`}
          >
            <button 
              onClick={() => navigate('/register')}
              className="btn-primary inline-flex items-center"
            >
              Dołącz do społeczności
              <ArrowRight className="w-5 h-5 ml-2" />
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
