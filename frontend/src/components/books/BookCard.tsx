import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MoreVertical, User } from 'lucide-react';
import { LazyBookCover } from './LazyBookCover';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAuth } from '@/components/auth/AuthContext';
import type { Book } from '@/types';
import { statusConfig } from '@/lib/data';

interface BookCardProps {
  book: Book;
  showActions?: boolean;
  onBorrow?: () => void;
  onReserve?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  onClick?: () => void;
  variant?: 'default' | 'compact' | 'horizontal';
  currentUserId?: string;
}

export function BookCard({
  book,
  showActions = true,
  onBorrow: _onBorrow,
  onReserve: _onReserve,
  onEdit,
  onDelete,
  onClick,
  variant = 'default',
  currentUserId,
}: BookCardProps) {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [isHovered, setIsHovered] = useState(false);
  
  const statusInfo = statusConfig[book.status];
  const isOwner = currentUserId === book.owner_id || user?.id === book.owner_id;
  const owner = book.owner;
  
  const handleCardClick = () => {
    if (onClick) {
      onClick();
    } else {
      navigate(`/books/${book.id}`);
    }
  };

  if (variant === 'compact') {
    return (
      <div 
        onClick={handleCardClick}
        className="flex gap-4 p-4 bg-white rounded-xl shadow-sm border border-stone-200/60 hover:shadow-md transition-shadow cursor-pointer"
      >
        <div className="w-20 h-28 flex-shrink-0 rounded-lg overflow-hidden bg-stone-100">
          <LazyBookCover
            coverUrl={book.cover_url}
            title={book.title}
            className="w-full h-full"
          />
        </div>
        <div className="flex-1 min-w-0">
          <Badge className={`mb-2 ${statusInfo.color}`}>
            {statusInfo.label}
          </Badge>
          <h4 className="font-serif font-semibold text-book-brown line-clamp-2 mb-1">
            {book.title}
          </h4>
          <p className="text-sm text-book-gray line-clamp-1">{book.author}</p>
          {owner && (
            <div className="flex items-center gap-1 mt-2 text-xs text-book-muted">
              <User className="w-3 h-3" />
              {owner.username}
            </div>
          )}
        </div>
      </div>
    );
  }

  if (variant === 'horizontal') {
    return (
      <div 
        onClick={handleCardClick}
        className="flex gap-6 p-6 bg-white rounded-xl shadow-sm border border-stone-200/60 hover:shadow-md transition-all cursor-pointer"
      >
        <div className="w-32 h-44 flex-shrink-0 rounded-lg overflow-hidden bg-stone-100">
          <LazyBookCover
            coverUrl={book.cover_url}
            title={book.title}
            className="w-full h-full"
          />
        </div>
        <div className="flex-1 flex flex-col">
          <div className="flex items-start justify-between">
            <div>
              <Badge className={`mb-2 ${statusInfo.color}`}>
                {statusInfo.label}
              </Badge>
              <h3 className="font-serif text-xl font-semibold text-book-brown mb-1">
                {book.title}
              </h3>
              <p className="text-book-gray">{book.author}</p>
            </div>
          </div>
          
          {book.description && (
            <p className="text-sm text-book-gray mt-3 line-clamp-2 flex-1">
              {book.description}
            </p>
          )}
          
          {owner && (
            <div className="flex items-center gap-2 mt-3 text-sm text-book-muted">
              <div className="w-6 h-6 rounded-full bg-stone-200 flex items-center justify-center text-xs font-medium text-stone-600">
                {owner.first_name?.[0] || owner.username?.[0] || '?'}
              </div>
              <span>{owner.first_name} {owner.last_name}</span>
            </div>
          )}
          
          {/* Action buttons removed - user must go to detail page to interact */}
        </div>
      </div>
    );
  }

  // Default variant
  return (
    <div
      onClick={handleCardClick}
      className="group relative bg-white rounded-xl shadow-book border border-stone-200/60 overflow-hidden transition-all duration-300 hover:shadow-book-hover hover:-translate-y-2 cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Cover Container */}
      <div className="relative aspect-[2/3] overflow-hidden bg-stone-100">
        <div className={`transition-transform duration-500 ${isHovered ? 'scale-110' : 'scale-100'}`}>
          <LazyBookCover
            coverUrl={book.cover_url}
            title={book.title}
            className="w-full h-full"
          />
        </div>
        
        {/* Gradient Overlay */}
        <div 
          className={`absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent transition-opacity duration-300 ${
            isHovered ? 'opacity-100' : 'opacity-0'
          }`}
        />
        
        {/* Quick actions removed - user must go to detail page to interact */}
        
        {/* Owner Menu */}
        {isOwner && showActions && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button 
                className={`absolute top-3 left-3 p-2 rounded-full bg-white/90 backdrop-blur-sm transition-all duration-300 hover:bg-white ${
                  isHovered ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-2'
                }`}
              >
                <MoreVertical className="w-4 h-4 text-stone-600" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start">
              <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onEdit?.(); }}>
                Edytuj
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={(e) => { e.stopPropagation(); onDelete?.(); }}
                className="text-red-600 focus:text-red-600"
              >
                Usuń
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
      
      {/* Info */}
      <div className="p-4">
        <Badge className={`mb-2 ${statusInfo.color}`}>
          {statusInfo.label}
        </Badge>
        
        <h3 className="font-serif text-lg font-semibold text-book-brown line-clamp-2 mb-1 group-hover:text-book-gold transition-colors">
          {book.title}
        </h3>
        
        <p className="text-sm text-book-gray line-clamp-1">
          {book.author}
        </p>
        
        {owner && (
          <div className="flex items-center gap-2 mt-3 pt-3 border-t border-stone-100">
            <div className="w-6 h-6 rounded-full bg-stone-200 flex items-center justify-center text-xs font-medium text-stone-600">
              {owner.first_name?.[0] || '?'}
            </div>
            <span className="text-xs text-book-muted">{owner.first_name} {owner.last_name}</span>
          </div>
        )}
      </div>
    </div>
  );
}
