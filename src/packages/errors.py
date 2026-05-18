import logging
from typing import TYPE_CHECKING, Any

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse


HTTP_STATUS_MAP: dict[str, int] = {
    "not_found": 404,
    "unique": 409,
    "invalid_credentials": 401,
    "insufficient_permissions": 403,
}


class BaseError(Exception):
    """Transport-agnostic domain error with standardized HTTP response metadata.

    Subclass this and override code/message/status_code to define domain errors.

    Example:
        class UserNotFoundError(BaseError):
            code = "not_found"
            message = "User not found"
            status_code = 404
    """

    code: str = "invalid"
    message: str = "Validation error"
    status_code: int = 422

    def __init__(
        self,
        detail: str | None = None,
        *,
        attr: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        self.detail = detail or self.message
        self.attr = attr
        self.meta = dict(meta or {})
        super().__init__(self.detail)


def to_http_response(error: BaseError) -> "JSONResponse":
    from fastapi.responses import JSONResponse

    from presentations.api.schemas.common import ErrorItem

    status_code = HTTP_STATUS_MAP.get(error.code, error.status_code)
    item = ErrorItem(code=error.code, detail=error.detail, attr=error.attr)
    return JSONResponse(
        status_code=status_code,
        content={"message": error.message, "errors": [item.model_dump()]},
    )
