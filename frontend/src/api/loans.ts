import { apiClient } from './client';
import type { ApiResponse, LoanRequest, BorrowedBook, MessageThread, Message } from '@/types';

// Types matching backend schemas
export interface LoanRequestCreate {
  user_book_id: string;
  message?: string;
}

export interface LoanRequestAction {
  action: 'accept' | 'reject';
  reason?: string;
}

export interface MessageCreate {
  content: string;
}

export interface LoanUpdate {
  status: 'returned';
}

export interface LoansResponse {
  success: boolean;
  total: number;
  loans: BorrowedBook[];
  meta: {
    pagination: {
      page: number;
      per_page: number;
      total: number;
      total_pages: number;
    }
  };
  summary?: {
    can_borrow: boolean;
    active_loans: number;
    max_loans: number;
  };
}

export const loansApi = {
  // ========== BOOK MANAGEMENT (User Library) ==========
  // Using booksApi instead - these are aliases for clarity
  
  // ========== LOAN REQUESTS ==========
  
  // Create loan request - POST /loan-requests
  createRequest: (userBookId: string, message?: string) =>
    apiClient<ApiResponse<LoanRequest>>('/loan-requests', { 
      method: 'POST', 
      body: { user_book_id: userBookId, message } 
    }),
  
  // Accept request - PATCH /loan-requests/{request_id}
  acceptRequest: (requestId: string) =>
    apiClient<ApiResponse<LoanRequest>>(`/loan-requests/${requestId}`, { 
      method: 'PATCH',
      body: { action: 'accept' }
    }),
  
  // Reject request - PATCH /loan-requests/{request_id}
  rejectRequest: (requestId: string, reason?: string) =>
    apiClient<ApiResponse<LoanRequest>>(`/loan-requests/${requestId}`, { 
      method: 'PATCH',
      body: { action: 'reject', reason }
    }),
  
  // Get incoming requests - GET /loan-requests/incoming
  getIncomingRequests: (page: number = 1, perPage: number = 20, status?: string) => {
    let url = `/loan-requests/incoming?page=${page}&per_page=${perPage}`;
    if (status) url += `&status=${status}`;
    return apiClient<ApiResponse<LoanRequest[]>>(url);
  },
  
  // Get outgoing requests - GET /loan-requests/outgoing
  getOutgoingRequests: (page: number = 1, perPage: number = 20, status?: string, includeSummary: boolean = false) => {
    let url = `/loan-requests/outgoing?page=${page}&per_page=${perPage}&include_summary=${includeSummary}`;
    if (status) url += `&status=${status}`;
    return apiClient<ApiResponse<LoanRequest[]> & { summary?: any }>(url);
  },

  // Get request details - GET /loan-requests/{request_id}
  getRequestDetails: (requestId: string) =>
    apiClient<ApiResponse<LoanRequest>>(`/loan-requests/${requestId}`),
  
  // Cancel request - DELETE /loan-requests/{request_id}
  cancelRequest: (requestId: string) =>
    apiClient<ApiResponse<void>>(`/loan-requests/${requestId}`, { 
      method: 'DELETE' 
    }),

  // Update request message - PATCH /loan-requests/{request_id}/message
  updateRequestMessage: (requestId: string, message: string) =>
    apiClient<ApiResponse<LoanRequest>>(`/loan-requests/${requestId}/message`, {
      method: 'PATCH',
      body: { message }
    }),

  // ========== MESSAGES ==========
  
  getMessages: (requestId: string) =>
    apiClient<ApiResponse<MessageThread>>(`/loan-requests-messages/${requestId}/messages`),
  
  sendMessage: (requestId: string, content: string) =>
    apiClient<ApiResponse<Message>>(`/loan-requests-messages/${requestId}/messages`, {
      method: 'POST',
      body: { content }
    }),

  markAllMessagesRead: (requestId: string) =>
    apiClient<ApiResponse<{ marked_as_read: number }>>(`/loan-requests-messages/${requestId}/messages/read-all`, {
      method: 'POST'
    }),

  markMessageRead: (messageId: string) =>
    apiClient<ApiResponse<boolean>>(`/loan-requests-messages/messages/${messageId}/read`, {
      method: 'PATCH'
    }),

  // ========== LOANS ==========
  
  // Get loans - GET /loans?type=...
  getLoans: (type?: 'borrowed' | 'lent', status?: string, page: number = 1, perPage: number = 20, includeSummary: boolean = false) => {
    let url = `/loans?page=${page}&per_page=${perPage}`;
    if (type) url += `&type=${type}`;
    if (status) url += `&status=${status}`;
    if (includeSummary) url += `&include_summary=true`;
    return apiClient<LoansResponse>(url);
  },
  
  // Get borrowed books - GET /loans?type=borrowed
  getBorrowedBooks: (status?: string, page: number = 1, perPage: number = 20) =>
    loansApi.getLoans('borrowed', status, page, perPage),
  
  // Get lent books - GET /loans?type=lent
  getLentBooks: (status?: string, page: number = 1, perPage: number = 20) =>
    loansApi.getLoans('lent', status, page, perPage),
  
  // Get loan details - GET /loans/{loan_id}
  getLoanDetails: (loanId: string) =>
    apiClient<ApiResponse<BorrowedBook>>(`/loans/${loanId}`),
  
  // Return book - PATCH /loans/{loan_id}
  returnBook: (loanId: string) =>
    apiClient<ApiResponse<{ success: boolean; message: string; loan: any }>>(`/loans/${loanId}`, { 
      method: 'PATCH',
      body: { status: 'returned' }
    }),
};
