import { apiClient } from './client';
import type { ApiResponse, PaginatedResponse } from '@/types';
import type { User } from './auth';

export interface AdminDashboardStats {
  total_users: number;
  total_books: number;
  total_loans: number;
  pending_requests: number;
  active_loans: number;
  new_users_today: number;
  new_books_today: number;
  generated_at: string;
}

export interface AdminUser extends User {
  created_at: string;
  is_active: boolean;
  books_count?: number;
}

export interface AdminBook {
  id: string;
  title: string;
  author: string;
  isbn?: string;
  description?: string;
  publisher?: string;
  publication_year?: number;
  cover_url?: string;
  genre?: string;
  created_at: string;
  updated_at: string;
}

export interface AdminUserBook {
  user_book_id: string;
  user_id: string;
  user_email: string;
  user_name: string;
  book_id: string;
  book_title: string;
  book_author: string;
  book_isbn?: string;
  book_cover_url?: string;
  status: 'available' | 'reserved' | 'borrowed' | 'unavailable';
  condition?: string;
  is_lendable: boolean;
  has_active_loan: boolean;
  added_at: string;
}

export interface ResetPasswordResponse {
  temp_password: string;
}

export const adminApi = {
  // ========== DASHBOARD ==========
  
  // Dashboard stats - GET /admin/dashboard
  getDashboard: () =>
    apiClient<ApiResponse<AdminDashboardStats>>('/admin/dashboard'),

  // ========== USERS MANAGEMENT ==========
  
  // Get users list - GET /admin/users
  getUsers: (page: number = 1, perPage: number = 10, search?: string) => {
    let url = `/admin/users?page=${page}&per_page=${perPage}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    return apiClient<ApiResponse<PaginatedResponse<AdminUser>>>(url);
  },

  // Get user details - GET /admin/users/{user_id}
  getUserDetails: (id: string) =>
    apiClient<ApiResponse<AdminUser>>(`/admin/users/${id}`),

  // Update user role - PATCH /admin/users/{user_id}/role
  updateUserRole: (id: string, role: 'admin' | 'reader') =>
    apiClient<ApiResponse<{ id: string; role: string }>>(`/admin/users/${id}/role`, { 
      method: 'PATCH', 
      body: { role } 
    }),

  // Reset user password - POST /admin/users/{user_id}/reset-password
  resetUserPassword: (id: string) =>
    apiClient<ApiResponse<ResetPasswordResponse>>(`/admin/users/${id}/reset-password`, { 
      method: 'POST' 
    }),

  // Deactivate user - POST /admin/users/{user_id}/deactivate
  deactivateUser: (id: string) =>
    apiClient<ApiResponse<{ id: string; is_active: boolean }>>(`/admin/users/${id}/deactivate`, {
      method: 'POST'
    }),

  // Activate user - POST /admin/users/{user_id}/activate
  activateUser: (id: string) =>
    apiClient<ApiResponse<{ id: string; is_active: boolean }>>(`/admin/users/${id}/activate`, {
      method: 'POST'
    }),

  // Delete user - DELETE /admin/users/{user_id}
  deleteUser: (id: string) =>
    apiClient<ApiResponse<void>>(`/admin/users/${id}`, { 
      method: 'DELETE' 
    }),

  // ========== BOOKS MANAGEMENT ==========
  
  // Get books list - GET /admin/books
  getBooks: (page: number = 1, perPage: number = 10, search?: string) => {
    let url = `/admin/books?page=${page}&per_page=${perPage}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    return apiClient<ApiResponse<PaginatedResponse<AdminBook>>>(url);
  },

  // Get book details - GET /admin/books/{book_id}
  getBookDetails: (id: string) =>
    apiClient<ApiResponse<AdminBook>>(`/admin/books/${id}`),

  // Update book metadata - PATCH /admin/books/{book_id}
  updateBookMetadata: (id: string, metadata: Partial<AdminBook>) =>
    apiClient<ApiResponse<AdminBook>>(`/admin/books/${id}`, {
      method: 'PATCH',
      body: metadata
    }),

  // Merge books - POST /admin/books/merge
  mergeBooks: (sourceId: string, targetId: string) =>
    apiClient<ApiResponse<{ moved_copies: number }>>('/admin/books/merge', {
      method: 'POST',
      body: { source_id: sourceId, target_id: targetId }
    }),

  // Delete book - DELETE /admin/books/{book_id}
  deleteBook: (id: string, force: boolean = false) =>
    apiClient<ApiResponse<void>>(`/admin/books/${id}?force=${force}`, { 
      method: 'DELETE' 
    }),

  // Add book - POST /admin/books
  addBook: (data: { isbn: string; title?: string; author?: string; description?: string }) =>
    apiClient<ApiResponse<AdminBook>>('/admin/books', {
      method: 'POST',
      body: data
    }),

  // ========== USER BOOKS MANAGEMENT ==========
  
  // List user books - GET /admin/books/user-books
  getUserBooks: (params?: { user_id?: string; book_id?: string; page?: number; per_page?: number }) => {
    let url = '/admin/books/user-books?page=' + (params?.page || 1) + '&per_page=' + (params?.per_page || 20);
    if (params?.user_id) url += `&user_id=${params.user_id}`;
    if (params?.book_id) url += `&book_id=${params.book_id}`;
    return apiClient<ApiResponse<PaginatedResponse<AdminUserBook>>>(url);
  },

  // Add book to user - POST /admin/books/user-books
  addBookToUser: (userId: string, bookId: string, condition: string = 'good', isLendable: boolean = true) =>
    apiClient<ApiResponse<{ user_book_id: string; message: string }>>('/admin/books/user-books', {
      method: 'POST',
      body: { user_id: userId, book_id: bookId, condition, is_lendable: isLendable }
    }),

  // Remove book from user - DELETE /admin/books/user-books/{user_book_id}
  removeBookFromUser: (userBookId: string, force: boolean = false) =>
    apiClient<ApiResponse<{ user_book_id: string; message: string }>>(`/admin/books/user-books/${userBookId}?force=${force}`, {
      method: 'DELETE'
    }),

  // Update user book status - PATCH /admin/books/user-books/{user_book_id}
  updateUserBookStatus: (userBookId: string, status: string, isLendable?: boolean) =>
    apiClient<ApiResponse<{ user_book_id: string; status: string; message: string }>>(`/admin/books/user-books/${userBookId}`, {
      method: 'PATCH',
      body: { status, is_lendable: isLendable }
    }),

  // NOTE: /admin/loans endpoint does not exist in backend
  // Use loansApi.getLoans() instead for viewing loans
};
