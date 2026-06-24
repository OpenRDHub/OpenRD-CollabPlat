from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: str = "OK"
    message: str = "success"
    data: T | None = None


class PaginatedData(BaseModel, Generic[T]):
    items: list[T] = []
    page: int = 1
    page_size: int = 20
    total: int = 0


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
