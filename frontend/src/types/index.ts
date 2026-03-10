// User types
export interface User {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  username?: string;
  avatar_url?: string;
  role?: 'user' | 'admin';
  is_active?: boolean;
  created_at: string;
}

// Book status type
export type BookStatus = 'available' | 'lent' | 'borrowed' | 'reserved' | 'unavailable';

// Book filters type
export interface BookFilters {
  search?: string;
  genre?: string;
  status?: BookStatus | 'all';
  author?: string;
}

// Book in library (from Book table)
export interface BookInLibrary {
  id: string;
  isbn: string;
  title: string;
  author: string | null;
  description: string | null;
  cover_url: string | null;
  publisher: string | null;
  publication_year: number | null;
  page_count?: number | null;
  language?: string | null;
  genre?: string | null;
}

// Book with owner information (for community books)
export interface Book {
  id: string;
  book_id?: string;  // Actual book ID (for enrich endpoint)
  isbn: string;
  title: string;
  author: string | null;
  description: string | null;
  cover_url: string | null;
  publisher: string | null;
  publication_year: number | null;
  page_count?: number | null;
  language?: string | null;
  genre?: string | null;
  published_date?: string;
  status: BookStatus;
  is_lendable: boolean;
  owner_id: string;
  owner?: {
    id: string;
    first_name: string;
    last_name: string;
    location: string | null;
    username?: string;
    avatar_url?: string;
  };
  condition?: string | null;
  created_at: string;
  updated_at?: string;
}

// UserBook types (association)
export interface UserBook {
  id: string;
  user_id: string;
  book_id: string;
  book?: BookInLibrary;
  status: BookStatus;
  condition: string | null;
  is_lendable: boolean;
  user_notes: string | null;
  added_at: string;
  updated_at: string;
}

// Library item (combined)
export interface UserLibraryItem {
  id: string;
  book: BookInLibrary;
  book_id?: string;
  title?: string;
  author?: string;
  cover_url?: string | null;
  status: BookStatus;
  condition: string | null;
  is_lendable: boolean;
  user_notes: string | null;
  added_at: string;
  due_date?: string | null;
  borrowed_at?: string | null;
  owner_id?: string;
  owner_name?: string;
  owner_avatar?: string | null;
}

// Add book request (ISBN required!)
export interface AddBookRequest {
  isbn: string;
  title?: string;
  author?: string;
  description?: string;
  publisher?: string;
  publication_year?: number;
  language?: string;
  genre?: string;
  condition?: string;
  is_lendable?: boolean;
}

// Aliases for backward compatibility
export type BookCreate = AddBookRequest;
export type BorrowedBook = UserLibraryItem;

// Chat types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  recommendations?: BookRecommendation[];
  created_at: string;
}

export interface BookRecommendation {
  id: string;
  title: string;
  author: string;
  score: number;
}

// Navigation types
export interface NavItem {
  id: string;
  label: string;
  href: string;
  icon?: string;
  scrollTo?: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Loan Request types
export interface LoanRequest {
  id: string;
  book_id: string;
  book_title: string;
  book_cover_url: string | null;
  owner_id: string;
  owner_name: string;
  owner_avatar: string | null;
  borrower_id: string;
  borrower_name: string;
  borrower_avatar: string | null;
  status: 'pending' | 'reserved' | 'accepted' | 'rejected' | 'cancelled';
  message: string | null;
  reason: string | null;
  created_at: string;
  responded_at: string | null;
}

// Loan types
export interface Loan {
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

// Message types for loan request threads
export interface Message {
  id: string;
  loan_request_id: string;
  sender_id: string;
  sender_name: string;
  sender_avatar: string | null;
  content: string;
  message_type: 'text' | 'system';
  is_read: boolean;
  created_at: string;
}

export interface MessageThread {
  loan_request_id: string;
  book_id: string;
  book_title: string;
  status: string;
  messages: Message[];
  total_messages: number;
  unread_count: number;
}
