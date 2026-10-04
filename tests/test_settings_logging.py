import json
import logging

from vantawave.core.logging.json_logger import JsonFormatter
from vantawave.core.settings import load_settings


def test_settings_from_environment(monkeypatch):
    monkeypatch.setenv("VANTAWAVE_ENV", "test")
    monkeypatch.setenv("VANTAWAVE_PORT", "9999")
    monkeypatch.setenv("VANTAWAVE_READINESS_REQUIRES_DATABASE", "true")
    monkeypatch.setenv("VANTAWAVE_ALLOW_LOCAL_CREDENTIAL_VIEW", "true")

    settings = load_settings()
    assert settings.environment == "test"
    assert settings.port == 9999
    assert settings.readiness_requires_database is True
    assert settings.allow_local_credential_view is True


def test_json_formatter_emits_structured_payload():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="vantawave.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    record.component = "test-component"
    payload = json.loads(formatter.format(record))
    assert payload["message"] == "hello"
    assert payload["component"] == "test-component"
