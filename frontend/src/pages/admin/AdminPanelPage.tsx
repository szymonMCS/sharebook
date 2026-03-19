import { useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  BookOpen,
  Library,
  Shield,
  Menu,
  LogOut,
  Home,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { FloatingBooks, GradientOrbs } from '@/components/layout/FloatingBooks';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { useAuth } from '@/components/auth/AuthContext';

interface NavItem {
  id: string;
  label: string;
  href: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', href: '/admin/dashboard', icon: LayoutDashboard },
  { id: 'users', label: 'Użytkownicy', href: '/admin/users', icon: Users },
  { id: 'books', label: 'Książki', href: '/admin/books', icon: BookOpen },
  { id: 'user-books', label: 'Książki użytkowników', href: '/admin/user-books', icon: Library },
];

function Sidebar({ className }: { className?: string }) {
  const location = useLocation();
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className={cn("flex flex-col h-full", className)}>
      {/* Header */}
      <div className="p-6 border-b border-stone-200/60">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center">
            <Shield className="w-5 h-5 text-red-600" />
          </div>
          <div>
            <h2 className="font-serif font-semibold text-book-brown">Panel Admina</h2>
            <p className="text-xs text-book-muted">Zarządzanie platformą</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname.startsWith(item.href);
          const Icon = item.icon;

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
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-stone-200/60 space-y-2">
        <NavLink
          to="/dashboard"
          className={cn(
            "flex items-center gap-2 px-3 py-2 rounded-lg transition-all",
            "text-book-gray hover:bg-stone-100 hover:text-book-brown"
          )}
        >
          <Home className="w-4 h-4" />
          <span className="text-sm font-medium">Powrót do aplikacji</span>
        </NavLink>
        <Button 
          variant="ghost" 
          className="w-full justify-start gap-2 text-book-gray hover:text-red-600"
          onClick={handleLogout}
        >
          <LogOut className="w-4 h-4" />
          Wyloguj
        </Button>
        <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-xl p-4">
          <p className="text-xs text-book-muted text-center">
            Panel administracyjny ShareBook
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
        <Sidebar />
      </SheetContent>
    </Sheet>
  );
}

export function AdminPanelPage() {
  return (
    <div className="min-h-screen bg-warm-beige relative">
      <FloatingBooks />
      <GradientOrbs />

      <main className="relative z-10 pt-4 lg:pt-8">
        <div className="flex min-h-[calc(100vh-80px)]">
          {/* Desktop Sidebar */}
          <aside className="hidden lg:block w-72 bg-white/80 backdrop-blur-md border-r border-stone-200/60 sticky top-4 h-[calc(100vh-32px)]">
            <Sidebar />
          </aside>

          {/* Main Content */}
          <div className="flex-1">
            {/* Mobile Header */}
            <div className="lg:hidden px-4 py-4 border-b border-stone-200/60 bg-white/80 backdrop-blur-md sticky top-0 z-20">
              <div className="flex items-center gap-3">
                <MobileNav />
                <div className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-red-600" />
                  <span className="font-serif font-semibold text-book-brown">Panel Admina</span>
                </div>
              </div>
            </div>

            {/* Content Area */}
            <div className="p-4 lg:p-8 max-w-7xl mx-auto">
              <Outlet />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
