// API Client for ShareBook - compatible with cookie-based auth

export const AUTH_UNAUTHORIZED_EVENT = 'auth:unauthorized';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: object | FormData;
  skipCsrf?: boolean;
}

// Get CSRF token from cookies
function getCsrfToken(): string | null {
  // Backend sets cookie as 'XSRF-TOKEN', we need to send header as 'X-CSRF-Token'
  const match = document.cookie.match(/XSRF-TOKEN=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : null;
}

// Helper to determine if request needs CSRF token
function needsCsrfToken(method: string): boolean {
  return ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method.toUpperCase());
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  
  const headers: Record<string, string> = {};
  
  // Add CSRF token for modifying operations
  if (needsCsrfToken(options.method || 'GET') && !options.skipCsrf) {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      headers['X-XSRF-TOKEN'] = csrfToken;
    }
  }
  
  // Add content-type only for JSON requests (not FormData)
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  
  const response = await fetch(url, {
    ...options,
    credentials: 'include', // Important: send cookies
    headers,
    body: options.body instanceof FormData 
      ? options.body 
      : options.body ? JSON.stringify(options.body) : undefined
  });
  
  if (!response.ok) {
    if (response.status === 401) {
      // Emit event to trigger logout in AuthContext
      window.dispatchEvent(new CustomEvent(AUTH_UNAUTHORIZED_EVENT));
      throw new Error('Sesja wygasła. Zaloguj się ponownie.');
    }
    
    if (response.status === 403) {
      const errorData = await response.json().catch(() => ({ detail: 'Brak dostępu' }));
      throw new Error(errorData.detail || errorData.message || 'Brak dostępu');
    }
    
    const errorData = await response.json().catch(() => ({ detail: 'Błąd serwera' }));
    const errorMessage = errorData.detail || errorData.message || errorData.error || 'Błąd serwera';
    throw new Error(errorMessage);
  }
  
  // Handle 204 No Content
  if (response.status === 204) {
    return null as T;
  }
  
  return response.json();
}

export const api = {
  get: <T>(endpoint: string) => apiClient<T>(endpoint, { method: 'GET' }),
  post: <T>(endpoint: string, body: object, skipCsrf?: boolean) => 
    apiClient<T>(endpoint, { method: 'POST', body, skipCsrf }),
  put: <T>(endpoint: string, body: object) => 
    apiClient<T>(endpoint, { method: 'PUT', body }),
  patch: <T>(endpoint: string, body: object) => 
    apiClient<T>(endpoint, { method: 'PATCH', body }),
  delete: <T>(endpoint: string) => apiClient<T>(endpoint, { method: 'DELETE' }),
};
