# 📚 ShareBook

Aplikacja do wypożyczania książek między użytkownikami w lokalnej społeczności. Umożliwia udostępnianie własnych książek, wyszukiwanie dostępnych pozycji oraz zarządzanie wypożyczeniami.

## 🏗️ Architektura

- **Backend**: FastAPI (Python) + PostgreSQL + SQLAlchemy 2.0
- **Frontend**: React + TypeScript + Tailwind CSS + shadcn/ui
- **AI**: OpenAI API (wyszukiwanie książek, chat z asystentem)
- **Autentykacja**: JWT (access/refresh tokens) + CSRF protection

## 🚀 Uruchomienie lokalne

### Wymagania
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (z rozszerzeniem pgvector)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Skopiuj i uzupełnij zmienne środowiskowe
cp .env.example .env

# Uruchom migracje (jeśli potrzebne) i serwer
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Aplikacja będzie dostępna pod adresem `http://localhost:5173`

## 📁 Struktura projektu

```
sharebook/
├── backend/
│   ├── src/
│   │   ├── api/v1/endpoints/     # Endpointy API
│   │   ├── services/             # Logika biznesowa
│   │   │   ├── admin/           # Serwisy administracyjne
│   │   │   ├── auth/            # Autentykacja
│   │   │   ├── books/           # Książki
│   │   │   ├── loans/           # Wypożyczenia
│   │   │   └── ai/              # Integracja z AI
│   │   ├── schemas/             # Pydantic models
│   │   └── core/                # Konfiguracja, wyjątki, security
│   └── database/
│       ├── models.py            # SQLAlchemy modele
│       ├── repositories/        # Warstwa dostępu do danych
│       └── interfaces.py        # Interfejsy repozytoriów
├── frontend/
│   ├── src/
│   │   ├── api/                 # Klient API
│   │   ├── components/          # Komponenty React
│   │   ├── hooks/               # Custom hooks (React Query)
│   │   ├── pages/               # Strony aplikacji
│   │   └── types/               # TypeScript types
│   └── public/
└── venv/                        # Wirtualne środowisko
```

## ⚙️ Konfiguracja

Utwórz plik `backend/.env`:

```env
# Baza danych
DATABASE_URL=postgresql+asyncpg://user:password@localhost/sharebook

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Inne
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development
```

## 🎯 Główne funkcjonalności

### Dla użytkowników
- 🔍 Wyszukiwanie książek w katalogu społeczności
- 📖 Dodawanie własnych książek (via ISBN)
- 🔄 Wypożyczanie książek od innych użytkowników
- 💬 Komunikacja z właścicielem (chat)
- 📱 Śledzenie statusu wypożyczeń

### Dla administratorów
- 📊 Dashboard ze statystykami
- 👥 Zarządzanie użytkownikami (role, reset hasła)
- 📚 Zarządzanie katalogiem książek
- 🔧 Zarządzanie kopiami użytkowników

### AI
- 🤖 Wyszukiwanie metadanych książek (OpenAI + Google Books)
- 💬 Chatbot z bazą wiedzy o książkach (RAG)
- 🎨 Automatyczne generowanie okładek (DALL-E)

## 🔐 Autentykacja

- **Cookie-based JWT**: Access token (httpOnly, secure), Refresh token, CSRF token
- **Role**: `reader` (domyślnie), `admin`
- **Bezpieczeństwo**: Rate limiting, CSRF protection, password strength validation (zxcvbn)

## 🛣️ Główne endpointy API

### Auth
- `POST /api/v1/auth/register` - Rejestracja
- `POST /api/v1/auth/login` - Logowanie
- `POST /api/v1/auth/logout` - Wylogowanie
- `POST /api/v1/auth/refresh` - Odświeżenie tokena

### Książki
- `GET /api/v1/books` - Wyszukiwanie książek
- `GET /api/v1/books/{id}` - Szczegóły książki
- `POST /api/v1/books` - Dodanie książki (admin)
- `GET /api/v1/community/books` - Książki społeczności

### Biblioteka użytkownika
- `GET /api/v1/my-books` - Moja biblioteka
- `POST /api/v1/my-books` - Dodanie książki (ISBN)
- `PATCH /api/v1/my-books/{id}/lendable` - Zmiana statusu wypożyczania
- `PATCH /api/v1/my-books/{id}/status` - Zmiana statusu książki
- `DELETE /api/v1/my-books/{id}` - Usunięcie z biblioteki

### Wypożyczenia
- `GET /api/v1/loans` - Lista wypożyczeń
- `PATCH /api/v1/loans/{id}` - Zwrot książki
- `POST /api/v1/loan-requests` - Nowa prośba o wypożyczenie
- `GET /api/v1/loan-requests/incoming` - Przychodzące prośby
- `GET /api/v1/loan-requests/outgoing` - Wysłane prośby
- `PATCH /api/v1/loan-requests/{id}` - Akceptacja/odrzucenie

### Admin
- `GET /api/v1/admin/dashboard` - Statystyki
- `GET /api/v1/admin/users` - Lista użytkowników
- `DELETE /api/v1/admin/users/{id}` - Usunięcie użytkownika
- `GET /api/v1/admin/books` - Zarządzanie książkami
- `GET /api/v1/admin/books/user-books` - Zarządzanie kopiami

### AI
- `POST /api/v1/ai/chat` - Chat z asystentem
- `GET /api/v1/ai/health` - Status AI
- `POST /api/v1/ai/sync` - Synchronizacja wektorowej bazy

## 🧪 Testowanie

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## 🐳 Docker (opcjonalnie)

```bash
# Uruchomienie PostgreSQL z pgvector
docker run -d \
  --name sharebook-db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=sharebook \
  -p 5432:5432 \
  ankane/pgvector:latest
```

## 📄 Licencja

MIT License

## 👥 Autorzy

Projekt stworzony w celach edukacyjnych i dla lokalnych społeczności czytelniczych.
