import { BookOpen, Heart, Github } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-book-brown text-white">
      {/* Main Footer */}
      <div className="section-padding py-12">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            {/* Brand */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-book-gold flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <span className="font-serif text-xl font-bold">ShareBook</span>
            </div>

            {/* Links */}
            <div className="flex items-center gap-6">
              <a 
                href="#privacy" 
                className="text-white/60 hover:text-book-gold transition-colors text-sm"
              >
                Polityka prywatności
              </a>
              <a 
                href="#terms" 
                className="text-white/60 hover:text-book-gold transition-colors text-sm"
              >
                Regulamin
              </a>
              <a 
                href="https://github.com/szymonMCS/sharebook" 
                target="_blank"
                rel="noopener noreferrer"
                className="text-white/60 hover:text-book-gold transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-white/10">
        <div className="section-padding py-4">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-2">
            <p className="text-white/50 text-sm">
              © 2024 ShareBook. Wszystkie prawa zastrzeżone.
            </p>
            <p className="text-white/50 text-sm flex items-center gap-1">
              Zrobione z <Heart className="w-4 h-4 text-red-400 fill-red-400" /> dla miłośników książek
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
