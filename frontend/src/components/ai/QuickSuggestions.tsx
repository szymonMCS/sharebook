import { Lightbulb } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface QuickSuggestionsProps {
  onSuggestionClick: (text: string) => void;
  suggestions: string[];
  className?: string;
}

export function QuickSuggestions({
  onSuggestionClick,
  suggestions,
  className,
}: QuickSuggestionsProps) {
  return (
    <div className={cn('space-y-3', className)}>
      <div className="flex items-center gap-2 text-book-muted">
        <Lightbulb className="w-4 h-4" />
        <span className="text-xs font-medium">Szybkie sugestie</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            onClick={() => onSuggestionClick(suggestion)}
            className={cn(
              'text-xs rounded-full border-stone-200 hover:border-book-gold hover:text-book-gold hover:bg-book-gold/5',
              'transition-all duration-200'
            )}
          >
            {suggestion}
          </Button>
        ))}
      </div>
    </div>
  );
}
