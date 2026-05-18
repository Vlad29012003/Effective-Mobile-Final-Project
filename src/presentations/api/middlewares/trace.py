import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from packages.logging import clear_trace_id, set_trace_id


class TraceIdMiddleware(BaseHTTPMiddleware):
    """Attaches a request trace ID to logs and response headers."""

    DEFAULT_HEADER = "X-Request-ID"

    def __init__(
        self,
        app: ASGIApp,
        *,
        inbound_header: str | None = None,
        outbound_header: str | None = None,
    ) -> None:
        super().__init__(app)
        self.inbound_header = inbound_header or self.DEFAULT_HEADER
        self.outbound_header = outbound_header or self.inbound_header

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        trace_id = request.headers.get(self.inbound_header) or uuid.uuid4().hex
        set_trace_id(trace_id)
        try:
            response = await call_next(request)
        finally:
            clear_trace_id()

        response.headers[self.outbound_header] = trace_id

        exposed = response.headers.get("Access-Control-Expose-Headers", "")
        exposed_set = {h.strip() for h in exposed.split(",") if h.strip()}
        if self.outbound_header not in exposed_set:
            exposed_set.add(self.outbound_header)
            response.headers["Access-Control-Expose-Headers"] = ", ".join(sorted(exposed_set))

        return response
