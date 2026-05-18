import logging

from .context import get_trace_id


class TraceIdFilter(logging.Filter):
    """Injects trace_id into every log record so %(trace_id)s is always available."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "trace_id"):
            record.trace_id = get_trace_id()
        return True
