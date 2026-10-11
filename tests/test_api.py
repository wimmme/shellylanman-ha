"""The REST client's reading of ShellyLanMan's errors."""

from __future__ import annotations

from custom_components.shellylanman.api import _error_of


def test_error_of_coded() -> None:
    """ShellyLanMan 0.9.7+: {"error": {"code", "message"}}."""
    assert _error_of('{"error": {"code": "device_offline", "message": "timeout"}}') == ("device_offline", "timeout")
    assert _error_of('{"error": {"code": "internal"}}') == ("internal", "internal")  # never an empty message


def test_error_of_before_codes() -> None:
    """Up to 0.9.6 the error was a sentence; anything else is passed on as text."""
    assert _error_of('{"error": "no such device"}') == (None, "no such device")
    assert _error_of("Bad Gateway") == (None, "Bad Gateway")
    assert _error_of("[1, 2]") == (None, "[1, 2]")
