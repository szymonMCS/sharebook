import { create } from 'zustand';
import { booksApi } from '@/api/books';
import { loansApi } from '@/api/loans';
import type { UserLibraryItem, AddBookRequest, LoanRequest } from '@/types';

interface User {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
}

interface UserBooksState {
  books: UserLibraryItem[];
  borrowedBooks: UserLibraryItem[];
  lentBooks: UserLibraryItem[];
  incomingRequests: LoanRequest[];
  outgoingRequests: LoanRequest[];
  user: User | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchBooks: () => Promise<void>;
  fetchMyBooks: () => Promise<void>;
  fetchBorrowed: () => Promise<void>;
  fetchLent: () => Promise<void>;
  fetchRequests: () => Promise<void>;
  addBook: (data: AddBookRequest) => Promise<void>;
  removeBook: (id: string) => Promise<void>;
  toggleLendable: (id: string, isLendable: boolean) => Promise<void>;
  acceptRequest: (requestId: string) => Promise<void>;
  rejectRequest: (requestId: string, reason?: string) => Promise<void>;
  cancelRequest: (requestId: string) => Promise<void>;
  returnBook: (id: string) => Promise<void>;
  clearError: () => void;
}

export const useUserBooksStore = create<UserBooksState>((set, get) => ({
  books: [],
  borrowedBooks: [],
  lentBooks: [],
  incomingRequests: [],
  outgoingRequests: [],
  user: null,
  isLoading: false,
  error: null,

  fetchBooks: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await booksApi.getMyLibrary();
      // Backend returns { success, user_id, data: UserLibraryItem[], meta: {...} }
      const books = response.data || [];
      set({ books, isLoading: false });
    } catch (err) {
      set({ 
        error: err instanceof Error ? err.message : 'Błąd ładowania',
        isLoading: false 
      });
    }
  },

  fetchMyBooks: async () => {
    await get().fetchBooks();
  },

  fetchBorrowed: async () => {
    try {
      const response = await loansApi.getBorrowedBooks();
      // Backend returns { success, total, loans, meta: {...} }
      const books = response.loans || [];
      set({ borrowedBooks: books });
    } catch (err) {
      console.error('Failed to fetch borrowed books:', err);
      set({ borrowedBooks: [] });
    }
  },

  fetchLent: async () => {
    try {
      const response = await loansApi.getLentBooks();
      // Backend returns { success, total, loans, meta: {...} }
      const books = response.loans || [];
      set({ lentBooks: books });
    } catch (err) {
      console.error('Failed to fetch lent books:', err);
      set({ lentBooks: [] });
    }
  },

  fetchRequests: async () => {
    set({ isLoading: true, error: null });
    try {
      const [incomingRes, outgoingRes] = await Promise.all([
        loansApi.getIncomingRequests(),
        loansApi.getOutgoingRequests()
      ]);
      
      set({ 
        incomingRequests: incomingRes.success ? (incomingRes.data || []) : [],
        outgoingRequests: outgoingRes.success ? (outgoingRes.data || []) : [],
        isLoading: false 
      });
    } catch (err) {
      set({ 
        error: err instanceof Error ? err.message : 'Błąd ładowania próśb',
        isLoading: false 
      });
    }
  },

  addBook: async (data) => {
    set({ isLoading: true, error: null });
    try {
      await booksApi.addBook(data);
      await get().fetchBooks();
    } catch (err) {
      set({ 
        error: err instanceof Error ? err.message : 'Błąd dodawania',
        isLoading: false 
      });
      throw err;
    }
  },

  removeBook: async (id) => {
    try {
      await booksApi.removeBook(id);
      set(state => ({
        books: state.books.filter(b => b.id !== id)
      }));
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Błąd usuwania' });
      throw err;
    }
  },

  toggleLendable: async (id, isLendable) => {
    try {
      await booksApi.toggleLendable(id, isLendable);
      await get().fetchBooks();
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Błąd aktualizacji' });
      throw err;
    }
  },

  acceptRequest: async (requestId: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await loansApi.acceptRequest(requestId);
      if (response.success && response.data) {
        set(state => ({
          incomingRequests: state.incomingRequests.map(r =>
            r.id === requestId ? response.data! : r
          ),
          isLoading: false
        }));
      } else {
        throw new Error(response.message || 'Nie udało się zaakceptować prośby');
      }
    } catch (err) {
      set({ 
        error: err instanceof Error ? err.message : 'Błąd akceptacji',
        isLoading: false 
      });
      throw err;
    }
  },

  rejectRequest: async (requestId: string, reason?: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await loansApi.rejectRequest(requestId, reason);
      if (response.success && response.data) {
        set(state => ({
          incomingRequests: state.incomingRequests.map(r =>
            r.id === requestId ? response.data! : r
          ),
          isLoading: false
        }));
      } else {
        throw new Error(response.message || 'Nie udało się odrzucić prośby');
      }
    } catch (err) {
      set({ 
        error: err instanceof Error ? err.message : 'Błąd odrzucania',
        isLoading: false 
      });
      throw err;
    }
  },

  // NOTE: reserveRequest removed - endpoint does not exist in backend
  // Status 'reserved' is set automatically by backend when needed

  cancelRequest: async (requestId: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await loansApi.cancelRequest(requestId);
      if (response.success) {
        set(state => ({
          outgoingRequests: state.outgoingRequests.filter(r => r.id !== requestId),
          isLoading: false
        }));
      } else {
        throw new Error(response.message || 'Nie udało się anulować prośby');
      }
    } catch (err) {
      set({ 
        error: err instanceof Error ? err.message : 'Błąd anulowania',
        isLoading: false 
      });
      throw err;
    }
  },

  returnBook: async (id: string) => {
    // Note: API call is handled by useReturnBook hook
    // This method provides optimistic UI update for the store
    set(state => ({
      borrowedBooks: state.borrowedBooks.filter(b => b.id !== id)
    }));
  },

  clearError: () => set({ error: null }),
}));
