import { useState, useEffect, useRef, useCallback } from 'react';

// Types for WebSocket messages
interface SubscribeMessage {
  action: 'subscribe';
  book_id: string;
}

interface UnsubscribeMessage {
  action: 'unsubscribe';
  book_id: string;
}

interface CoverUpdatedMessage {
  type: 'cover_updated';
  book_id: string;
  cover_url: string;
}

interface BookEnrichedMessage {
  type: 'book_enriched';
  book_id: string;
  book_data: {
    title?: string;
    author?: string;
    description?: string;
    [key: string]: any;
  };
}

type WebSocketMessage = SubscribeMessage | UnsubscribeMessage | CoverUpdatedMessage | BookEnrichedMessage;

// Hook return type
interface UseBookCoverWSReturn {
  isConnected: boolean;
  isDownloading: boolean;
  latestCoverUrl: string | null;
  bookEnriched: boolean;
  enrichedData: BookEnrichedMessage['book_data'] | null;
  error: string | null;
}

const WS_URL = 'ws://localhost:8000/api/v1/ws/book-covers';
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY_MS = 3000;

/**
 * Hook do obsługi WebSocket dla aktualizacji okładek książek.
 * 
 * @param bookId - ID książki do subskrypcji
 * @returns Obiekt ze stanem połączenia i aktualnym URL okładki
 * 
 * @example
 * ```typescript
 * const { isConnected, isDownloading, latestCoverUrl, error } = useBookCoverWS(book.id);
 * const coverUrl = latestCoverUrl || book.cover_url;
 * ```
 */
export function useBookCoverWS(bookId: string): UseBookCoverWSReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [latestCoverUrl, setLatestCoverUrl] = useState<string | null>(null);
  const [bookEnriched, setBookEnriched] = useState(false);
  const [enrichedData, setEnrichedData] = useState<BookEnrichedMessage['book_data'] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isUnmountingRef = useRef(false);

  // Funkcja do wysyłania wiadomości przez WebSocket
  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
      console.log('[useBookCoverWS] Wysłano:', message);
    } else {
      console.warn('[useBookCoverWS] WebSocket nie jest otwarty, nie można wysłać:', message);
    }
  }, []);

  // Funkcja czyszcząca timeouty
  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  // Główna logika połączenia WebSocket
  const connect = useCallback(() => {
    if (isUnmountingRef.current) {
      console.log('[useBookCoverWS] Pominięto połączenie - komponent jest odmontowywany');
      return;
    }

    // Don't connect if bookId is empty
    if (!bookId) {
      console.log('[useBookCoverWS] Pominięto połączenie - brak bookId');
      return;
    }

    if (reconnectAttemptsRef.current >= MAX_RECONNECT_ATTEMPTS) {
      console.error('[useBookCoverWS] Osiągnięto maksymalną liczbę prób połączenia');
      setError('Nie udało się połączyć z serwerem po wielu próbach');
      return;
    }

    console.log(`[useBookCoverWS] Próba połączenia #${reconnectAttemptsRef.current + 1} dla bookId: ${bookId}`);

    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[useBookCoverWS] Połączenie otwarte');
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;

        // Wysyłamy subskrypcję po połączeniu
        sendMessage({ action: 'subscribe', book_id: bookId });
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WebSocketMessage;
          console.log('[useBookCoverWS] Otrzymano wiadomość:', data);

          if (data.type === 'cover_updated' && data.book_id === bookId) {
            console.log('[useBookCoverWS] Aktualizacja okładki:', data.cover_url);
            setLatestCoverUrl(data.cover_url);
            setIsDownloading(false);
          }
          
          if (data.type === 'book_enriched' && data.book_id === bookId) {
            console.log('[useBookCoverWS] Dane książki wzbogacone:', data.book_data);
            setBookEnriched(true);
            setEnrichedData(data.book_data);
          }
        } catch (err) {
          console.error('[useBookCoverWS] Błąd parsowania wiadomości:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('[useBookCoverWS] Błąd WebSocket:', error);
        setError('Wystąpił błąd połączenia WebSocket');
      };

      ws.onclose = (event) => {
        console.log('[useBookCoverWS] Połączenie zamknięte, kod:', event.code, 'powód:', event.reason);
        setIsConnected(false);
        wsRef.current = null;

        // Próbujemy ponownie połączyć, jeśli nie było celowego zamknięcia
        if (!isUnmountingRef.current && event.code !== 1000) {
          reconnectAttemptsRef.current += 1;
          console.log(`[useBookCoverWS] Próba ponownego połączenia za ${RECONNECT_DELAY_MS}ms (próba ${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, RECONNECT_DELAY_MS);
        }
      };
    } catch (err) {
      console.error('[useBookCoverWS] Błąd tworzenia WebSocket:', err);
      setError('Nie udało się utworzyć połączenia WebSocket');
    }
  }, [bookId, sendMessage]);

  // Efekt inicjalizujący połączenie
  useEffect(() => {
    console.log('[useBookCoverWS] Inicjalizacja hooka dla bookId:', bookId);
    isUnmountingRef.current = false;
    reconnectAttemptsRef.current = 0;

    // Symulacja stanu pobierania na początku (opcjonalnie)
    setIsDownloading(true);

    connect();

    // Cleanup przy unmount lub zmianie bookId
    return () => {
      console.log('[useBookCoverWS] Cleanup dla bookId:', bookId);
      isUnmountingRef.current = true;
      clearReconnectTimeout();

      if (wsRef.current) {
        // Wysyłamy unsubscribe przed zamknięciem
        if (wsRef.current.readyState === WebSocket.OPEN) {
          sendMessage({ action: 'unsubscribe', book_id: bookId });
          console.log('[useBookCoverWS] Wysłano unsubscribe');
        }

        wsRef.current.close(1000, 'Component unmounting');
        wsRef.current = null;
      }
    };
  }, [bookId, connect, clearReconnectTimeout, sendMessage]);

  return {
    isConnected,
    isDownloading,
    latestCoverUrl,
    bookEnriched,
    enrichedData,
    error,
  };
}

export default useBookCoverWS;
