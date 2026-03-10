import { useQuery, useQueryClient } from '@tanstack/react-query';
import type { Book, BookFilters } from '@/types';
import { booksApi } from '@/api/books';
import { STALE_TIME } from '@/store/queryClient';

// Query keys
export const bookKeys = {
  all: ['books'] as const,
  lists: () => [...bookKeys.all, 'list'] as const,
  list: (filters: BookFilters) => [...bookKeys.lists(), filters] as const,
  details: () => [...bookKeys.all, 'detail'] as const,
  detail: (id: string) => [...bookKeys.details(), id] as const,
  community: () => [...bookKeys.all, 'community'] as const,
  library: (page?: number) => [...bookKeys.all, 'library', page] as const,
};

// API functions
const fetchBooks = async (filters?: BookFilters): Promise<Book[]> => {
  const response = await booksApi.search(
    filters?.search || '',
    1,
    100
  );
  return response.data;
};

const fetchCommunityBooks = async (filters?: BookFilters, page: number = 1, perPage: number = 20): Promise<Book[]> => {
  const response = await booksApi.getCommunityBooks(page, perPage, {
    status: filters?.status !== 'all' ? filters?.status : undefined,
    search: filters?.search,
    author: filters?.author,
  });
  return response.data;
};

const fetchBookById = async (id: string): Promise<Book> => {
  const response = await booksApi.getBook(id);
  return response.data;
};

// Hooks
export function useBooks(filters?: BookFilters) {
  return useQuery({
    queryKey: bookKeys.list(filters || {}),
    queryFn: () => fetchBooks(filters),
    staleTime: STALE_TIME,
  });
}

export function useCommunityBooks(filters?: BookFilters, page: number = 1, perPage: number = 20) {
  return useQuery({
    queryKey: [...bookKeys.community(), filters, page, perPage],
    queryFn: () => fetchCommunityBooks(filters, page, perPage),
    staleTime: STALE_TIME,
  });
}

export function useBook(id: string) {
  return useQuery({
    queryKey: bookKeys.detail(id),
    queryFn: () => fetchBookById(id),
    staleTime: STALE_TIME,
    enabled: !!id,
  });
}

// Prefetch helpers
export function usePrefetchBooks() {
  const queryClient = useQueryClient();

  const prefetchBook = (id: string) => {
    queryClient.prefetchQuery({
      queryKey: bookKeys.detail(id),
      queryFn: () => fetchBookById(id),
      staleTime: STALE_TIME,
    });
  };

  const invalidateBooks = () => {
    queryClient.invalidateQueries({ queryKey: bookKeys.lists() });
    queryClient.invalidateQueries({ queryKey: bookKeys.community() });
  };

  const invalidateBook = (id: string) => {
    queryClient.invalidateQueries({ queryKey: bookKeys.detail(id) });
  };

  const setBookData = (id: string, data: Book) => {
    queryClient.setQueryData(bookKeys.detail(id), data);
  };

  return {
    prefetchBook,
    invalidateBooks,
    invalidateBook,
    setBookData,
    queryClient,
  };
}
