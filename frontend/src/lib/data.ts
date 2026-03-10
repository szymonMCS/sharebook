import type { Book, User, Loan, ChatMessage } from '@/types';
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

// Mock users
export const mockUsers: User[] = [
  {
    id: '1',
    username: 'anna_czytelniczka',
    email: 'anna@example.com',
    avatar_url: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop',
    role: 'user',
    first_name: 'Anna',
    last_name: 'Kowalska',
    is_active: true,
    created_at: '2024-01-15T10:00:00Z',
  },
  {
    id: '2',
    username: 'marek_ksiazkowy',
    email: 'marek@example.com',
    avatar_url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop',
    role: 'user',
    first_name: 'Marek',
    last_name: 'Nowak',
    is_active: true,
    created_at: '2024-02-20T14:30:00Z',
  },
  {
    id: '3',
    username: 'kasia_bibliotekarka',
    email: 'kasia@example.com',
    avatar_url: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop',
    role: 'admin',
    first_name: 'Kasia',
    last_name: 'Wójcik',
    is_active: true,
    created_at: '2023-12-01T09:00:00Z',
  },
];

// Mock books with cover images
export const mockBooks: Book[] = [
  {
    id: '1',
    owner_id: '1',
    isbn: '978-83-8008-449-5',
    title: 'Wiedźmin: Ostatnie życzenie',
    author: 'Andrzej Sapkowski',
    description: 'Pierwszy tom cyklu wiedźmińskiego, zawierający opowiadania o przygodach Geralta z Rivii.',
    cover_url: 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=600&fit=crop',
    genre: 'Fantasy',
    page_count: 332,
    published_date: '1993',
    status: 'available',
    is_lendable: true,
    publisher: 'SuperNOWA',
    publication_year: 1993,
    created_at: '2024-03-01T10:00:00Z',
    updated_at: '2024-03-01T10:00:00Z',
  },
  {
    id: '2',
    owner_id: '1',
    isbn: '978-83-7506-530-8',
    title: '1984',
    author: 'George Orwell',
    description: 'Klasyczna dystopia przedstawiająca totalitarne społeczeństwo pod stałym nadzorem Wielkiego Brata.',
    cover_url: 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400&h=600&fit=crop',
    genre: 'Dystopia',
    page_count: 328,
    published_date: '1949',
    status: 'borrowed',
    is_lendable: true,
    publisher: 'Muza',
    publication_year: 1949,
    created_at: '2024-03-05T14:20:00Z',
    updated_at: '2024-03-10T09:15:00Z',
  },
  {
    id: '3',
    owner_id: '2',
    isbn: '978-83-240-3536-3',
    title: 'Mały Książę',
    author: 'Antoine de Saint-Exupéry',
    description: 'Filozoficzna baśń o małym księciu podróżującym po wszechświecie i poznającym dziwnych dorosłych.',
    cover_url: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=600&fit=crop',
    genre: 'Literatura dziecięca',
    page_count: 96,
    published_date: '1943',
    status: 'available',
    is_lendable: true,
    publisher: 'Nasza Księgarnia',
    publication_year: 1943,
    created_at: '2024-02-15T11:30:00Z',
    updated_at: '2024-02-15T11:30:00Z',
  },
  {
    id: '4',
    owner_id: '2',
    isbn: '978-83-7432-459-8',
    title: 'Hobbit, czyli tam i z powrotem',
    author: 'J.R.R. Tolkien',
    description: 'Historia Bilba Bagginsa, który wyrusza na nieoczekiwaną przygodę z krasnoludami i czarodziejem.',
    cover_url: 'https://images.unsplash.com/photo-1621351183012-e2f997203889?w=400&h=600&fit=crop',
    genre: 'Fantasy',
    page_count: 315,
    published_date: '1937',
    status: 'reserved',
    is_lendable: true,
    publisher: 'Iskry',
    publication_year: 1937,
    created_at: '2024-01-20T16:45:00Z',
    updated_at: '2024-03-12T10:20:00Z',
  },
  {
    id: '5',
    owner_id: '3',
    isbn: '978-83-080-5492-5',
    title: 'Zbrodnia i kara',
    author: 'Fiodor Dostojewski',
    description: 'Psychologiczna powieść o młodym studencie, który popełnia morderstwo i zmaga się z wyrzutami sumienia.',
    cover_url: 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=600&fit=crop',
    genre: 'Klasyka',
    page_count: 672,
    published_date: '1866',
    status: 'available',
    is_lendable: true,
    publisher: 'Zysk i S-ka',
    publication_year: 1866,
    created_at: '2024-03-08T13:00:00Z',
    updated_at: '2024-03-08T13:00:00Z',
  },
  {
    id: '6',
    owner_id: '1',
    isbn: '978-83-7432-007-1',
    title: 'Harry Potter i Kamień Filozoficzny',
    author: 'J.K. Rowling',
    description: 'Pierwsza część przygód młodego czarodzieja Harry\'ego Pottera w Szkole Magii i Czarodziejstwa.',
    cover_url: 'https://images.unsplash.com/photo-1618666012174-83b441c0bc76?w=400&h=600&fit=crop',
    genre: 'Fantasy',
    page_count: 328,
    published_date: '1997',
    status: 'available',
    is_lendable: true,
    publisher: 'Media Rodzina',
    publication_year: 1997,
    created_at: '2024-02-28T09:30:00Z',
    updated_at: '2024-02-28T09:30:00Z',
  },
  {
    id: '7',
    owner_id: '2',
    isbn: '978-83-240-3537-0',
    title: 'Duma i uprzedzenie',
    author: 'Jane Austen',
    description: 'Romantyczna powieść o miłości i społecznych konwencjach w angielskiej prowincji XIX wieku.',
    cover_url: 'https://images.unsplash.com/photo-1476275466078-4007374efbbe?w=400&h=600&fit=crop',
    genre: 'Romans',
    page_count: 416,
    published_date: '1813',
    status: 'unavailable',
    is_lendable: false,
    publisher: 'Wydawnictwo Dolnośląskie',
    publication_year: 1813,
    created_at: '2024-01-10T15:20:00Z',
    updated_at: '2024-01-15T11:00:00Z',
  },
  {
    id: '8',
    owner_id: '3',
    isbn: '978-83-7432-123-8',
    title: 'Władca Pierścieni: Drużyna Pierścienia',
    author: 'J.R.R. Tolkien',
    description: 'Pierwszy tom epickiej trylogii fantasy o walce Dobra ze Złem w Śródziemiu.',
    cover_url: 'https://images.unsplash.com/photo-1509021436665-8f07dbf5bf1d?w=400&h=600&fit=crop',
    genre: 'Fantasy',
    page_count: 448,
    published_date: '1954',
    status: 'available',
    is_lendable: true,
    publisher: 'Czytelnik',
    publication_year: 1954,
    created_at: '2024-03-15T10:45:00Z',
    updated_at: '2024-03-15T10:45:00Z',
  },
  {
    id: '9',
    owner_id: '1',
    isbn: '978-83-080-1234-5',
    title: 'Mistrz i Małgorzata',
    author: 'Michaił Bułhakow',
    description: 'Mistyczna powieść o wizycie szatana w Moskwie i miłości Mistrza do Małgorzaty.',
    cover_url: 'https://images.unsplash.com/photo-1519682337058-a94d519337bc?w=400&h=600&fit=crop',
    genre: 'Klasyka',
    page_count: 384,
    published_date: '1967',
    status: 'available',
    is_lendable: true,
    publisher: 'Pomorska',
    publication_year: 1967,
    created_at: '2024-02-10T14:00:00Z',
    updated_at: '2024-02-10T14:00:00Z',
  },
  {
    id: '10',
    owner_id: '2',
    isbn: '978-83-7432-456-7',
    title: 'Solaris',
    author: 'Stanisław Lem',
    description: 'Science fiction o kontakcie z inteligentnym oceanem na odległej planecie.',
    cover_url: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=600&fit=crop',
    genre: 'Science Fiction',
    page_count: 224,
    published_date: '1961',
    status: 'borrowed',
    is_lendable: true,
    publisher: 'Wydawnictwo Literackie',
    publication_year: 1961,
    created_at: '2024-03-01T11:20:00Z',
    updated_at: '2024-03-05T16:30:00Z',
  },
  {
    id: '11',
    owner_id: '3',
    isbn: '978-83-080-9876-5',
    title: 'Lalka',
    author: 'Bolesław Prus',
    description: 'Powieść o miłości Stanisława Wokulskiego do Izabeli Łęckiej i obyczajach XIX-wiecznej Warszawy.',
    cover_url: 'https://images.unsplash.com/photo-1524578271613-d550eacf6090?w=400&h=600&fit=crop',
    genre: 'Klasyka',
    page_count: 640,
    published_date: '1890',
    status: 'available',
    is_lendable: true,
    publisher: 'Wydawnictwo Książkowe',
    publication_year: 1890,
    created_at: '2024-01-25T09:15:00Z',
    updated_at: '2024-01-25T09:15:00Z',
  },
  {
    id: '12',
    owner_id: '1',
    isbn: '978-83-7432-789-0',
    title: 'Gra o tron',
    author: 'George R.R. Martin',
    description: 'Pierwszy tom epickiej sagi fantasy o walce o Żelazny Tron Siedmiu Królestw.',
    cover_url: 'https://images.unsplash.com/photo-1535905557558-afc4877a26fc?w=400&h=600&fit=crop',
    genre: 'Fantasy',
    page_count: 864,
    published_date: '1996',
    status: 'reserved',
    is_lendable: true,
    publisher: 'Zysk i S-ka',
    publication_year: 1996,
    created_at: '2024-03-10T13:45:00Z',
    updated_at: '2024-03-14T10:00:00Z',
  },
];

// Mock loans
export const mockLoans: Loan[] = [
  {
    id: '1',
    book_id: '2',
    owner_id: '1',
    borrower_id: '2',
    status: 'active',
    borrowed_at: '2024-03-10T09:15:00Z',
    due_date: '2024-04-10T09:15:00Z',
    created_at: '2024-03-10T09:15:00Z',
  },
  {
    id: '2',
    book_id: '10',
    owner_id: '2',
    borrower_id: '3',
    status: 'active',
    borrowed_at: '2024-03-05T16:30:00Z',
    due_date: '2024-04-05T16:30:00Z',
    created_at: '2024-03-05T16:30:00Z',
  },
  {
    id: '3',
    book_id: '5',
    owner_id: '3',
    borrower_id: '1',
    status: 'returned',
    borrowed_at: '2024-02-01T10:00:00Z',
    due_date: '2024-03-01T10:00:00Z',
    returned_at: '2024-02-25T14:20:00Z',
    created_at: '2024-02-01T10:00:00Z',
  },
];

// Mock chat messages
export const mockChatMessages: ChatMessage[] = [
  {
    id: '1',
    role: 'assistant',
    content: 'Cześć! Jestem Twoim AI bibliotekarzem. Powiedz mi, jaki masz nastrój lub czego szukasz, a polecę Ci coś z biblioteczki! 📚',
    created_at: '2024-03-15T10:00:00Z',
  },
];

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

// Helper functions
export function getBookById(id: string): Book | undefined {
  return mockBooks.find(book => book.id === id);
}

export function getBooksByOwner(ownerId: string): Book[] {
  return mockBooks.filter(book => book.owner_id === ownerId);
}

export function getAvailableBooks(): Book[] {
  return mockBooks.filter(book => book.status === 'available');
}

export function getUserById(id: string): User | undefined {
  return mockUsers.find(user => user.id === id);
}

export function getLoansByUser(userId: string): Loan[] {
  return mockLoans.filter(
    loan => loan.owner_id === userId || loan.borrower_id === userId
  );
}

export function getBorrowedBooksByUser(userId: string): Loan[] {
  return mockLoans.filter(
    loan => loan.borrower_id === userId && loan.status === 'active'
  );
}
