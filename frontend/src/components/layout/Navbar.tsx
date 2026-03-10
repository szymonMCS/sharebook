import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { BookOpen, Menu, X, User, LogOut, Library, Settings, Sparkles, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAuth } from '@/components/auth/AuthContext';

const navLinks: { label: string; href: string; scrollTo?: string }[] = [
  { label: 'Strona główna', href: '/' },
  { label: 'Książki', href: '/browse' },
  { label: 'Jak to działa', href: '/how-it-works' },
  { label: 'O nas', href: '/about' },
];

interface NavbarProps {
  className?: string;
}

export function Navbar({ className = '' }: NavbarProps) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const isHomePage = location.pathname === '/';

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (sectionId: string) => {
    if (!isHomePage) return;
    const element = document.getElementById(sectionId);
    element?.scrollIntoView({ behavior: 'smooth' });
    setIsMobileMenuOpen(false);
  };

  const handleLogout = async () => {
    await logout();
    setIsMobileMenuOpen(false);
    navigate('/');
  };

  return (
    <>
      <nav
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled
            ? 'bg-white/90 backdrop-blur-md shadow-sm border-b border-stone-200/50'
            : 'bg-transparent'
        } ${className}`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 lg:h-20">
            {/* Logo */}
            <Link 
              to="/" 
              className="flex items-center gap-2 group"
            >
              <div className="w-10 h-10 rounded-lg bg-book-gold flex items-center justify-center group-hover:scale-110 transition-transform">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <span className="font-serif text-xl font-bold text-book-brown">
                ShareBook
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center gap-8">
              {navLinks.map((link) => (
                <Link
                  key={link.label}
                  to={link.href}
                  onClick={(e) => {
                    if (link.scrollTo && isHomePage) {
                      e.preventDefault();
                      scrollToSection(link.scrollTo);
                    }
                  }}
                  className="text-book-gray hover:text-book-brown font-medium transition-colors relative group"
                >
                  {link.label}
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-book-gold transition-all group-hover:w-full" />
                </Link>
              ))}
            </div>

            {/* Desktop Actions */}
            <div className="hidden lg:flex items-center gap-4">
              {isAuthenticated ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button className="flex items-center gap-3 px-4 py-2 rounded-full bg-stone-100 hover:bg-stone-200 transition-colors">
                      <div className="w-8 h-8 rounded-full bg-book-gold/20 flex items-center justify-center">
                        <User className="w-4 h-4 text-book-gold" />
                      </div>
                      <span className="font-medium text-book-brown">
                        {user?.first_name || user?.email}
                      </span>
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuItem asChild>
                    <Link to="/reader" className="cursor-pointer flex items-center">
                      <Library className="w-4 h-4 mr-2" />
                      Panel Czytelnika
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/ai-librarian" className="cursor-pointer flex items-center">
                      <Sparkles className="w-4 h-4 mr-2" />
                      AI Bibliotekarz
                    </Link>
                  </DropdownMenuItem>
                  {user?.role === 'admin' && (
                    <DropdownMenuItem asChild>
                      <Link to="/admin" className="cursor-pointer flex items-center">
                        <Shield className="w-4 h-4 mr-2" />
                        Panel Admina
                      </Link>
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to="/profile" className="cursor-pointer flex items-center">
                      <Settings className="w-4 h-4 mr-2" />
                      Profil i ustawienia
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-red-600 focus:text-red-600">
                    <LogOut className="w-4 h-4 mr-2" />
                    Wyloguj się
                  </DropdownMenuItem>
                </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <>
                  <Button 
                    variant="ghost" 
                    asChild
                    className="text-book-brown hover:text-book-gold hover:bg-book-gold/10"
                  >
                    <Link to="/login">Zaloguj się</Link>
                  </Button>
                  <Button asChild className="bg-book-gold hover:bg-book-gold-hover text-white rounded-full px-6">
                    <Link to="/register">Dołącz teraz</Link>
                  </Button>
                </>
              )}
            </div>

            {/* Mobile Menu Button */}
            <button
              className="lg:hidden p-2 rounded-lg hover:bg-stone-100 transition-colors"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? (
                <X className="w-6 h-6 text-book-brown" />
              ) : (
                <Menu className="w-6 h-6 text-book-brown" />
              )}
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Menu */}
      <div
        className={`fixed inset-0 z-40 lg:hidden transition-all duration-300 ${
          isMobileMenuOpen
            ? 'opacity-100 pointer-events-auto'
            : 'opacity-0 pointer-events-none'
        }`}
      >
        {/* Backdrop */}
        <div 
          className="absolute inset-0 bg-black/20 backdrop-blur-sm"
          onClick={() => setIsMobileMenuOpen(false)}
        />
        
        {/* Menu Panel */}
        <div
          className={`absolute top-16 left-4 right-4 bg-white rounded-2xl shadow-xl border border-stone-200 overflow-hidden transition-all duration-300 ${
            isMobileMenuOpen
              ? 'translate-y-0 opacity-100'
              : '-translate-y-4 opacity-0'
          }`}
        >
          <div className="p-4">
            {/* Mobile Nav Links */}
            <div className="space-y-1">
              {navLinks.map((link) => (
                <Link
                  key={link.label}
                  to={link.href}
                  onClick={(e) => {
                    if (link.scrollTo && isHomePage) {
                      e.preventDefault();
                      scrollToSection(link.scrollTo);
                    }
                    setIsMobileMenuOpen(false);
                  }}
                  className="block px-4 py-3 rounded-xl text-book-brown hover:bg-stone-100 font-medium transition-colors"
                >
                  {link.label}
                </Link>
              ))}
            </div>

            {/* Mobile Actions */}
            <div className="mt-4 pt-4 border-t border-stone-200">
              {isAuthenticated ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-3 px-4 py-3">
                    <div className="w-10 h-10 rounded-full bg-book-gold/20 flex items-center justify-center">
                      <User className="w-5 h-5 text-book-gold" />
                    </div>
                    <div>
                      <p className="font-medium text-book-brown">{user?.first_name || 'User'}</p>
                      <p className="text-sm text-book-gray">{user?.email}</p>
                    </div>
                  </div>
                  
                  {/* Mobile: Panel Czytelnika */}
                  <Link 
                    to="/reader" 
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-3 rounded-xl text-book-brown hover:bg-stone-100 font-medium transition-colors"
                  >
                    <Library className="w-5 h-5 text-book-gold" />
                    Panel Czytelnika
                  </Link>
                  
                  {/* Mobile: AI Bibliotekarz */}
                  <Link 
                    to="/ai-librarian" 
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-3 rounded-xl text-book-brown hover:bg-stone-100 font-medium transition-colors"
                  >
                    <Sparkles className="w-5 h-5 text-book-gold" />
                    AI Bibliotekarz
                  </Link>
                  
                  {/* Mobile: Panel Admina (tylko dla admina) */}
                  {user?.role === 'admin' && (
                    <Link 
                      to="/admin" 
                      onClick={() => setIsMobileMenuOpen(false)}
                      className="flex items-center gap-3 px-4 py-3 rounded-xl text-book-brown hover:bg-stone-100 font-medium transition-colors"
                    >
                      <Shield className="w-5 h-5 text-book-gold" />
                      Panel Admina
                    </Link>
                  )}
                  
                  {/* Mobile: Profil */}
                  <Link 
                    to="/profile" 
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-3 rounded-xl text-book-brown hover:bg-stone-100 font-medium transition-colors"
                  >
                    <Settings className="w-5 h-5 text-book-gold" />
                    Profil
                  </Link>
                  
                  <div className="pt-2 border-t border-stone-200 mt-2">
                    <Button 
                      variant="outline" 
                      className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
                      onClick={handleLogout}
                    >
                      <LogOut className="w-4 h-4 mr-2" />
                      Wyloguj się
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <Button variant="outline" asChild className="w-full">
                    <Link to="/login" onClick={() => setIsMobileMenuOpen(false)}>Zaloguj się</Link>
                  </Button>
                  <Button asChild className="w-full bg-book-gold hover:bg-book-gold-hover text-white">
                    <Link to="/register" onClick={() => setIsMobileMenuOpen(false)}>Dołącz teraz</Link>
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
