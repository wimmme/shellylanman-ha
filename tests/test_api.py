"""The REST and MCP client: ShellyLanMan's errors, the app's loopback listener."""

from __future__ import annotations

import aiohttp
import pytest

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.shellylanman.api import (
    LOCAL_URL,
    ShellyLanManAuthError,
    ShellyLanManClient,
    ShellyLanManError,
    _error_of,
)

from .conftest import URL


def test_error_of_coded() -> None:
    """ShellyLanMan 0.9.7+: {"error": {"code", "message"}}."""
    assert _error_of('{"error": {"code": "device_offline", "message": "timeout"}}') == ("device_offline", "timeout")
    assert _error_of('{"error": {"code": "internal"}}') == ("internal", "internal")  # never an empty message


def test_error_of_before_codes() -> None:
    """Up to 0.9.6 the error was a sentence; anything else is passed on as text."""
    assert _error_of('{"error": "no such device"}') == (None, "no such device")
    assert _error_of("Bad Gateway") == (None, "Bad Gateway")
    assert _error_of("[1, 2]") == (None, "[1, 2]")


async def test_rest_errors(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    client = ShellyLanManClient(async_get_clientsession(hass), URL)
    aioclient_mock.get(f"{URL}/api/v1/about", text="<html>")
    with pytest.raises(ShellyLanManError, match="not JSON"):
        await client.about()
    aioclient_mock.clear_requests()
    aioclient_mock.get(f"{URL}/api/v1/about", exc=aiohttp.ClientError("refused"))
    with pytest.raises(ShellyLanManError, match="refused"):
        await client.about()


async def test_loopback_listener(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    """The app on this host: the listener's address from the status, else the default; passwords from there."""
    local, loopback = "http://127.0.0.1:3082", "http://localhost:8197"
    client = ShellyLanManClient(async_get_clientsession(hass), local)
    aioclient_mock.get(f"{local}/api/v1/status", exc=aiohttp.ClientError())
    assert await client.local_url() == LOCAL_URL

    aioclient_mock.clear_requests()
    client = ShellyLanManClient(async_get_clientsession(hass), local)
    aioclient_mock.get(f"{local}/api/v1/status", json={"localUrl": loopback})
    aioclient_mock.get(f"{loopback}/api/v1/devices/AABBCC000001/credentials", json={"user": "admin", "password": "pw"})
    aioclient_mock.get(f"{loopback}/api/v1/devices/AABBCC000002/credentials", exc=aiohttp.ClientError())
    assert await client.credentials("AABBCC000001") == {"user": "admin", "password": "pw"}
    assert await client.credentials("AABBCC000002") is None


async def test_mcp_errors(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    client = ShellyLanManClient(async_get_clientsession(hass), URL, "tok")
    refused: list[bool] = []
    client.on_auth_error = lambda: refused.append(True)
    cases = [
        ({"status": 401}, ShellyLanManAuthError, "refused"),
        ({"status": 404}, ShellyLanManError, "switched off"),
        ({"status": 500}, ShellyLanManError, "HTTP 500"),
        ({"exc": aiohttp.ClientError("gone")}, ShellyLanManError, "gone"),
        ({"json": {"jsonrpc": "2.0", "id": 1, "error": {"code": -32601, "message": "no such method"}}}, ShellyLanManError, "no such method"),
    ]
    for answer, error, text in cases:
        aioclient_mock.clear_requests()
        aioclient_mock.post(f"{URL}/mcp", **answer)
        with pytest.raises(error, match=text):
            await client.mcp("tools/list")
    assert refused == [True]  # only the refused token asks for a new one
