import logging
from typing import Any, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class Broadcaster:
    def __init__(self, registry, subscriptions):
        self._registry = registry
        self._subscriptions = subscriptions

    async def send_personal(self, websocket: WebSocket, message: dict) -> bool:
        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.warning(f"Failed to send personal message: {e}")
            return False

    async def broadcast_to_book(self, book_id: str, message: dict) -> int:
        subscribers = self._subscriptions.get_subscribers(book_id)
        if not subscribers:
            return 0

        sent = 0
        disconnected = []

        for ws in subscribers:
            try:
                await ws.send_json(message)
                sent += 1
            except Exception as e:
                logger.warning(f"Failed to send to subscriber: {e}")
                disconnected.append(ws)

        for ws in disconnected:
            await self._registry.unregister(ws)
            self._subscriptions.unsubscribe_all(ws)

        return sent

    async def broadcast_to_all(self, message: dict) -> int:
        connections = self._registry.get_all_connections()
        sent = 0
        disconnected = []

        for ws in connections:
            try:
                await ws.send_json(message)
                sent += 1
            except Exception as e:
                logger.warning(f"Failed to broadcast: {e}")
                disconnected.append(ws)

        for ws in disconnected:
            await self._registry.unregister(ws)
            self._subscriptions.unsubscribe_all(ws)

        return sent
