import { api } from './client';

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  success: boolean;
  answer: string;
  sources: {
    title: string;
    author: string;
    similarity_score: number;
  }[];
  model_used: string;
}

export interface AIHealthResponse {
  status: string;
  vector_db: {
    indexed_books?: number;
    total_chunks?: number;
    error?: string;
  };
}

export interface SyncResponse {
  success: boolean;
  total_books: number;
  indexed_books: number;
  total_chunks: number;
  errors: string[];
}

export const aiApi = {
  // Send chat message - POST /ai/chat
  chat: (message: string) =>
    api.post<ChatResponse>('/ai/chat', { message }),
  
  // Get AI health status - GET /ai/health
  getHealth: () =>
    api.get<AIHealthResponse>('/ai/health'),
  
  // Sync all books to RAG (manual trigger, admin only) - POST /ai/sync
  sync: () =>
    api.post<SyncResponse>('/ai/sync', {}),
  
  // NOTE: /ai/history and /ai/history (DELETE) endpoints do not exist in backend
  // Chat history is not persisted server-side
};
