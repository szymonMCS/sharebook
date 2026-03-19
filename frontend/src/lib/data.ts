import { 
  CheckCircle, 
  Clock, 
  BookOpen, 
  XCircle,
  type LucideIcon 
} from 'lucide-react';

export interface StatusConfig {
  label: string;
  color: string;
  className: string;
  icon: LucideIcon;
}

// Unified status config for all UI components
export const statusConfig: Record<string, StatusConfig> = {
  available: { 
    label: 'Dostępna', 
    color: 'bg-green-100 text-green-800 border-green-200',
    className: 'bg-green-100 text-green-800 border-green-200',
    icon: CheckCircle
  },
  reserved: { 
    label: 'Zarezerwowana', 
    color: 'bg-amber-100 text-amber-800 border-amber-200',
    className: 'bg-amber-100 text-amber-800 border-amber-200',
    icon: Clock
  },
  borrowed: { 
    label: 'Wypożyczona', 
    color: 'bg-blue-100 text-blue-800 border-blue-200',
    className: 'bg-blue-100 text-blue-800 border-blue-200',
    icon: BookOpen
  },
  lent: { 
    label: 'Wypożyczona', 
    color: 'bg-blue-100 text-blue-800 border-blue-200',
    className: 'bg-blue-100 text-blue-800 border-blue-200',
    icon: BookOpen
  },
  unavailable: { 
    label: 'Niedostępna', 
    color: 'bg-gray-100 text-gray-800 border-gray-200',
    className: 'bg-gray-100 text-gray-800 border-gray-200',
    icon: XCircle
  },
};

// Genre list
export const genres = [
  'Wszystkie',
  'Fantasy',
  'Science Fiction',
  'Klasyka',
  'Romans',
  'Dystopia',
  'Literatura dziecięca',
  'Kryminał',
  'Thriller',
  'Biografia',
  'Historia',
  'Poradnik',
];
