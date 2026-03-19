# 📚 ShareBook

Aplikacja webowa do wymiany książek między użytkownikami. ShareBook umożliwia przeglądanie katalogu książek, wypożyczanie ich od innych użytkowników, zarządzanie własną biblioteką oraz korzystanie z asystenta AI do odkrywania nowych tytułów.

## ✨ Funkcjonalności

### 🔐 Autentykacja i autoryzacja
- Rejestracja i logowanie użytkowników
- Bezpieczne hasła z walidacją siły (zxcvbn)
- Tokeny JWT z mechanizmem odświeżania
- Rate limiting dla prób logowania

### 📖 Katalog książek
- Przeglądanie dostępnych książek w systemie
- Szczegółowe informacje o każdym tytule
- Okładki książek (pobierane z Google Books lub generowane przez AI)
- Wyszukiwanie i filtrowanie

### 🏠 Biblioteka użytkownika
- Dodawanie własnych książek do systemu
- Zarządzanie własnymi pozycjami (dostępność, stan)
- Przeglądanie książek wypożyczonych i pożyczonych

### 🔄 System wypożyczeń
- Wysyłanie próśb o wypożyczenie książki
- Akceptowanie/odrzucanie próśb przez właścicieli
- Śledzenie statusu wypożyczeń
- System wiadomości między użytkownikami

### 🤖 Asystent AI (RAG)
- Chatbot oparty na Retrieval-Augmented Generation
- Pomaga w odkrywaniu książek na podstawie opisów
- Integracja z OpenAI API oraz Moonshot API
- Wektoryzacja bazy wiedzy (pgvector)

### 🛠️ Panel administracyjny
- Zarządzanie użytkownikami (banowanie, nadawanie uprawnień)
- Zarządzanie książkami w systemie
- Podgląd statystyk platformy

## 🛠️ Technologie

### Backend
- **Python 3.11+** z **FastAPI**
- **PostgreSQL 15+** z rozszerzeniem **pgvector**
- **SQLAlchemy 2.0** (async)
- **Pydantic** dla walidacji danych
- **JWT** dla autentykacji
- **OpenAI API / Moonshot API** dla funkcji AI

### Frontend
- **React 19** z **TypeScript**
- **Vite** jako bundler
- **Tailwind CSS** + **shadcn/ui** dla styli
- **TanStack Query** dla zarządzania stanem serwera
- **React Router** dla nawigacji
- **Zustand** dla zarządzania stanem lokalnym
- **React Hook Form** + **Zod** dla formularzy

## 🚀 Instalacja i uruchomienie

### Wymagania
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+ z pgvector
- Docker (opcjonalnie, dla bazy danych)

### 1. Klonowanie repozytorium

```bash
git clone <repo-url>
cd sharebook
```

### 2. Konfiguracja środowiska

Skopiuj plik `.env.example` do `.env` i uzupełnij zmienne:

```bash
cp .env.example .env
```

Najważniejsze zmienne do skonfigurowania:
- `DATABASE_URL` - połączenie z PostgreSQL
- `SECRET_KEY` - klucz do podpisywania tokenów JWT
- `OPENAI_API_KEY` - klucz API OpenAI (opcjonalnie, dla chatbota)
- `MOONSHOT_API_KEY` - klucz API Moonshot (alternatywny model AI)

### 3. Baza danych (Docker)

```bash
docker run -d \
  --name sharebook-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=sharebook \
  -p 5433:5432 \
  ankane/pgvector:latest
```

### 4. Backend

```bash
# Tworzenie środowiska wirtualnego
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instalacja zależności
pip install -r requirements.txt

# Uruchomienie serwera
uvicorn backend.src.main:app --reload --port 8000
```

API będzie dostępne pod `http://localhost:8000`
Dokumentacja Swagger: `http://localhost:8000/docs`

### 5. Frontend

```bash
cd frontend

# Instalacja zależności
npm install

# Uruchomienie serwera deweloperskiego
npm run dev
```

Frontend będzie dostępny pod `http://localhost:5173`

## 🧪 Testy

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

## 📁 Struktura projektu

```
sharebook/
├── backend/
│   ├── src/
│   │   ├── api/v1/endpoints/    # Endpointy API
│   │   ├── services/            # Logika biznesowa
│   │   ├── schemas/             # Pydantic models
│   │   ├── core/                # Bezpieczeństwo, wyjątki
│   │   └── main.py              # Punkt wejścia aplikacji
│   ├── database/
│   │   ├── models.py            # Modele SQLAlchemy
│   │   └── repositories/        # Warstwa dostępu do danych
│   └── tests/                   # Testy
├── frontend/
│   ├── src/
│   │   ├── components/          # Komponenty React
│   │   ├── pages/               # Strony aplikacji
│   │   ├── hooks/               # Custom hooks
│   │   ├── lib/                 # Narzędzia, API client
│   │   └── store/               # Zustand stores
│   └── tests/                   # Testy
└── logs/                        # Logi aplikacji
```

## 🔧 Rozwój

### Kodowanie
- Backend: `ruff` do formatowania i lintowania
- Frontend: `eslint` + `prettier`

### Pre-commit (opcjonalnie)
```bash
pip install pre-commit
pre-commit install
```

## 📄 Licencja

[MIT](LICENSE)

## 🤝 Wkład w projekt

Zachęcamy do zgłaszania issue i pull requestów!
