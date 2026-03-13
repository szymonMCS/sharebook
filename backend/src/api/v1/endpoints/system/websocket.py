import asyncio
import json
import logging
from typing import Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.services.websocket import WebSocketManager

logger = logging.getLogger(__name__)

router = APIRouter()
manager = WebSocketManager()

async def _parse_message(raw_data: str) -> dict[str, Any] | None:
    try:
        return await asyncio.to_thread(json.loads, raw_data)
    except json.JSONDecodeError:
        return None


@router.websocket("/ws/book-covers")
async def book_covers_websocket(websocket: WebSocket) -> None:
    await manager.connect(websocket)

    try:
        while True:
            try:
                raw_data = await websocket.receive_text()
                data = await _parse_message(raw_data)

                if data is None:
                    await manager._broadcaster.send_personal(websocket, {"type": "error", "message": "Invalid JSON"})
                    continue

                action = data.get("action", "").lower()
                book_id = data.get("book_id")

                match action:
                    case "ping":
                        await manager.handle_ping(websocket)
                    case "subscribe":
                        await manager.handle_subscribe(book_id, websocket)
                    case "unsubscribe":
                        await manager.handle_unsubscribe(book_id, websocket)
                    case _:
                        await manager._broadcaster.send_personal(websocket, {"type": "error", "message": f"Unknown action: {action}"})
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
                break
            except asyncio.CancelledError:
                logger.info("WebSocket cancelled")
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    finally:
        await manager.disconnect(websocket)


async def notify_cover_status(book_id: str, status: str, cover_url: str | None = None) -> int:
    message = {
        "type": "cover_status",
        "book_id": book_id,
        "status": status,
    }
    if cover_url:
        message["cover_url"] = cover_url
    return await manager.broadcast_to_book(book_id, message)

async def notify_cover_updated(book_id: str, cover_url: str) -> int:
    return await manager.broadcast_to_book(book_id, {
        "type": "cover_updated",
        "book_id": book_id,
        "cover_url": cover_url,
    })

async def notify_book_enriched(book_id: str, book_data: dict) -> int:
    return await manager.broadcast_to_book(book_id, {
        "type": "book_enriched",
        "book_id": book_id,
        "book_data": book_data,
    })
