import { QueryClient } from '@tanstack/react-query';

const STALE_TIME = 5 * 60 * 1000; // 5 minut
const CACHE_TIME = 10 * 60 * 1000; // 10 minut
const RETRY_COUNT = 3;

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: STALE_TIME,
      gcTime: CACHE_TIME,
      retry: RETRY_COUNT,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
      refetchOnMount: true,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Eksportuj stałe dla użycia w hookach
export { STALE_TIME, CACHE_TIME, RETRY_COUNT };
