import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from '@/components/layout/Navbar';
import { FloatingBooks, GradientOrbs } from '@/components/layout/FloatingBooks';
import { HeroSection } from '@/components/sections/HeroSection';
import { FeaturedBooksSection } from '@/components/sections/FeaturedBooksSection';
import { HowItWorksSection } from '@/components/sections/HowItWorksSection';
import { Footer } from '@/components/layout/Footer';
import { LoginPage } from '@/pages/auth/LoginPage';
import { RegisterPage } from '@/pages/auth/RegisterPage';
import { AboutPage } from '@/pages/AboutPage';
import { HowItWorksPage } from '@/pages/HowItWorksPage';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { ProtectedAdminRoute } from '@/components/auth/ProtectedAdminRoute';
import { AuthProvider } from '@/components/auth/AuthContext';
import { ErrorBoundary } from '@/components/layout/ErrorBoundary';

// Reader Panel
import { ReaderPanelPage } from '@/pages/reader/ReaderPanelPage';
import { MyBooksSection } from '@/pages/reader/MyBooksSection';
import { BorrowedBooksSection } from '@/pages/reader/BorrowedBooksSection';
import { LentBooksSection } from '@/pages/reader/LentBooksSection';
import { LoanRequestsSection } from '@/pages/reader/LoanRequestsSection';

// Admin Panel
import { AdminPanelPage } from '@/pages/admin/AdminPanelPage';
import { DashboardSection } from '@/pages/admin/DashboardSection';
import { UsersSection } from '@/pages/admin/UsersSection';
import { BooksSection } from '@/pages/admin/BooksSection';

// AI Chat
import { AIChatPage } from '@/pages/ai/AIChatPage';

// Profile
import { ProfilePage } from '@/pages/profile/ProfilePage';

// Browse Books
import { BrowsePage } from '@/pages/browse/BrowsePage';

// Book Details
import { BookDetailPage } from '@/pages/books/BookDetailPage';

function HomePage() {
  return (
    <div className="min-h-screen bg-warm-beige relative">
      <FloatingBooks />
      <GradientOrbs />
      <Navbar />
      <main className="relative z-10">
        <HeroSection />
        <FeaturedBooksSection />
        <HowItWorksSection />
      </main>
      <Footer />
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ErrorBoundary>
          <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/how-it-works" element={<HowItWorksPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Protected routes - Reader Panel */}
          <Route element={<ProtectedRoute />}>
            <Route path="/reader" element={<ReaderPanelPage />}>
              <Route index element={<Navigate to="my-books" replace />} />
              <Route path="my-books" element={<MyBooksSection />} />
              <Route path="borrowed" element={<BorrowedBooksSection />} />
              <Route path="lent" element={<LentBooksSection />} />
              <Route path="requests" element={<LoanRequestsSection />} />
            </Route>
          </Route>

          {/* Admin routes (protected) */}
          <Route element={<ProtectedAdminRoute />}>
            <Route path="/admin" element={<AdminPanelPage />}>
              <Route index element={<Navigate to="dashboard" replace />} />
              <Route path="dashboard" element={<DashboardSection />} />
              <Route path="users" element={<UsersSection />} />
              <Route path="books" element={<BooksSection />} />
            </Route>
          </Route>

          {/* Browse Books (public) */}
          <Route path="/browse" element={<BrowsePage />} />
          <Route path="/books/:id" element={<BookDetailPage />} />

          {/* AI Chat (public) */}
          <Route path="/ai-librarian" element={<AIChatPage />} />

          {/* Profile (protected) */}
          <Route element={<ProtectedRoute />}>
            <Route path="/profile" element={<ProfilePage />} />
          </Route>

          {/* Catch all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        </ErrorBoundary>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
