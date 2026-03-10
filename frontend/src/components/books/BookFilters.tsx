import { Search, Filter, X, ArrowUpAZ, ArrowDownZA } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { BookStatus } from '@/types';

export interface BrowseFilters {
  search: string;
  status: BookStatus | 'all';
  author: string;
  authorSort?: 'az' | 'za';
}

interface BookFiltersProps {
  filters: BrowseFilters;
  onFiltersChange: (filters: BrowseFilters) => void;
  authors: string[];
}

const statusOptions: { value: BookStatus | 'all'; label: string }[] = [
  { value: 'all', label: 'Wszystkie statusy' },
  { value: 'available', label: 'Dostępne' },
  { value: 'reserved', label: 'Zarezerwowane' },
  { value: 'borrowed', label: 'Wypożyczone' },
];

export function BookFilters({ filters, onFiltersChange, authors }: BookFiltersProps) {
  const hasActiveFilters = filters.search || filters.status !== 'all' || filters.author;

  const handleReset = () => {
    onFiltersChange({
      search: '',
      status: 'all',
      author: '',
      authorSort: 'az',
    });
  };

  // Sort authors based on selected sort order
  const sortedAuthors = [...authors].sort((a, b) => {
    if (filters.authorSort === 'za') {
      return b.localeCompare(a);
    }
    return a.localeCompare(b);
  });

  // Filter authors based on search text
  const filteredAuthors = filters.author
    ? sortedAuthors.filter(author =>
        author.toLowerCase().includes(filters.author.toLowerCase())
      )
    : sortedAuthors;

  return (
    <div className="bg-white rounded-xl p-4 sm:p-6 border border-stone-200/60 shadow-sm">
      <div className="flex items-center gap-2 mb-4">
        <Filter className="w-5 h-5 text-book-gold" />
        <h2 className="font-serif font-semibold text-book-brown">Filtry</h2>
        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleReset}
            className="ml-auto text-book-muted hover:text-book-brown"
          >
            <X className="w-4 h-4 mr-1" />
            Wyczyść
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-book-muted" />
          <Input
            placeholder="Szukaj książek..."
            value={filters.search}
            onChange={(e) => onFiltersChange({ ...filters, search: e.target.value })}
            className="pl-10 bg-stone-50 border-stone-200 focus:bg-white"
          />
        </div>

        {/* Status Filter */}
        <Select
          value={filters.status}
          onValueChange={(value) => onFiltersChange({ ...filters, status: value as BookStatus | 'all' })}
        >
          <SelectTrigger className="bg-stone-50 border-stone-200">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            {statusOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Author Filter with Text Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-book-muted" />
          <Input
            placeholder="Szukaj autora..."
            value={filters.author}
            onChange={(e) => onFiltersChange({ ...filters, author: e.target.value })}
            className="pl-10 bg-stone-50 border-stone-200 focus:bg-white"
          />
        </div>
      </div>

      {/* Author Sort and Suggestions */}
      {filters.author && filteredAuthors.length > 0 && (
        <div className="mt-4 pt-4 border-t border-stone-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-book-muted">
              Znaleziono {filteredAuthors.length} autorów
            </span>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onFiltersChange({ ...filters, authorSort: 'az' })}
                className={filters.authorSort !== 'za' ? 'text-book-gold' : 'text-book-muted'}
              >
                <ArrowUpAZ className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onFiltersChange({ ...filters, authorSort: 'za' })}
                className={filters.authorSort === 'za' ? 'text-book-gold' : 'text-book-muted'}
              >
                <ArrowDownZA className="w-4 h-4" />
              </Button>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {filteredAuthors.slice(0, 10).map((author) => (
              <Button
                key={author}
                variant="outline"
                size="sm"
                onClick={() => onFiltersChange({ ...filters, author })}
                className="text-xs"
              >
                {author}
              </Button>
            ))}
            {filteredAuthors.length > 10 && (
              <span className="text-xs text-book-muted self-center">
                +{filteredAuthors.length - 10} więcej
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
