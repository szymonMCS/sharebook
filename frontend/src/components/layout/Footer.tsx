import { BookOpen, Heart, Github, Twitter, Mail } from 'lucide-react';

const footerLinks = {
  product: [
    { label: 'Funkcje', href: '#features' },
    { label: 'Cennik', href: '#pricing' },
    { label: 'API', href: '#api' },
    { label: 'Integracje', href: '#integrations' },
  ],
  company: [
    { label: 'O nas', href: '#about' },
    { label: 'Blog', href: '#blog' },
    { label: 'Kariera', href: '#careers' },
    { label: 'Kontakt', href: '#contact' },
  ],
  resources: [
    { label: 'Dokumentacja', href: '#docs' },
    { label: 'Pomoc', href: '#help' },
    { label: 'FAQ', href: '#faq' },
    { label: 'Społeczność', href: '#community' },
  ],
  legal: [
    { label: 'Polityka prywatności', href: '#privacy' },
    { label: 'Regulamin', href: '#terms' },
    { label: 'Cookies', href: '#cookies' },
  ],
};

export function Footer() {
  return (
    <footer className="bg-book-brown text-white">
      {/* Main Footer */}
      <div className="section-padding py-16">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-12">
            {/* Brand */}
            <div className="lg:col-span-2">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-book-gold flex items-center justify-center">
                  <BookOpen className="w-6 h-6 text-white" />
                </div>
                <span className="font-serif text-2xl font-bold">ShareBook</span>
              </div>
              <p className="text-white/70 mb-6 max-w-sm leading-relaxed">
                Dziel się książkami z przyjaciółmi. Stwórz swoją wirtualną biblioteczkę 
                i odkrywaj nowe historie razem z nami.
              </p>
              <div className="flex gap-4">
                <a 
                  href="#" 
                  className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center hover:bg-book-gold transition-colors"
                >
                  <Twitter className="w-5 h-5" />
                </a>
                <a 
                  href="#" 
                  className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center hover:bg-book-gold transition-colors"
                >
                  <Github className="w-5 h-5" />
                </a>
                <a 
                  href="#" 
                  className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center hover:bg-book-gold transition-colors"
                >
                  <Mail className="w-5 h-5" />
                </a>
              </div>
            </div>

            {/* Links */}
            <div>
              <h4 className="font-semibold mb-4 text-white/90">Produkt</h4>
              <ul className="space-y-3">
                {footerLinks.product.map((link) => (
                  <li key={link.label}>
                    <a 
                      href={link.href} 
                      className="text-white/60 hover:text-book-gold transition-colors"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4 text-white/90">Firma</h4>
              <ul className="space-y-3">
                {footerLinks.company.map((link) => (
                  <li key={link.label}>
                    <a 
                      href={link.href} 
                      className="text-white/60 hover:text-book-gold transition-colors"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4 text-white/90">Zasoby</h4>
              <ul className="space-y-3">
                {footerLinks.resources.map((link) => (
                  <li key={link.label}>
                    <a 
                      href={link.href} 
                      className="text-white/60 hover:text-book-gold transition-colors"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4 text-white/90">Prawne</h4>
              <ul className="space-y-3">
                {footerLinks.legal.map((link) => (
                  <li key={link.label}>
                    <a 
                      href={link.href} 
                      className="text-white/60 hover:text-book-gold transition-colors"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-white/10">
        <div className="section-padding py-6">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
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
