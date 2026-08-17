import json
import logging
import os


def get_log_level() -> int:
    """
    Get the logging level from the LOG_LEVEL environment variable, or use the default value of INFO.

    :return int: logging level
    """
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    return getattr(logging, log_level)


class GcpJsonFormatter(logging.Formatter):
    """
    Formats log records as single-line JSON objects compatible with Google Cloud Logging.

    GCP parses the ``severity`` field to set the log level in Cloud Logging,
    enabling correct colouring, filtering, and alerting in the console.
    Exception tracebacks are included under ``traceback`` when present.
    Stack traces (from ``stack_info=True``) are included under ``stackTrace``.
    """

    def format(self, record: logging.LogRecord) -> str:
        entry: dict = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            entry["traceback"] = self.formatException(record.exc_info)
        if record.stack_info:
            entry["stackTrace"] = self.formatStack(record.stack_info)
        return json.dumps(entry)


def configure_gcp_logging(level: int | None = None) -> None:
    """
    Configure the root logger to emit JSON-structured logs for Google Cloud Logging.

    Call this once at application startup (e.g. in ``main.py`` or your Cloud Function
    entry point). All subsequent log calls — from ``sds-common`` and from your own code
    — will be formatted as structured JSON that GCP can parse correctly, giving you
    proper severity levels, filtering, and alerting in Cloud Logging.

    :param level: Optional log level (e.g. ``logging.DEBUG``). Defaults to the value
                  of the ``LOG_LEVEL`` environment variable, or ``INFO`` if not set.

    Example::

        from sds_common.config.logging_config import configure_gcp_logging
        configure_gcp_logging()
    """
    handler = logging.StreamHandler()
    handler.setFormatter(GcpJsonFormatter())
    logging.basicConfig(
        handlers=[handler],
        level=level if level is not None else get_log_level(),
        force=True,
    )
