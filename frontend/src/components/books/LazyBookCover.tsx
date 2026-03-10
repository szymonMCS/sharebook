import { useState } from 'react';
import { BookCoverPlaceholder } from './BookCoverPlaceholder';
import { getCoverImageUrl } from '@/lib/utils';

interface LazyBookCoverProps {
  coverUrl: string | undefined | null;
  title: string;
  className?: string;
  alt?: string;
}

/**
 * LazyBookCover - Component that handles book cover loading with fallback.
 * 
 * Features:
 * - Shows placeholder while image is loading
 * - Shows placeholder if image fails to load (404, etc.)
 * - Automatically generates full URL from cover path
 * 
 * This is useful for covers that are generated in background - 
 * the URL is returned immediately, but the file may appear later.
 */
export function LazyBookCover({ 
  coverUrl, 
  title, 
  className = '',
  alt
}: LazyBookCoverProps) {
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Generate full URL (convert null to undefined for compatibility)
  const fullUrl = getCoverImageUrl(coverUrl ?? undefined);

  // If no URL or error occurred, show placeholder
  if (!fullUrl || hasError) {
    return <BookCoverPlaceholder title={title} className={className} />;
  }

  return (
    <div className={`relative ${className}`}>
      {/* Loading placeholder */}
      {isLoading && (
        <div className="absolute inset-0">
          <BookCoverPlaceholder title={title} className="h-full w-full" />
        </div>
      )}
      
      {/* Actual image */}
      <img
        src={fullUrl}
        alt={alt || title}
        className={`w-full h-full object-cover transition-opacity duration-300 ${
          isLoading ? 'opacity-0' : 'opacity-100'
        }`}
        onLoad={() => {
          setIsLoading(false);
        }}
        onError={() => {
          setHasError(true);
          setIsLoading(false);
        }}
      />
    </div>
  );
}
