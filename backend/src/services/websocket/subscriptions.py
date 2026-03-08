import asyncio
from typing import Dict, Set, List
from fastapi import WebSocket


class SubscriptionManager:
    def __init__(self):
        self._book_subscribers: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, book_id: str, websocket: WebSocket) -> bool:
        async with self._lock:
            if book_id not in self._book_subscribers:
                self._book_subscribers[book_id] = set()
            if websocket in self._book_subscribers[book_id]:
                return False
            self._book_subscribers[book_id].add(websocket)
            return True

    async def unsubscribe(self, book_id: str, websocket: WebSocket) -> bool:
        async with self._lock:
            if book_id not in self._book_subscribers:
                return False
            if websocket not in self._book_subscribers[book_id]:
                return False
            self._book_subscribers[book_id].discard(websocket)
            if not self._book_subscribers[book_id]:
                del self._book_subscribers[book_id]
            return True

    def unsubscribe_all(self, websocket: WebSocket) -> List[str]:
        books = []
        for book_id, connections in list(self._book_subscribers.items()):
            if websocket in connections:
                connections.discard(websocket)
                books.append(book_id)
                if not connections:
                    del self._book_subscribers[book_id]
        return books

    def get_subscribers(self, book_id: str) -> List[WebSocket]:
        return list(self._book_subscribers.get(book_id, []))

    def get_stats(self) -> dict:
        return {
            "subscribed_books": len(self._book_subscribers),
            "total_subscriptions": sum(len(s) for s in self._book_subscribers.values()),
        }
