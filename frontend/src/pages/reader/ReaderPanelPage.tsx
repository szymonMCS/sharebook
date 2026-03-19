import { useEffect, useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { 
  BookOpen, 
  BookMarked, 
  Inbox, 
  Library,
  Menu,
  Share2,
  LogOut,
  Shield
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Navbar } from '@/components/layout/Navbar';
import { FloatingBooks, GradientOrbs } from '@/components/layout/FloatingBooks';
import { useAuth } from '@/components/auth/AuthContext';
import { useUserBooksStore } from '@/store/userBooksStore';
import { Sheet, SheetContent, SheetTrigger, SheetTitle } from '@/components/ui/sheet';
import { Badge } from '@/components/ui/badge';

interface NavItem {
  id: string;
  label: string;
  href: string;
  icon: React.ElementType;
  badge?: number;
}

const navItems: NavItem[] = [
  { id: 'my-books', label: 'Moje książki', href: '/reader/my-books', icon: Library },
  { id: 'borrowed', label: 'Wypożyczone od innych', href: '/reader/borrowed', icon: BookOpen },
  { id: 'lent', label: 'Wypożyczone innym', href: '/reader/lent', icon: Share2 },
  { id: 'requests', label: 'Prośby', href: '/reader/requests', icon: Inbox },
];

function Sidebar({ className }: { className?: string }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, isAdmin } = useAuth();
  const { incomingRequests, outgoingRequests } = useUserBooksStore();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };
  
  // Guard against undefined values (happens after registration before data is loaded)
  const safeIncoming = incomingRequests || [];
  const safeOutgoing = outgoingRequests || [];
  
  const pendingIncoming = safeIncoming.filter(r => r.status === 'pending').length;
  const pendingOutgoing = safeOutgoing.filter(r => r.status === 'pending').length;
  const totalRequests = pendingIncoming + pendingOutgoing;

  return (
    <div className={cn("flex flex-col h-full", className)}>
      {/* Header */}
      <div className="p-6 border-b border-stone-200/60">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-book-gold/10 flex items-center justify-center">
            <BookMarked className="w-5 h-5 text-book-gold" />
          </div>
          <div>
            <h2 className="font-serif font-semibold text-book-brown">Panel Czytelnika</h2>
            <p className="text-xs text-book-muted">Zarządzaj swoimi książkami</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname.startsWith(item.href);
          const Icon = item.icon;
          const badgeCount = item.id === 'requests' && totalRequests > 0 
            ? totalRequests 
            : undefined;

          return (
            <NavLink
              key={item.id}
              to={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group",
                isActive 
                  ? "bg-book-gold text-white shadow-md" 
                  : "text-book-gray hover:bg-stone-100 hover:text-book-brown"
              )}
            >
              <Icon className={cn(
                "w-5 h-5 transition-transform",
                !isActive && "group-hover:scale-110"
              )} />
              <span className="font-medium flex-1">{item.label}</span>
              {badgeCount !== undefined && (
                <Badge 
                  variant={isActive ? "secondary" : "default"}
                  className={cn(
                    "text-xs",
                    isActive 
                      ? "bg-white/20 text-white hover:bg-white/30" 
                      : "bg-book-gold text-white"
                  )}
                >
                  {badgeCount}
                </Badge>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-stone-200/60 space-y-2">
        {isAdmin && (
          <NavLink
            to="/admin"
            className={cn(
              "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200",
              location.pathname.startsWith('/admin')
                ? "bg-red-100 text-red-700"
                : "text-book-gray hover:bg-stone-100 hover:text-book-brown"
            )}
          >
            <Shield className="w-5 h-5" />
            <span className="font-medium flex-1">Panel Admina</span>
          </NavLink>
        )}
        <Button 
          variant="ghost" 
          className="w-full justify-start gap-2 text-book-gray hover:text-red-600"
          onClick={handleLogout}
        >
          <LogOut className="w-4 h-4" />
          Wyloguj
        </Button>
        <div className="bg-gradient-to-br from-book-gold/5 to-book-brown/5 rounded-xl p-4">
          <p className="text-xs text-book-muted text-center">
            Udostępniaj książki i odkrywaj nowe historie
          </p>
        </div>
      </div>
    </div>
  );
}

function MobileNav() {
  const [open, setOpen] = useState(false);

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button 
          variant="ghost" 
          size="icon" 
          className="lg:hidden"
        >
          <Menu className="w-5 h-5" />
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-[280px] p-0 bg-warm-beige">
        <SheetTitle className="sr-only">Nawigacja panelu czytelnika</SheetTitle>
        <Sidebar />
      </SheetContent>
    </Sheet>
  );
}

export function ReaderPanelPage() {
  const { fetchMyBooks, fetchBorrowed, fetchLent, fetchRequests, clearError } = useUserBooksStore();

  useEffect(() => {
    // Load all data on mount
    Promise.all([
      fetchMyBooks(),
      fetchBorrowed(),
      fetchLent(),
      fetchRequests()
    ]);

    return () => {
      clearError();
    };
  }, [fetchMyBooks, fetchBorrowed, fetchLent, fetchRequests, clearError]);

  return (
    <div className="min-h-screen bg-warm-beige relative">
      <FloatingBooks />
      <GradientOrbs />
      <Navbar />

      <main className="relative z-10 pt-16 lg:pt-20">
        <div className="flex min-h-[calc(100vh-80px)]">
          {/* Desktop Sidebar */}
          <aside className="hidden lg:block w-72 bg-white/80 backdrop-blur-md border-r border-stone-200/60 sticky top-20 h-[calc(100vh-80px)]">
            <Sidebar />
          </aside>

          {/* Main Content */}
          <div className="flex-1">
            {/* Mobile Header */}
            <div className="lg:hidden px-4 py-4 border-b border-stone-200/60 bg-white/80 backdrop-blur-md sticky top-16 z-20">
              <div className="flex items-center gap-3">
                <MobileNav />
                <div className="flex items-center gap-2">
                  <BookMarked className="w-5 h-5 text-book-gold" />
                  <span className="font-serif font-semibold text-book-brown">Panel Czytelnika</span>
                </div>
              </div>
            </div>

            {/* Content Area */}
            <div className="p-4 lg:p-8 max-w-6xl mx-auto">
              <Outlet />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
