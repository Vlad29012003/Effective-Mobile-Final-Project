import logging
from collections.abc import Mapping, Sequence
from typing import Any, cast

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from packages.errors import BaseError, to_http_response
from presentations.api.schemas.common import ErrorItem

logger = logging.getLogger(__name__)

_HTTP_MESSAGES: dict[int, str] = {
    400: "Bad request",
    401: "Authentication failed",
    403: "Access denied",
    404: "Resource not found",
    405: "Method not allowed",
    409: "Conflict",
    422: "Validation error",
    429: "Too many requests",
}


async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    message = _HTTP_MESSAGES.get(exc.status_code, "Request error")
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    error = ErrorItem(code=str(exc.status_code), detail=detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": message, "errors": [error.model_dump()]},
    )


def _map_error_type(error_type: str, message: str) -> str:
    et, msg = error_type.lower(), message.lower()
    if "missing" in et or "field required" in msg:
        return "required"
    if "string_too_short" in et or "min length" in msg:
        return "min_length"
    if "string_too_long" in et or "max length" in msg:
        return "max_length"
    if "greater_than" in et:
        return "min_value"
    if "less_than" in et:
        return "max_value"
    return "invalid"


def _flatten_errors(errors: Sequence[Mapping[str, Any]]) -> list[ErrorItem]:
    items: list[ErrorItem] = []
    for err in errors:
        loc = err.get("loc")
        attr = None
        if isinstance(loc, list | tuple) and loc:
            parts = [str(p) for p in loc if p not in ("body", "query", "path", "header")]
            attr = ".".join(parts) or None
        msg = str(err.get("msg") or "Invalid value")
        code = _map_error_type(str(err.get("type") or ""), msg)
        items.append(ErrorItem(code=code, detail=msg, attr=attr))
    return items


async def handle_validation_error(
    request: Request, exc: RequestValidationError | ValidationError
) -> JSONResponse:
    errors = _flatten_errors(cast(Sequence[Mapping[str, Any]], exc.errors()))
    return JSONResponse(
        status_code=422,
        content={"message": "Validation error", "errors": [e.model_dump() for e in errors]},
    )


async def handle_base_error(request: Request, exc: BaseError) -> JSONResponse:
    return to_http_response(exc)


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception")
    error = ErrorItem(code="internal_error", detail="Internal server error")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "errors": [error.model_dump()]},
    )


def get_exception_handlers() -> Mapping[type[Exception], Any]:
    return {
        HTTPException: handle_http_exception,
        RequestValidationError: handle_validation_error,
        ValidationError: handle_validation_error,
        BaseError: handle_base_error,
        Exception: handle_unexpected_error,
    }
