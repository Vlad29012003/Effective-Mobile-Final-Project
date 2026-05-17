from collections.abc import Sequence

from fastapi import Request
from pydantic import BaseModel, Field


class ErrorItem(BaseModel):
    code: str
    detail: str
    attr: str | None = None


class ErrorResponse(BaseModel):
    message: str
    errors: list[ErrorItem]


class PaginationParams(BaseModel):
    page: int
    page_size: int
    sort: str | None = Field(
        default=None,
        description=(
            "Sort order. Separate fields with commas (e.g. `-created_at,name`). "
            "Prefix with `-` for descending or use `field:asc` / `field:desc` syntax."
        ),
        examples=["name", "-created_at", "name:asc,created_at:desc"],
    )


class PaginatedResponse[T](BaseModel):
    count: int
    total_pages: int
    next: str | None
    previous: str | None
    results: Sequence[T]

    @classmethod
    def from_request(
        cls,
        request: Request,
        *,
        results: Sequence[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

        def url_for(p: int) -> str:
            q = dict(request.query_params)
            q["page"] = str(p)
            return str(request.url.replace_query_params(**q))

        next_url = url_for(page + 1) if page < total_pages else None
        prev_url = url_for(page - 1) if page > 1 and total_pages > 0 else None
        return cls(
            count=total,
            total_pages=total_pages,
            next=next_url,
            previous=prev_url,
            results=list(results),
        )
