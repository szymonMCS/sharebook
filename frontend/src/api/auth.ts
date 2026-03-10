import { apiClient } from './client';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'reader' | 'admin';
  location?: string;
  phone?: string;
  is_active?: boolean;
  created_at: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export const authApi = {
  login: async (email: string, password: string): Promise<ApiResponse<{ user: User }>> => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      credentials: 'include', // Important: receive cookies
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Login failed' }));
      throw new Error(error.error || error.detail || 'Login failed');
    }

    return response.json();
  },

  register: (data: { email: string; password: string; first_name: string; last_name: string; location: string; phone?: string }) =>
    apiClient<ApiResponse<{ user: User }>>('/auth/register', { 
      method: 'POST', 
      body: { ...data, role: 'reader' },
      skipCsrf: true, // Registration doesn't require CSRF
    }),

  logout: () => 
    apiClient<void>('/auth/logout', { 
      method: 'POST',
      skipCsrf: false,
    }),

  me: () => apiClient<ApiResponse<{ user: User }>>('/users/me'),
};
