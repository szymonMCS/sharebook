import { BookOpen } from 'lucide-react';

interface BookCoverPlaceholderProps {
  title: string | null | undefined;
  className?: string;
}

export function BookCoverPlaceholder({ title, className = '' }: BookCoverPlaceholderProps) {
  // Get initials from title (first letter of first 2-3 words)
  const getInitials = (text: string | null | undefined): string => {
    if (!text) return '?';
    const words = text.split(/\s+/).filter(w => w.length > 0);
    if (words.length === 0) return '?';
    if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
    return words.slice(0, 2).map(w => w[0].toUpperCase()).join('');
  };

  // Generate a consistent color based on title
  const getColor = (text: string | null | undefined): string => {
    const colors = [
      'bg-amber-100 text-amber-700 border-amber-200',
      'bg-blue-100 text-blue-700 border-blue-200',
      'bg-emerald-100 text-emerald-700 border-emerald-200',
      'bg-rose-100 text-rose-700 border-rose-200',
      'bg-violet-100 text-violet-700 border-violet-200',
      'bg-orange-100 text-orange-700 border-orange-200',
      'bg-cyan-100 text-cyan-700 border-cyan-200',
      'bg-indigo-100 text-indigo-700 border-indigo-200',
    ];
    let hash = 0;
    const safeText = text || '';
    for (let i = 0; i < safeText.length; i++) {
      hash = safeText.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
  };

  const initials = getInitials(title);
  const colorClass = getColor(title);

  return (
    <div
      className={`
        w-full h-full flex flex-col items-center justify-center
        border-2 border-dashed rounded-lg
        ${colorClass}
        ${className}
      `}
    >
      <BookOpen className="w-8 h-8 mb-2 opacity-60" />
      <span className="text-lg font-bold opacity-80">{initials}</span>
    </div>
  );
}
