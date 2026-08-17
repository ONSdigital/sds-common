"""Tests for GCP logging configuration helpers."""
import json
import logging

import pytest

from sds_common.config.logging_config import GcpJsonFormatter, configure_gcp_logging, get_log_level


class TestGetLogLevel:
    def test_returns_info_by_default(self, monkeypatch):
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        assert get_log_level() == logging.INFO

    def test_returns_debug_when_set(self, monkeypatch):
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        assert get_log_level() == logging.DEBUG

    def test_returns_warning_when_set(self, monkeypatch):
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        assert get_log_level() == logging.WARNING


class TestGcpJsonFormatter:
    def _make_record(self, msg="test message", level=logging.INFO, exc_info=None):
        record = logging.LogRecord(
            name="test.logger",
            level=level,
            pathname="",
            lineno=0,
            msg=msg,
            args=(),
            exc_info=exc_info,
        )
        return record

    def test_outputs_valid_json(self):
        formatter = GcpJsonFormatter()
        output = formatter.format(self._make_record())
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_severity_field_matches_level(self):
        formatter = GcpJsonFormatter()
        output = json.loads(formatter.format(self._make_record(level=logging.WARNING)))
        assert output["severity"] == "WARNING"

    def test_message_field_is_present(self):
        formatter = GcpJsonFormatter()
        output = json.loads(formatter.format(self._make_record(msg="hello world")))
        assert output["message"] == "hello world"

    def test_logger_field_is_present(self):
        formatter = GcpJsonFormatter()
        output = json.loads(formatter.format(self._make_record()))
        assert output["logger"] == "test.logger"

    def test_traceback_included_when_exc_info_present(self):
        formatter = GcpJsonFormatter()
        try:
            raise ValueError("boom")
        except ValueError:
            import sys
            record = self._make_record(exc_info=sys.exc_info())
        output = json.loads(formatter.format(record))
        assert "traceback" in output
        assert "ValueError" in output["traceback"]

    def test_no_traceback_field_without_exception(self):
        formatter = GcpJsonFormatter()
        output = json.loads(formatter.format(self._make_record()))
        assert "traceback" not in output


class TestConfigureGcpLogging:
    def test_sets_json_formatter_on_root_logger(self):
        configure_gcp_logging()
        root = logging.getLogger()
        assert any(isinstance(h.formatter, GcpJsonFormatter) for h in root.handlers)

    def test_uses_default_log_level(self, monkeypatch):
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        configure_gcp_logging()
        assert logging.getLogger().level == logging.INFO

    def test_accepts_explicit_level(self):
        configure_gcp_logging(level=logging.DEBUG)
        assert logging.getLogger().level == logging.DEBUG

    def test_log_output_is_valid_json(self, capfd):
        configure_gcp_logging(level=logging.DEBUG)
        logging.getLogger("test.output").warning("test warning message")
        captured = capfd.readouterr()
        parsed = json.loads(captured.err)
        assert parsed["severity"] == "WARNING"
        assert parsed["message"] == "test warning message"
