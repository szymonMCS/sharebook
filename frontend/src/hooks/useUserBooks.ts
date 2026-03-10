import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { BookCreate, UserLibraryItem } from '@/types';
import { booksApi } from '@/api/books';
import { loansApi } from '@/api/loans';
import { STALE_TIME } from '@/store/queryClient';

// Query keys
export const userBookKeys = {
  all: ['userBooks'] as const,
  lists: () => [...userBookKeys.all, 'list'] as const,
  myBooks: () => [...userBookKeys.lists(), 'my'] as const,
  borrowed: () => [...userBookKeys.all, 'borrowed'] as const,
  lent: () => [...userBookKeys.all, 'lent'] as const,
  requests: () => [...userBookKeys.all, 'requests'] as const,
  incomingRequests: () => [...userBookKeys.requests(), 'incoming'] as const,
  outgoingRequests: () => [...userBookKeys.requests(), 'outgoing'] as const,
};

// Hooks dla książek użytkownika
export function useMyBooks(page: number = 1, perPage: number = 20) {
  return useQuery({
    queryKey: [...userBookKeys.myBooks(), page, perPage],
    queryFn: async () => {
      const response = await booksApi.getMyLibrary(page, perPage);
      // Backend returns { success, user_id, data: UserLibraryItem[], meta: {pagination} }
      return response.data || [];
    },
    staleTime: 0, // Always refetch to avoid stale data
    refetchOnMount: true,
  });
}

export function useBorrowedBooks(page: number = 1, perPage: number = 20) {
  return useQuery({
    queryKey: [...userBookKeys.borrowed(), page, perPage],
    queryFn: async () => {
      const response = await loansApi.getBorrowedBooks(undefined, page, perPage);
      return response.loans || [];
    },
    staleTime: STALE_TIME,
  });
}

export function useLentBooks(page: number = 1, perPage: number = 20) {
  return useQuery({
    queryKey: [...userBookKeys.lent(), page, perPage],
    queryFn: async () => {
      const response = await loansApi.getLentBooks(undefined, page, perPage);
      return response.loans || [];
    },
    staleTime: STALE_TIME,
  });
}

export function useLoanRequests(incomingPage: number = 1, outgoingPage: number = 1, perPage: number = 20) {
  const queryClient = useQueryClient();

  const { data: incoming = [], isLoading: isLoadingIncoming } = useQuery({
    queryKey: [...userBookKeys.incomingRequests(), incomingPage, perPage],
    queryFn: async () => {
      const response = await loansApi.getIncomingRequests(incomingPage, perPage);
      return response.data || [];
    },
    staleTime: STALE_TIME,
  });

  const { data: outgoing = [], isLoading: isLoadingOutgoing } = useQuery({
    queryKey: [...userBookKeys.outgoingRequests(), outgoingPage, perPage],
    queryFn: async () => {
      const response = await loansApi.getOutgoingRequests(outgoingPage, perPage);
      return response.data || [];
    },
    staleTime: STALE_TIME,
  });

  const invalidateRequests = () => {
    queryClient.invalidateQueries({ queryKey: userBookKeys.requests() });
  };

  return {
    incoming,
    outgoing,
    isLoading: isLoadingIncoming || isLoadingOutgoing,
    invalidateRequests,
  };
}

// Mutations
export function useCreateBook() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (book: BookCreate) => booksApi.addBook(book),
    onSuccess: () => {
      // Po dodaniu książki, odśwież listę moich książek
      queryClient.invalidateQueries({ queryKey: userBookKeys.myBooks() });
    },
  });
}

export function useUpdateBookStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      booksApi.updateStatus(id, status),
    onSuccess: () => {
      // Po zmianie statusu, odśwież listę moich książek
      queryClient.invalidateQueries({ queryKey: userBookKeys.myBooks() });
    },
  });
}

export function useDeleteBook() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => booksApi.removeBook(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userBookKeys.myBooks() });
    },
  });
}

export function useToggleLendable() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, isLendable }: { id: string; isLendable: boolean }) =>
      booksApi.toggleLendable(id, isLendable),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userBookKeys.myBooks() });
    },
  });
}

export function useCreateLoanRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userBookId, message }: { userBookId: string; message?: string }) =>
      loansApi.createRequest(userBookId, message),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userBookKeys.outgoingRequests() });
    },
  });
}

export function useAcceptRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (requestId: string) => loansApi.acceptRequest(requestId),
    onSuccess: () => {
      // Odśwież przychodzące prośby, wypożyczone i pożyczone książki
      queryClient.invalidateQueries({ queryKey: userBookKeys.requests() });
      queryClient.invalidateQueries({ queryKey: userBookKeys.borrowed() });
      queryClient.invalidateQueries({ queryKey: userBookKeys.lent() });
      queryClient.invalidateQueries({ queryKey: userBookKeys.myBooks() });
    },
  });
}

export function useRejectRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ requestId, reason }: { requestId: string; reason?: string }) =>
      loansApi.rejectRequest(requestId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userBookKeys.incomingRequests() });
    },
  });
}

export function useCancelRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (requestId: string) => loansApi.cancelRequest(requestId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userBookKeys.outgoingRequests() });
    },
  });
}

export function useReturnBook() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (loanId: string) => loansApi.returnBook(loanId),
    onSuccess: () => {
      // Odśwież wypożyczone książki, pożyczone książki i moje książki
      queryClient.invalidateQueries({ queryKey: userBookKeys.borrowed() });
      queryClient.invalidateQueries({ queryKey: userBookKeys.lent() });
      queryClient.invalidateQueries({ queryKey: userBookKeys.myBooks() });
    },
  });
}

// Hook łączący wszystkie operacje
export function useUserBooks(myBooksPage?: number, borrowedPage?: number, lentPage?: number) {
  const myBooksQuery = useMyBooks(myBooksPage);
  const borrowedQuery = useBorrowedBooks(borrowedPage);
  const lentQuery = useLentBooks(lentPage);
  const requestsQuery = useLoanRequests();

  const createBook = useCreateBook();
  const updateBookStatus = useUpdateBookStatus();
  const deleteBook = useDeleteBook();
  const toggleLendable = useToggleLendable();
  const createRequest = useCreateLoanRequest();
  const acceptRequest = useAcceptRequest();
  const rejectRequest = useRejectRequest();
  const cancelRequest = useCancelRequest();
  const returnBook = useReturnBook();

  return {
    // Queries
    myBooks: myBooksQuery.data ?? [],
    borrowedBooks: borrowedQuery.data ?? [],
    lentBooks: lentQuery.data ?? [],
    incomingRequests: requestsQuery.incoming,
    outgoingRequests: requestsQuery.outgoing,
    
    // Loading states
    isLoadingMyBooks: myBooksQuery.isLoading,
    isLoadingBorrowed: borrowedQuery.isLoading,
    isLoadingLent: lentQuery.isLoading,
    isLoadingRequests: requestsQuery.isLoading,
    isLoading: myBooksQuery.isLoading || borrowedQuery.isLoading || lentQuery.isLoading || requestsQuery.isLoading,
    
    // Errors
    myBooksError: myBooksQuery.error,
    borrowedError: borrowedQuery.error,
    lentError: lentQuery.error,
    
    // Refetch functions
    refetchMyBooks: myBooksQuery.refetch,
    refetchBorrowed: borrowedQuery.refetch,
    refetchLent: lentQuery.refetch,
    
    // Mutations
    createBook: createBook.mutateAsync,
    updateBookStatus: updateBookStatus.mutateAsync,
    deleteBook: deleteBook.mutateAsync,
    toggleLendable: toggleLendable.mutateAsync,
    createRequest: createRequest.mutateAsync,
    acceptRequest: acceptRequest.mutateAsync,
    rejectRequest: rejectRequest.mutateAsync,
    cancelRequest: cancelRequest.mutateAsync,
    returnBook: returnBook.mutateAsync,
    
    // Mutation states
    isCreatingBook: createBook.isPending,
    isUpdatingBookStatus: updateBookStatus.isPending,
    isDeletingBook: deleteBook.isPending,
    isTogglingLendable: toggleLendable.isPending,
    isCreatingRequest: createRequest.isPending,
    isAcceptingRequest: acceptRequest.isPending,
    isRejectingRequest: rejectRequest.isPending,
    isCancellingRequest: cancelRequest.isPending,
    isReturningBook: returnBook.isPending,
  };
}
