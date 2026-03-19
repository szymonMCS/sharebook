import { useQuery, useQueryClient } from '@tanstack/react-query';
import type { Book } from '@/types';
import { booksApi } from '@/api/books';
import { STALE_TIME } from '@/store/queryClient';

export interface CommunityBookFilters {
  search?: string;
  status?: 'available' | 'reserved' | 'borrowed' | 'lent' | 'unavailable' | 'all';
  author?: string;
  page?: number;
  per_page?: number;
}

export interface PaginationInfo {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface CommunityBooksResponse {
  data: Book[];
  meta: {
    pagination: PaginationInfo;
  };
}

// Query keys
export const communityBookKeys = {
  all: ['communityBooks'] as const,
  lists: () => [...communityBookKeys.all, 'list'] as const,
  list: (filters: CommunityBookFilters) => [...communityBookKeys.lists(), filters] as const,
};

// API function
const fetchCommunityBooks = async (filters?: CommunityBookFilters): Promise<CommunityBooksResponse> => {
  const page = filters?.page || 1;
  const perPage = filters?.per_page || 20;
  
  const response = await booksApi.getCommunityBooks(page, perPage, {
    search: filters?.search,
    status: filters?.status === 'all' ? undefined : filters?.status,
    author: filters?.author,
  });
  
  return {
    data: response.data,
    meta: response.meta,
  };
};

// Hook
export function useCommunityBooks(filters?: CommunityBookFilters) {
  return useQuery({
    queryKey: communityBookKeys.list(filters || {}),
    queryFn: () => fetchCommunityBooks(filters),
    staleTime: STALE_TIME,
  });
}

// Prefetch helpers
export function usePrefetchCommunityBooks() {
  const queryClient = useQueryClient();

  const invalidateCommunityBooks = () => {
    queryClient.invalidateQueries({ queryKey: communityBookKeys.lists() });
  };

  return {
    invalidateCommunityBooks,
    queryClient,
  };
}
