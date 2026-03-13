import logging
import time
from typing import Any
from uuid import UUID
from fastapi import WebSocket
from src.services.websocket.registry import ConnectionRegistry
from src.services.websocket.subscriptions import SubscriptionManager
from src.services.websocket.broadcaster import Broadcaster

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        self._registry = ConnectionRegistry()
        self._subscriptions = SubscriptionManager()
        self._broadcaster = Broadcaster(self._registry, self._subscriptions)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await self._registry.register(websocket)
        logger.info(f"WebSocket connected. Total: {self._registry.get_count()}")
        await self._send_welcome(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        self._subscriptions.unsubscribe_all(websocket)
        await self._registry.unregister(websocket)
        logger.info(f"WebSocket disconnected. Remaining: {self._registry.get_count()}")

    async def subscribe(self, book_id: str, websocket: WebSocket) -> bool:
        try:
            UUID(book_id)
        except (ValueError, TypeError):
            logger.warning(f"Invalid book_id: {book_id}")
            return False

        if await self._subscriptions.subscribe(book_id, websocket):
            self._registry.subscribe_to_book(websocket, book_id)
            return True
        return False

    async def unsubscribe(self, book_id: str, websocket: WebSocket) -> bool:
        if await self._subscriptions.unsubscribe(book_id, websocket):
            self._registry.unsubscribe_from_book(websocket, book_id)
            return True
        return False

    async def handle_ping(self, websocket: WebSocket) -> None:
        self._registry.update_ping(websocket)
        await self._broadcaster.send_personal(websocket, {"type": "pong", "timestamp": time.time()})

    async def handle_subscribe(self, book_id: str, websocket: WebSocket) -> None:
        if not book_id:
            await self._broadcaster.send_personal(websocket, {"type": "error", "message": "book_id required"})
            return

        if await self.subscribe(book_id, websocket):
            await self._broadcaster.send_personal(websocket, {"type": "subscribed", "book_id": book_id})
        else:
            await self._broadcaster.send_personal(websocket, {"type": "error", "message": f"Already subscribed to {book_id}"})

    async def handle_unsubscribe(self, book_id: str, websocket: WebSocket) -> None:
        if not book_id:
            await self._broadcaster.send_personal(websocket, {"type": "error", "message": "book_id required"})
            return

        if await self.unsubscribe(book_id, websocket):
            await self._broadcaster.send_personal(websocket, {"type": "unsubscribed", "book_id": book_id})
        else:
            await self._broadcaster.send_personal(websocket, {"type": "error", "message": f"Not subscribed to {book_id}"})

    async def broadcast_to_book(self, book_id: str, message: dict) -> int:
        return await self._broadcaster.broadcast_to_book(book_id, message)

    async def _send_welcome(self, websocket: WebSocket) -> None:
        stats = {
            "total_connections": self._registry.get_count(),
            **self._subscriptions.get_stats(),
        }
        await self._broadcaster.send_personal(websocket, {
            "type": "connected",
            "message": "Connected to book covers WebSocket",
            "stats": stats,
        })
