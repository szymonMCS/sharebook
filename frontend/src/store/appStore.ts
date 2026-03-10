import { useState, useCallback } from 'react';
import type { Book, User, ChatMessage, BookStatus } from '@/types';
import { mockBooks, mockLoans, mockChatMessages, mockUsers } from '@/lib/data';

// Simple hook-based store for auth
export function useAuthStore() {
  const [currentUser, setCurrentUser] = useState<User | null>(mockUsers[0]);
  const [isAuthenticated, setIsAuthenticated] = useState(true);

  const login = useCallback((user: User) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
  }, []);

  const logout = useCallback(() => {
    setCurrentUser(null);
    setIsAuthenticated(false);
  }, []);

  return {
    currentUser,
    isAuthenticated,
    login,
    logout,
  };
}

// Books store
export function useBooksStore() {
  const [books, setBooks] = useState<Book[]>(mockBooks);
  const [filters, setFilters] = useState<{ search?: string; status: BookStatus | 'all'; genre?: string }>({ status: 'all' });

  const addBook = useCallback((book: Book) => {
    setBooks((prev) => [book, ...prev]);
  }, []);

  const updateBook = useCallback((id: string, updates: Partial<Book>) => {
    setBooks((prev) =>
      prev.map((book) =>
        book.id === id
          ? { ...book, ...updates, updated_at: new Date().toISOString() }
          : book
      )
    );
  }, []);

  const deleteBook = useCallback((id: string) => {
    setBooks((prev) => prev.filter((book) => book.id !== id));
  }, []);

  const getFilteredBooks = useCallback(() => {
    return books.filter((book) => {
      const matchesSearch = filters.search
        ? book.title.toLowerCase().includes(filters.search.toLowerCase()) ||
          (book.author || '').toLowerCase().includes(filters.search.toLowerCase())
        : true;

      const matchesStatus =
        filters.status && filters.status !== 'all'
          ? book.status === filters.status
          : true;

      const matchesGenre =
        filters.genre && filters.genre !== 'Wszystkie'
          ? book.genre === filters.genre
          : true;

      return matchesSearch && matchesStatus && matchesGenre;
    });
  }, [books, filters]);

  const getBookById = useCallback(
    (id: string) => books.find((book) => book.id === id),
    [books]
  );

  const getUserBooks = useCallback(
    (userId: string) => books.filter((book) => book.owner_id === userId),
    [books]
  );

  return {
    books,
    filters,
    setBooks,
    addBook,
    updateBook,
    deleteBook,
    setFilters,
    getFilteredBooks,
    getBookById,
    getUserBooks,
  };
}

// UI store
export function useUIStore() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [activeModal, setActiveModal] = useState<string | null>(null);
  const [toast, setToast] = useState<{
    message: string;
    type: 'success' | 'error' | 'info';
  } | null>(null);

  const toggleSidebar = useCallback(() => {
    setIsSidebarOpen((prev) => !prev);
  }, []);

  const showToast = useCallback(
    (message: string, type: 'success' | 'error' | 'info') => {
      setToast({ message, type });
    },
    []
  );

  const clearToast = useCallback(() => {
    setToast(null);
  }, []);

  return {
    isSidebarOpen,
    isLoading,
    activeModal,
    toast,
    toggleSidebar,
    setSidebarOpen: setIsSidebarOpen,
    setLoading: setIsLoading,
    setActiveModal,
    showToast,
    clearToast,
  };
}

// Chat store
export function useChatStore() {
  const [messages, setMessages] = useState<ChatMessage[]>(mockChatMessages);
  const [isTyping, setIsTyping] = useState(false);

  const addMessage = useCallback((message: ChatMessage) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  const setTyping = useCallback((typing: boolean) => {
    setIsTyping(typing);
  }, []);

  const clearChat = useCallback(() => {
    setMessages(mockChatMessages);
  }, []);

  return {
    messages,
    isTyping,
    addMessage,
    setTyping,
    clearChat,
  };
}

// Loans store
interface Loan {
  id: string;
  book_id: string;
  owner_id: string;
  borrower_id: string;
  status: 'active' | 'returned' | 'overdue';
  borrowed_at: string;
  due_date: string;
  returned_at?: string;
  created_at: string;
}

export function useLoansStore() {
  const [loans, setLoans] = useState<Loan[]>(mockLoans as Loan[]);

  const addLoan = useCallback((loan: Loan) => {
    setLoans((prev) => [...prev, loan]);
  }, []);

  const updateLoan = useCallback((id: string, updates: Partial<Loan>) => {
    setLoans((prev) =>
      prev.map((loan) => (loan.id === id ? { ...loan, ...updates } : loan))
    );
  }, []);

  const getUserLoans = useCallback(
    (userId: string) =>
      loans.filter(
        (loan) => loan.owner_id === userId || loan.borrower_id === userId
      ),
    [loans]
  );

  const getActiveLoans = useCallback(
    (userId: string) =>
      loans.filter(
        (loan) =>
          (loan.owner_id === userId || loan.borrower_id === userId) &&
          loan.status === 'active'
      ),
    [loans]
  );

  return {
    loans,
    addLoan,
    updateLoan,
    getUserLoans,
    getActiveLoans,
  };
}
