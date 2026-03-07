import asyncio
import time
from typing import Dict, Optional, Any
from fastapi import WebSocket


class ConnectionRegistry:
    def __init__(self):
        self._connections: Dict[WebSocket, dict] = {}
        self._lock = asyncio.Lock()

    async def register(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections[websocket] = {
                "connected_at": time.time(),
                "last_ping": time.time(),
                "subscribed_books": set(),
                "client_info": websocket.client.host if websocket.client else "unknown",
            }

    async def unregister(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.pop(websocket, None)

    def get_metadata(self, websocket: WebSocket) -> Optional[dict]:
        return self._connections.get(websocket)

    def update_ping(self, websocket: WebSocket) -> None:
        if meta := self._connections.get(websocket):
            meta["last_ping"] = time.time()

    def subscribe_to_book(self, websocket: WebSocket, book_id: str) -> None:
        if meta := self._connections.get(websocket):
            meta["subscribed_books"].add(book_id)

    def unsubscribe_from_book(self, websocket: WebSocket, book_id: str) -> None:
        if meta := self._connections.get(websocket):
            meta["subscribed_books"].discard(book_id)

    def get_subscribed_books(self, websocket: WebSocket) -> set:
        if meta := self._connections.get(websocket):
            return meta["subscribed_books"]
        return set()

    def get_all_connections(self) -> list:
        return list(self._connections.keys())

    def get_count(self) -> int:
        return len(self._connections)
