import logging
import logging.config
from typing import Any

from .context import clear_trace_id, get_trace_id, set_trace_id, trace_id_var
from .filters import TraceIdFilter
from .formatters import JSONFormatter


def configure_logging(log_level: str, log_format: str = "text", debug: bool = False) -> None:
    level = getattr(logging, log_level.upper(), logging.INFO)
    use_json = log_format.lower() == "json"

    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {"level": level, "handlers": ["console"]},
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | trace=%(trace_id)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {"()": "packages.logging.formatters.JSONFormatter"},
        },
        "filters": {
            "with_trace": {"()": "packages.logging.filters.TraceIdFilter"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json" if use_json else "standard",
                "filters": ["with_trace"],
                "level": level,
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["console"], "level": level, "propagate": False},
            "uvicorn.error": {"handlers": ["console"], "level": level, "propagate": False},
            "uvicorn.access": {"handlers": ["console"], "level": level, "propagate": False},
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": "INFO" if debug else "WARNING",
                "propagate": False,
            },
            "sqlalchemy.pool": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        },
    }

    logging.config.dictConfig(config)


__all__ = [
    "configure_logging",
    "JSONFormatter",
    "TraceIdFilter",
    "trace_id_var",
    "get_trace_id",
    "set_trace_id",
    "clear_trace_id",
]
