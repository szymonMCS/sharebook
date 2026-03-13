import { api } from './client';
import type { UserLibraryItem, AddBookRequest, Book } from '@/types';

export interface LibraryResponse {
  user_id: string;
  data: UserLibraryItem[];
  meta: {
    pagination: {
      page: number;
      per_page: number;
      total: number;
      total_pages: number;
    }
  };
}

export interface AddBookResponse {
  success: boolean;
  data: {
    book_id: string;
    user_book_id: string;
    isbn: string;
    status: 'processing';
    is_new_book: boolean;
  };
  message: string;
}

export const booksApi = {
  // Get user's library - GET /my-books
  getMyLibrary: (page: number = 1, perPage: number = 20) =>
    api.get<LibraryResponse>(`/my-books?page=${page}&per_page=${perPage}`),
  
  // Get single book by ID - GET /books/{book_id}
  getBook: (bookId: string) =>
    api.get<{ success: boolean; data: Book }>(`/books/${bookId}`),
  
  // Get specific copy of user's book - GET /my-books/{user_book_id}
  getMyBookCopy: (userBookId: string) =>
    api.get<{ success: boolean; data: UserLibraryItem }>(`/my-books/${userBookId}`),
  
  // Add book to library (ISBN required) - POST /my-books
  addBook: (data: AddBookRequest) =>
    api.post<AddBookResponse>('/my-books', {
      isbn: data.isbn,
      condition: data.condition || 'good',
    }),
  
  // Remove book from library by user_book ID - DELETE /my-books/{user_book_id}
  removeBook: (userBookId: string) =>
    api.delete<void>(`/my-books/${userBookId}`),
  
  // Update lendable status by user_book_id - PATCH /my-books/{user_book_id}/lendable
  toggleLendable: (userBookId: string, isLendable: boolean) =>
    api.patch<{ success: boolean; message: string; data: { is_lendable: boolean } }>(
      `/my-books/${userBookId}/lendable`, 
      { is_lendable: isLendable }
    ),
  
  // Update book status by user_book_id - PATCH /my-books/{user_book_id}/status
  updateStatus: (userBookId: string, status: string) =>
    api.patch<{ success: boolean; message: string; data: { status: string } }>(
      `/my-books/${userBookId}/status`, 
      { status }
    ),

  // Search books - GET /books?query=...
  search: (query: string, page: number = 1, perPage: number = 20) =>
    api.get<{ success: boolean; data: Book[]; meta: { pagination: any } }>(
      `/books?query=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`
    ),

  // Get community books - GET /community/books
  getCommunityBooks: (page: number = 1, perPage: number = 20, filters?: { status?: string; search?: string; author?: string }) => {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('per_page', perPage.toString());
    if (filters?.status) params.append('status', filters.status);
    if (filters?.search) params.append('search', filters.search);
    if (filters?.author) params.append('author', filters.author);
    return api.get<{ success: boolean; data: Book[]; meta: { pagination: any } }>(`/community/books?${params.toString()}`);
  },

  // Enrich book data - POST /books/{book_id}/enrich
  enrichBook: (bookId: string) =>
    api.post<{ success: boolean; message: string; status: string }>(`/books/${bookId}/enrich`, {}),
};
