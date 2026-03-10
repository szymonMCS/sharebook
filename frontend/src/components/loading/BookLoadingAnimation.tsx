import { useEffect, useRef } from 'react';

interface BookLoadingAnimationProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function BookLoadingAnimation({ 
  message = 'Przywoływanie opowieści...', 
  size = 'md' 
}: BookLoadingAnimationProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Generowanie magicznych cząsteczek
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const createParticle = () => {
      const particle = document.createElement('div');
      particle.className = 'absolute rounded-full pointer-events-none';
      
      const size_px = Math.random() * 4 + 1;
      const x = Math.random() * 120 - 60;
      const y = -20;
      
      particle.style.width = `${size_px}px`;
      particle.style.height = `${size_px}px`;
      particle.style.left = `calc(50% + ${x}px)`;
      particle.style.top = `calc(50% + ${y}px)`;
      particle.style.background = '#d4af37';
      particle.style.opacity = '1';
      
      const duration = Math.random() * 2 + 1;
      particle.style.animation = `sparkle ${duration}s linear forwards`;
      
      container.appendChild(particle);
      
      setTimeout(() => {
        particle.remove();
      }, duration * 1000);
    };

    const interval = setInterval(createParticle, 100);
    return () => clearInterval(interval);
  }, []);

  const sizeClasses = {
    sm: 'scale-75',
    md: 'scale-100',
    lg: 'scale-150'
  };

  return (
    <div 
      ref={containerRef}
      className="relative flex flex-col items-center justify-center"
      style={{ perspective: '1000px' }}
    >
      <style>{`
        @keyframes fly {
          0%, 100% { transform: rotateX(25deg) translateY(0) rotateZ(-2deg); }
          50% { transform: rotateX(35deg) translateY(-30px) rotateZ(2deg); }
        }
        @keyframes flap-left {
          0% { transform: rotateY(0deg); }
          100% { transform: rotateY(75deg); }
        }
        @keyframes flap-right {
          0% { transform: rotateY(0deg); }
          100% { transform: rotateY(-75deg); }
        }
        @keyframes shadow-scale {
          0%, 100% { transform: scale(1); opacity: 0.4; }
          50% { transform: scale(1.4); opacity: 0.2; }
        }
        @keyframes sparkle {
          0% { transform: translateY(0) scale(1); opacity: 1; }
          100% { transform: translateY(100px) scale(0); opacity: 0; }
        }
      `}</style>
      
      <div className={`${sizeClasses[size]} transition-transform`}>
        {/* Książka */}
        <div 
          className="relative w-[120px] h-[80px]"
          style={{ 
            transformStyle: 'preserve-3d',
            animation: 'fly 3s ease-in-out infinite'
          }}
        >
          {/* Grzbiet */}
          <div 
            className="absolute left-1/2 top-0 w-[10px] h-full rounded-sm"
            style={{ 
              background: '#3a1f11',
              transform: 'translateX(-50%) translateZ(2px)',
              boxShadow: '0 0 15px rgba(0,0,0,0.5)'
            }}
          />
          
          {/* Lewe strony */}
          {[0, 1, 2].map((i) => (
            <div
              key={`left-${i}`}
              className="absolute top-0 right-1/2 w-[60px] h-[80px] border border-black/10"
              style={{
                background: '#f4ecd8',
                borderRadius: '5px 0 0 5px',
                transformOrigin: 'right center',
                animation: `flap-left 0.8s ease-in-out infinite alternate`,
                animationDelay: `${i * 0.1}s`,
                opacity: 1 - i * 0.1,
                boxShadow: 'inset 3px 0 10px rgba(0,0,0,0.1)'
              }}
            />
          ))}
          
          {/* Prawe strony */}
          {[0, 1, 2].map((i) => (
            <div
              key={`right-${i}`}
              className="absolute top-0 left-1/2 w-[60px] h-[80px] border border-black/10"
              style={{
                background: '#f4ecd8',
                borderRadius: '0 5px 5px 0',
                transformOrigin: 'left center',
                animation: `flap-right 0.8s ease-in-out infinite alternate`,
                animationDelay: `${i * 0.1}s`,
                opacity: 1 - i * 0.1,
                boxShadow: 'inset 3px 0 10px rgba(0,0,0,0.1)'
              }}
            />
          ))}
        </div>
        
        {/* Cień */}
        <div 
          className="absolute -bottom-12 left-1/2 -translate-x-1/2 w-[100px] h-[20px] rounded-full"
          style={{
            background: 'rgba(0,0,0,0.4)',
            filter: 'blur(8px)',
            animation: 'shadow-scale 3s ease-in-out infinite'
          }}
        />
      </div>
      
      {/* Tekst */}
      <p 
        className="mt-16 text-book-gold text-lg tracking-widest uppercase italic text-center"
        style={{ textShadow: '0 0 10px rgba(212, 175, 55, 0.6)' }}
      >
        {message}
      </p>
    </div>
  );
}
