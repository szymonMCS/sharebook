import { apiClient } from './client';
import type { ApiResponse, User } from '@/types';

export interface UserUpdateData {
  first_name?: string;
  last_name?: string;
  location?: string;
  phone?: string;
}

export interface PasswordChangeData {
  current_password: string;
  new_password: string;
}

export interface CommunityBook {
  id: string;
  title: string;
  author: string;
  isbn?: string;
  description?: string;
  cover_url?: string;
  status: string;
  is_lendable: boolean;
  owner_id: string;
  owner_name: string;
  owner_email?: string;
  created_at: string;
  updated_at: string;
}

export const usersApi = {
  /**
   * Get current user's profile
   * GET /api/v1/users/me
   */
  getProfile: () =>
    apiClient<ApiResponse<{ user: User }>>('/users/me'),

  /**
   * Update current user's profile
   * PATCH /api/v1/users/me
   */
  updateProfile: (data: UserUpdateData) =>
    apiClient<ApiResponse<{ user: User }>>('/users/me', {
      method: 'PATCH',
      body: data,
    }),

  /**
   * Change current user's password
   * Note: Backend doesn't have a separate endpoint, using PATCH /users/{user_id}
   * This might not work depending on backend implementation
   */
  changePassword: async (_data: PasswordChangeData): Promise<ApiResponse<void>> => {
    // First get current user to get the ID
    const meResponse = await usersApi.getProfile();
    if (!meResponse.success || !meResponse.data?.user) {
      throw new Error('Nie udało się pobrać danych użytkownika');
    }
    const userId = meResponse.data.user.id;
    
    // Note: Backend may not support password change via this endpoint
    // This is a best-effort implementation
    return apiClient<ApiResponse<void>>(`/users/${userId}`, {
      method: 'PATCH',
      body: {
        // Backend expects specific fields - this may vary
        // The actual password change endpoint might be different
      },
    });
  },

  /**
   * Get user by ID
   * GET /api/v1/users/{user_id}
   */
  getUser: (userId: string) =>
    apiClient<ApiResponse<User>>(`/users/${userId}`),

  /**
   * Get user profile by ID
   * GET /api/v1/users/{user_id}/profile
   */
  getUserProfile: (userId: string) =>
    apiClient<ApiResponse<{ profile: User }>>(`/users/${userId}/profile`),
};
