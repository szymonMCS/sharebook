import { useEffect, useState } from 'react';
import { Book, BookOpen, Bookmark, Library, BookCopy } from 'lucide-react';

interface FloatingBook {
  id: number;
  Icon: typeof Book;
  x: number;
  y: number;
  size: number;
  duration: number;
  delay: number;
  opacity: number;
}

export function FloatingBooks() {
  const [books, setBooks] = useState<FloatingBook[]>([]);
  
  const bookIcons = [Book, BookOpen, Bookmark, Library, BookCopy];

  useEffect(() => {
    // Generate random books only on client side to avoid hydration mismatch
    const generatedBooks: FloatingBook[] = Array.from({ length: 12 }, (_, i) => ({
      id: i,
      Icon: bookIcons[i % bookIcons.length],
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: 20 + Math.random() * 40,
      duration: 15 + Math.random() * 25,
      delay: Math.random() * 10,
      opacity: 0.04 + Math.random() * 0.04,
    }));
    setBooks(generatedBooks);
  }, []);

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {books.map((book) => (
        <div
          key={book.id}
          className="absolute text-book-gold animate-float-slow"
          style={{
            left: `${book.x}%`,
            top: `${book.y}%`,
            fontSize: book.size,
            opacity: book.opacity,
            animationDelay: `${book.delay}s`,
            animationDuration: `${book.duration}s`,
          }}
        >
          <book.Icon strokeWidth={1} />
        </div>
      ))}
    </div>
  );
}

export function GradientOrbs() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {/* Large orb top right */}
      <div 
        className="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full opacity-30"
        style={{
          background: 'radial-gradient(circle, rgba(196, 167, 125, 0.3) 0%, transparent 70%)',
          animation: 'pulse 8s ease-in-out infinite',
        }}
      />
      
      {/* Medium orb bottom left */}
      <div 
        className="absolute -bottom-20 -left-20 w-[400px] h-[400px] rounded-full opacity-20"
        style={{
          background: 'radial-gradient(circle, rgba(196, 167, 125, 0.25) 0%, transparent 70%)',
          animation: 'pulse 10s ease-in-out infinite reverse',
        }}
      />
      
      {/* Small orb center */}
      <div 
        className="absolute top-1/2 left-1/3 w-[300px] h-[300px] rounded-full opacity-15"
        style={{
          background: 'radial-gradient(circle, rgba(196, 167, 125, 0.2) 0%, transparent 70%)',
          animation: 'pulse 12s ease-in-out infinite',
        }}
      />
    </div>
  );
}

export function DecorativeCircles() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Animated circle 1 */}
      <div 
        className="absolute top-20 right-20 w-32 h-32 border border-book-gold/20 rounded-full"
        style={{
          animation: 'spin 20s linear infinite',
        }}
      />
      
      {/* Animated circle 2 */}
      <div 
        className="absolute top-28 right-28 w-20 h-20 border border-book-gold/15 rounded-full"
        style={{
          animation: 'spin 15s linear infinite reverse',
        }}
      />
      
      {/* Dotted circle */}
      <div 
        className="absolute bottom-40 left-10 w-24 h-24 border-2 border-dashed border-book-gold/20 rounded-full"
        style={{
          animation: 'spin 25s linear infinite',
        }}
      />
    </div>
  );
}
