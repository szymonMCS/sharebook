import asyncio
import json
import logging
import time
from typing import Any
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []
        self.book_subscriptions: dict[str, list[WebSocket]] = {}
        self.connection_metadata: dict[WebSocket, dict[str, Any]] = {}
        self.ping_interval: int = 30 

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_metadata[websocket] = {
            "connected_at": time.time(),
            "last_ping": time.time(),
            "subscribed_books": set(),
            "client_info": websocket.client.host if websocket.client else "unknown",
        }
        logger.info(
            "WebSocket connected: %s. Total connections: %d",
            websocket.client.host if websocket.client else "unknown",
            len(self.active_connections),
        )

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        metadata = self.connection_metadata.pop(websocket, None)
        if metadata:
            subscribed_books = metadata.get("subscribed_books", set())
            for book_id in subscribed_books:
                self._unsubscribe_from_book_internal(book_id, websocket)

        for book_id, connections in list(self.book_subscriptions.items()):
            if websocket in connections:
                connections.remove(websocket)
                if not connections:
                    del self.book_subscriptions[book_id]

        logger.info("WebSocket disconnected. Remaining connections: %d", len(self.active_connections),)

    def subscribe_to_book(self, book_id: str, websocket: WebSocket) -> bool:
        try:
            UUID(book_id)
        except (ValueError, TypeError):
            logger.warning("Invalid book_id format for subscription: %s", book_id)
            return False

        if book_id not in self.book_subscriptions:
            self.book_subscriptions[book_id] = []

        if websocket not in self.book_subscriptions[book_id]:
            self.book_subscriptions[book_id].append(websocket)

            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["subscribed_books"].add(book_id)

            logger.debug(
                "Subscribed connection to book %s. Total subscribers: %d",
                book_id,
                len(self.book_subscriptions[book_id]),
            )
            return True
        return False

    def unsubscribe_from_book(self, book_id: str, websocket: WebSocket) -> bool:
        try:
            UUID(book_id)
        except (ValueError, TypeError):
            logger.warning("Invalid book_id format for unsubscription: %s", book_id)
            return False

        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]["subscribed_books"].discard(book_id)

        return self._unsubscribe_from_book_internal(book_id, websocket)

    def _unsubscribe_from_book_internal(self, book_id: str, websocket: WebSocket) -> bool:
        if book_id in self.book_subscriptions:
            if websocket in self.book_subscriptions[book_id]:
                self.book_subscriptions[book_id].remove(websocket)
                if not self.book_subscriptions[book_id]:
                    del self.book_subscriptions[book_id]
                logger.debug("Unsubscribed connection from book %s", book_id)
                return True
        return False

    async def broadcast_to_book(self, book_id: str, message: dict[str, Any]) -> int:
        if book_id not in self.book_subscriptions:
            return 0

        sent_count = 0
        disconnected: list[WebSocket] = []

        for connection in self.book_subscriptions[book_id]:
            try:
                await connection.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.warning("Failed to send message to connection: %s", e)
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

        return sent_count

    async def broadcast_to_all(self, message: dict[str, Any]) -> int:
        sent_count = 0
        disconnected: list[WebSocket] = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.warning("Failed to broadcast message: %s", e)
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

        return sent_count

    async def send_personal_message(self, message: dict[str, Any], websocket: WebSocket) -> bool:
        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.warning("Failed to send personal message: %s", e)
            self.disconnect(websocket)
            return False

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_connections": len(self.active_connections),
            "total_subscriptions": sum(len(subs) for subs in self.book_subscriptions.values()),
            "subscribed_books": len(self.book_subscriptions),
        }

    async def handle_ping(self, websocket: WebSocket) -> None:
        await self.send_personal_message({"type": "pong", "timestamp": time.time()}, websocket,)
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]["last_ping"] = time.time()

    async def handle_stats(self, websocket: WebSocket) -> None:
        await self.send_personal_message({"type": "stats", "data": self.get_stats()}, websocket,)

    async def handle_subscribe(self, book_id: str | None, websocket: WebSocket) -> None:
        if not book_id:
            await self.send_personal_message({"type": "error", "message": "book_id is required for subscribe action"}, websocket,)
            return

        if self.subscribe_to_book(book_id, websocket):
            await self.send_personal_message({"type": "subscribed", "book_id": book_id}, websocket,)
        else:
            await self.send_personal_message({"type": "error", "message": f"Failed to subscribe to book {book_id}"}, websocket,)

    async def handle_unsubscribe(self, book_id: str | None, websocket: WebSocket) -> None:
        if not book_id:
            await self.send_personal_message({"type": "error", "message": "book_id is required for unsubscribe action"}, websocket,)
            return

        if self.unsubscribe_from_book(book_id, websocket):
            await self.send_personal_message({"type": "unsubscribed", "book_id": book_id}, websocket,)
        else:
            await self.send_personal_message({"type": "error", "message": f"Not subscribed to book {book_id}"}, websocket,)

    async def handle_unknown_action(self, action: str, websocket: WebSocket) -> None:
        await self.send_personal_message(
            {
                "type": "error",
                "message": f"Unknown action: {action}. Supported: subscribe, unsubscribe, ping, stats",
            },
            websocket,
        )

    async def send_welcome_message(self, websocket: WebSocket) -> None:
        await self.send_personal_message(
            {
                "type": "connected",
                "message": "Connected to book covers WebSocket",
                "stats": self.get_stats(),
            },
            websocket,
        )

manager = ConnectionManager()

async def _parse_message(raw_data: str) -> dict[str, Any] | None:
    try:
        return await asyncio.to_thread(json.loads, raw_data)
    except json.JSONDecodeError:
        return None

@router.websocket("/ws/book-covers")
async def book_covers_websocket(websocket: WebSocket) -> None:
    await manager.connect(websocket)

    try:
        await manager.send_welcome_message(websocket)

        while True:
            try:
                raw_data = await websocket.receive_text()
                logger.debug("Received WebSocket message: %s", raw_data)

                data = await _parse_message(raw_data)
                if data is None:
                    await manager.send_personal_message({"type": "error", "message": "Invalid message format"},websocket,)
                    continue

                action = data.get("action", "").lower()
                book_id = data.get("book_id")

                match action:
                    case "ping":
                        await manager.handle_ping(websocket)
                    case "stats":
                        await manager.handle_stats(websocket)
                    case "subscribe":
                        await manager.handle_subscribe(book_id, websocket)
                    case "unsubscribe":
                        await manager.handle_unsubscribe(book_id, websocket)
                    case _:
                        await manager.handle_unknown_action(action, websocket)

            except WebSocketDisconnect:
                logger.info("WebSocket disconnected normally")
                break
            except asyncio.CancelledError:
                logger.info("WebSocket connection cancelled")
                break
            except Exception as e:
                logger.error("Error handling WebSocket message: %s", e)
                try:
                    await manager.send_personal_message({"type": "error", "message": f"Internal error: {e!s}"}, websocket,)
                except Exception: 
                    break

    except Exception as e: 
        logger.error("WebSocket connection error: %s", e)
    finally:
        manager.disconnect(websocket)

async def notify_cover_updated(book_id: str, cover_url: str) -> int:
    message = {
        "type": "cover_updated",
        "book_id": book_id,
        "cover_url": cover_url,
    }

    return await manager.broadcast_to_book(book_id, message)

def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    return manager
