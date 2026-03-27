from typing import Optional, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    meta: Optional[dict] = None

    @classmethod
    def ok(cls, data: Optional[T] = None, message: Optional[str] = None, meta: Optional[dict] = None) -> "APIResponse[T]":
        return cls(success=True, data=data, message=message, meta=meta)

    @classmethod
    def error(cls, message: str, data: Optional[T] = None, meta: Optional[dict] = None) -> "APIResponse[T]":
        return cls(success=False, data=data, message=message, meta=meta)


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


def create_pagination_meta(page: int, per_page: int, total: int) -> dict:
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }
