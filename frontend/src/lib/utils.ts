import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Build full URL for book cover image.
 * Handles both external URLs and local paths.
 * 
 * @param coverUrl - URL from API (can be external http/https or local /assets/...)
 * @returns Full URL for the image
 */
export function getCoverImageUrl(coverUrl: string | undefined): string | undefined {
  if (!coverUrl) return undefined;
  
  // If it's already a full URL (external), return as-is
  if (coverUrl.startsWith('http://') || coverUrl.startsWith('https://')) {
    return coverUrl;
  }
  
  // Get API URL from Vite env or use default
  let apiUrl: string;
  try {
    apiUrl = (import.meta as { env?: { VITE_API_URL?: string } }).env?.VITE_API_URL || 'http://localhost:8000/api/v1';
  } catch {
    apiUrl = 'http://localhost:8000/api/v1';
  }
  
  // Remove /api/v1 from the end to get base API URL
  const baseUrl = apiUrl.replace(/\/api\/v1$/, '');
  
  // Handle backend/database/covers/ paths from database
  if (coverUrl.startsWith('backend/database/covers/')) {
    const filename = coverUrl.replace('backend/database/covers/', '');
    return `${baseUrl}/covers/${filename}`;
  }
  
  // If it's a local path starting with /assets/ or /covers/, prepend API URL
  if (coverUrl.startsWith('/assets/') || coverUrl.startsWith('/covers/')) {
    return `${baseUrl}${coverUrl}`;
  }
  
  // Legacy: if it starts with assets/ or covers/ without leading slash, add it
  if (coverUrl.startsWith('assets/') || coverUrl.startsWith('covers/')) {
    return `${baseUrl}/${coverUrl}`;
  }
  
  return coverUrl;
}
