from __future__ import annotations

import importlib
import logging
import os
from contextvars import ContextVar, Token
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI

log = logging.getLogger("perception_gap")

_INSTRUMENTED: bool = False
_FILTER_ATTACHED: bool = False
_LOGGING_INSTRUMENTED: bool = False

try:  # pragma: no cover - optional dependency
    from opentelemetry import trace as otel_trace  # type: ignore[import]
except ImportError:  # pragma: no cover - optional dependency
    otel_trace = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    from opentelemetry.instrumentation.logging import (  # type: ignore[import]
        LoggingInstrumentor,
    )
except ImportError:  # pragma: no cover - optional dependency
    LoggingInstrumentor = None  # type: ignore[assignment]

_REQUEST_ID_CTX: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def bind_request_id(request_id: Optional[str]) -> Token:
    """Bind the request identifier to a context variable for logging."""

    return _REQUEST_ID_CTX.set(request_id)


def reset_request_id(token: Token) -> None:
    """Restore the previous request identifier context."""

    try:
        _REQUEST_ID_CTX.reset(token)
    except LookupError:  # pragma: no cover - defensive reset
        _REQUEST_ID_CTX.set(None)


class RequestContextFilter(logging.Filter):
    """Inject request identifiers and tracing scope into log records."""

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - trivial
        request_id = _REQUEST_ID_CTX.get()
        record.request_id = request_id

        if otel_trace is not None:
            span = otel_trace.get_current_span()
            context = span.get_span_context() if span else None
            if context and context.trace_id:
                record.trace_id = f"{context.trace_id:032x}"
                record.span_id = f"{context.span_id:016x}"
            else:
                record.trace_id = None
                record.span_id = None
        else:
            record.trace_id = None
            record.span_id = None

        return True


def configure_observability(app: FastAPI) -> bool:
    """Attach OpenTelemetry instrumentation if the SDK is available."""

    _install_logging_filter()

    global _INSTRUMENTED
    if _INSTRUMENTED:
        return True

    try:
        from opentelemetry.instrumentation.fastapi import (  # type: ignore[import]
            FastAPIInstrumentor,
        )
        from opentelemetry.sdk.resources import Resource  # type: ignore[import]
        from opentelemetry.sdk.trace import TracerProvider  # type: ignore[import]
        from opentelemetry.sdk.trace.export import (  # type: ignore[import]
            BatchSpanProcessor,
            ConsoleSpanExporter,
        )
    except ImportError:
        log.info("OpenTelemetry not installed; skipping instrumentation")
        return False

    exporter = _configure_exporter()
    resource = Resource.create(
        {
            "service.name": os.getenv("OTEL_SERVICE_NAME", "360me-perception-gap"),
            "service.version": os.getenv("OTEL_SERVICE_VERSION", "0.9.0"),
            "service.namespace": os.getenv("OTEL_SERVICE_NAMESPACE", "mbti-arcade"),
            "service.instance.id": os.getenv(
                "OTEL_SERVICE_INSTANCE_ID", os.getenv("HOSTNAME", str(uuid4()))
            ),
        }
    )

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    otel_trace.set_tracer_provider(provider)  # type: ignore[union-attr]

    FastAPIInstrumentor().instrument_app(app, tracer_provider=provider)
    _instrument_application_logging()

    _INSTRUMENTED = True
    log.info("OpenTelemetry instrumentation enabled", extra={"otel_enabled": True})
    return True


def _install_logging_filter() -> None:
    global _FILTER_ATTACHED
    if _FILTER_ATTACHED:
        return

    logging.getLogger().addFilter(RequestContextFilter())
    _FILTER_ATTACHED = True


def _instrument_application_logging() -> None:
    global _LOGGING_INSTRUMENTED
    if _LOGGING_INSTRUMENTED or LoggingInstrumentor is None:
        return

    try:  # pragma: no cover - requires optional dependency
        LoggingInstrumentor().instrument(set_logging_format=False)
        _LOGGING_INSTRUMENTED = True
    except Exception:  # pragma: no cover - best effort
        log.debug("Failed to instrument logging", exc_info=True)


def _configure_exporter():  # pragma: no cover - importer resolution is trivial
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint:
        try:
            otlp_trace_exporter = importlib.import_module(
                "opentelemetry.exporter.otlp.proto.http.trace_exporter"
            )

            headers = _parse_otlp_headers(os.getenv("OTEL_EXPORTER_OTLP_HEADERS"))
            timeout = _parse_float(os.getenv("OTEL_EXPORTER_OTLP_TIMEOUT", ""))

            kwargs: dict[str, object] = {"endpoint": endpoint}
            if headers:
                kwargs["headers"] = headers
            if timeout is not None:
                kwargs["timeout"] = timeout
            return otlp_trace_exporter.OTLPSpanExporter(**kwargs)
        except ImportError:
            log.warning("OTLP exporter not available; falling back to console exporter")
    return _console_exporter()


def _parse_otlp_headers(raw: Optional[str]) -> dict[str, str]:
    if not raw:
        return {}

    headers: dict[str, str] = {}
    for item in raw.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key:
            headers[key] = value
    return headers


def _parse_float(value: str) -> Optional[float]:
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _console_exporter():  # pragma: no cover - trivial helper
    module = importlib.import_module("opentelemetry.sdk.trace.export")

    return module.ConsoleSpanExporter()
