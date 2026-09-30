"""Structured JSON Logging for Cloud Logging compliance (Criterion #13).

Configures structlog to emit machine-readable JSON records with bound execution context
(run_id, account_id, agent_name, candidate_model, case_id, tokens), replacing raw prints.
"""

import logging
import sys
from typing import Any
import structlog


def configure_structured_logging(log_level: str = "INFO") -> None:
    """Configures global structured logging to emit JSON lines to standard output.

    Args:
        log_level: Logging threshold (DEBUG, INFO, WARNING, ERROR). Defaults to INFO.
    """
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "bakeoff", **initial_context: Any) -> structlog.BoundLogger:
    """Returns a bound structlog logger with contextual key-value pairs attached.

    Args:
        name: Logger name component.
        **initial_context: Key-value metadata (e.g. run_id='RUN_123', account_id='okta').

    Returns:
        Structured bound logger.
    """
    base_logger = structlog.get_logger(name)
    if initial_context:
        return base_logger.bind(**initial_context)
    return base_logger
