import contextvars

trace_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("trace_id", default=None)


def get_trace_id() -> str:
    return trace_id_var.get() or "-"


def set_trace_id(trace_id: str) -> None:
    trace_id_var.set(trace_id)


def clear_trace_id() -> None:
    trace_id_var.set(None)
