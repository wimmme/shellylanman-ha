"""Config flow: by hand, from the app's discovery, reconfigure."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.hassio import HassioServiceInfo
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.shellylanman.const import CONF_MCP_TOKEN, DOMAIN

from .conftest import INSTANCE, TOOLS, URL, mock_shellylanman


async def test_user_flow(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    mock_shellylanman(aioclient_mock)
    aioclient_mock.post(f"{URL}/mcp", json={"jsonrpc": "2.0", "id": 1, "result": TOOLS})
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_URL: URL + "/", CONF_MCP_TOKEN: " tok "})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_URL: URL, CONF_MCP_TOKEN: "tok"}
    assert result["result"].unique_id == INSTANCE
    mcp_calls = [c for c in aioclient_mock.mock_calls if str(c[1]).endswith("/mcp")]
    assert mcp_calls and mcp_calls[0][3]["Authorization"] == "Bearer tok"


async def test_user_flow_errors(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    aioclient_mock.get(f"{URL}/api/v1/about", status=500)
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_URL: URL})
    assert result["errors"] == {"base": "cannot_connect"}

    aioclient_mock.clear_requests()
    aioclient_mock.get(f"{URL}/api/v1/about", json={"version": "v0.4.0"})  # no instanceId
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_URL: URL})
    assert result["errors"] == {"base": "too_old"}

    aioclient_mock.clear_requests()
    mock_shellylanman(aioclient_mock)
    aioclient_mock.post(f"{URL}/mcp", status=401)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_URL: URL, CONF_MCP_TOKEN: "bad"})
    assert result["errors"] == {"base": "invalid_token"}


async def test_hassio_discovery(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    local = "http://127.0.0.1:3082"
    mock_shellylanman(aioclient_mock, url=local)
    info = HassioServiceInfo(config={"url": local}, name="ShellyLanMan", slug="505f279b_shellylanman", uuid="u1")
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_HASSIO}, data=info)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "hassio_confirm"
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_URL: local}


async def test_hassio_discovery_updates_url(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    """The app announces itself again after a port change: the entry follows."""
    entry = MockConfigEntry(domain=DOMAIN, unique_id=INSTANCE, data={CONF_URL: "http://127.0.0.1:3082"})
    entry.add_to_hass(hass)
    new = "http://127.0.0.1:3090"
    mock_shellylanman(aioclient_mock, url=new)
    info = HassioServiceInfo(config={"url": new}, name="ShellyLanMan", slug="x_shellylanman", uuid="u1")
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_HASSIO}, data=info)
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data[CONF_URL] == new


async def test_user_flow_password(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    """A ShellyLanMan with a UI password: without a token the form asks for it; the token goes with every call."""
    aioclient_mock.get(f"{URL}/api/v1/about", status=401, json={"error": "login required"})
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_URL: URL})
    assert result["errors"] == {"base": "login_required"}

    aioclient_mock.clear_requests()
    mock_shellylanman(aioclient_mock)
    aioclient_mock.post(f"{URL}/mcp", json={"jsonrpc": "2.0", "id": 1, "result": TOOLS})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_URL: URL, CONF_MCP_TOKEN: "tok"})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    rest = [c for c in aioclient_mock.mock_calls if "/api/v1/" in str(c[1])]
    assert rest and all(c[3].get("Authorization") == "Bearer tok" for c in rest)


async def test_app_with_password_uses_loopback(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    """The app on this host with a UI password: without a token the calls go to its loopback listener."""
    local = "http://127.0.0.1:3082"
    loopback = "http://localhost:8097"  # the mocker ignores ports: another host name for the listener
    aioclient_mock.get(f"{local}/api/v1/about", status=401, json={"error": "login required"})
    mock_shellylanman(aioclient_mock, url=loopback)
    with patch("custom_components.shellylanman.api.LOCAL_URL", loopback):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_HASSIO},
            data=HassioServiceInfo(config={"url": local}, name="ShellyLanMan", slug="shellylanman", uuid="x"),
        )
    assert result["type"] is FlowResultType.FORM, result  # ShellyLanMan answered through the loopback listener
    assert any(str(c[1]).startswith(f"{loopback}/api/v1/about") for c in aioclient_mock.mock_calls)
