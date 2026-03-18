import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authApi, type User } from '@/api/auth';
import { AUTH_UNAUTHORIZED_EVENT } from '@/api/client';

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
const hasClerk = !!clerkPubKey && clerkPubKey.startsWith('pk_');

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; first_name: string; last_name: string; location?: string; phone?: string }) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Local JWT Provider (using cookie-based auth)
function LocalAuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  // Listen for 401 unauthorized events
  useEffect(() => {
    const handleUnauthorized = () => {
      setUser(null);
      navigate('/login', { replace: true });
    };

    window.addEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized);
    return () => window.removeEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized);
  }, [navigate, location.pathname]);

  // Check auth on mount by calling /users/me
  useEffect(() => {
    const checkAuth = async () => {
      try {
        console.log('[Auth] Checking auth via /users/me');
        const res = await authApi.me();
        console.log('[Auth] Me response:', res.success, res.data?.user?.email);
        if (res.success && res.data?.user) {
          setUser(res.data.user);
        } else {
          setUser(null);
        }
      } catch (err) {
        console.log('[Auth] API error:', err instanceof Error ? err.message : err);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  useEffect(() => {
    if (!loading && user && location.pathname === '/login') {
      navigate('/reader', { replace: true });
    }
  }, [loading, user, location.pathname, navigate]);

  const login = async (email: string, password: string) => {
    const res = await authApi.login(email, password);
    if (!res.success || !res.data?.user) {
      throw new Error(res.error || 'Nieprawidłowy email lub hasło');
    }
    setUser(res.data.user);
    navigate('/reader', { replace: true });
  };

  const register = async (data: { email: string; password: string; first_name: string; last_name: string; location?: string; phone?: string }) => {
    const res = await authApi.register(data);
    if (!res.success || !res.data?.user) {
      throw new Error(res.error || 'Rejestracja nie powiodła się');
    }
    setUser(res.data.user);
    navigate('/reader', { replace: true });
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (e) {
      console.error('Logout error:', e);
    } finally {
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isAdmin: user?.role === 'admin',
      loading,
      login,
      register,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

// Clerk Provider wrapper - loaded dynamically
function ClerkAuthProvider({ children }: { children: ReactNode }) {
  const [clerkLoaded, setClerkLoaded] = useState(false);
  const [clerkModule, setClerkModule] = useState<any>(null);

  useEffect(() => {
    const loadClerk = async () => {
      try {
        const mod = await import('@clerk/clerk-react');
        setClerkModule(mod);
      } catch {
        // Fall back to local auth on error
      } finally {
        setClerkLoaded(true);
      }
    };
    loadClerk();
  }, []);

  if (!clerkLoaded || !clerkModule) {
    return <LocalAuthProvider>{children}</LocalAuthProvider>;
  }

  const { ClerkProvider, useUser, useAuth: useClerkAuth, useSession } = clerkModule;

  return (
    <ClerkProvider publishableKey={clerkPubKey!}>
      <ClerkAuthContent useUser={useUser} useClerkAuth={useClerkAuth} useSession={useSession}>
        {children}
      </ClerkAuthContent>
    </ClerkProvider>
  );
}

function ClerkAuthContent({ 
  children, 
  useUser, 
  useClerkAuth, 
  useSession 
}: { 
  children: ReactNode;
  useUser: any;
  useClerkAuth: any;
  useSession: any;
}) {
  const { user: clerkUser, isLoaded } = useUser();
  const { signOut } = useClerkAuth();
  const { session, isSignedIn } = useSession();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Listen for 401 unauthorized events
  useEffect(() => {
    const handleUnauthorized = async () => {
      await signOut();
      setUser(null);
      // Only redirect to login if on protected page
      const publicPaths = ['/', '/browse', '/books', '/about', '/how-it-works', '/login', '/register'];
      const isPublicPage = publicPaths.some(path => location.pathname === path || location.pathname.startsWith('/books/'));
      if (!isPublicPage) {
        navigate('/login', { replace: true });
      }
    };

    window.addEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized);
    return () => window.removeEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized);
  }, [navigate, signOut, location.pathname]);

  useEffect(() => {
    if (!isLoaded) return;

    if (isSignedIn && clerkUser) {
      const primaryEmail = clerkUser.primaryEmailAddress?.emailAddress || '';
      
      setUser({
        id: clerkUser.id,
        email: primaryEmail,
        first_name: clerkUser.firstName || '',
        last_name: clerkUser.lastName || '',
        role: 'reader',
        created_at: new Date().toISOString(),
      });
      
      setLoading(false);
    } else {
      setUser(null);
      setLoading(false);
    }
  }, [clerkUser, isLoaded, isSignedIn]);

  const login = async () => {
    throw new Error('Use Clerk SignIn component for authentication');
  };

  const register = async () => {
    throw new Error('Use Clerk SignUp component for registration');
  };

  const logout = async () => {
    await signOut();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isAdmin: user?.role === 'admin',
      loading,
      login,
      register,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function AuthProvider({ children }: { children: ReactNode }) {
  if (hasClerk) {
    return <ClerkAuthProvider>{children}</ClerkAuthProvider>;
  }
  
  return <LocalAuthProvider>{children}</LocalAuthProvider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth musi być użyte wewnątrz AuthProvider');
  }
  return context;
}
