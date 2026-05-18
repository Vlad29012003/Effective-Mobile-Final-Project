import json
import logging
from datetime import UTC, datetime


class JSONFormatter(logging.Formatter):
    """Structured JSON formatter for non-local environments."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "trace_id"):
            entry["trace_id"] = record.trace_id
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry)
