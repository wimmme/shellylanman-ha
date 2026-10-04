"""Adding Shellys to Home Assistant's Shelly integration (ShellyLanMan DECISIONS P13-1..4).

Runs Home Assistant's real Shelly config flows; only the network is mocked
(aioshelly's get_info and the Shelly integration's validate_input) and the
Shelly entries are not set up.
"""

from __future__ import annotations

from ipaddress import ip_address
from typing import Any
from unittest.mock import patch

import pytest

from homeassistant.config_entries import SOURCE_IGNORE, SOURCE_ZEROCONF
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.shellylanman.const import DOMAIN

from .conftest import BACKUPS, CHECKLIST, INSTANCE, URL

# ShellyLanMan's view: discovered by Home Assistant (A1), missed (B2, B3 with a
# password), offline (C4), a BLU device and one Home Assistant already has (D5).
DEVICES: list[dict[str, Any]] = [
    {"id": "AABBCC0000A1", "name": "Porch", "hostname": "shellyplus1-aabbcc0000a1", "gen": "2", "ip": "192.0.2.1", "port": 80, "status": "online"},
    {"id": "AABBCC0000B2", "name": "Pump", "hostname": "shellyplug-s-AABBCC0000B2", "gen": "1", "ip": "192.0.2.2", "port": 80, "status": "online"},
    {"id": "AABBCC0000B3", "name": "Locked", "hostname": "shellyplus1-aabbcc0000b3", "gen": "3", "ip": "192.0.2.3", "port": 80, "status": "online", "protected": True},
    {"id": "AABBCC0000C4", "name": "Away", "hostname": "shellyplus1-aabbcc0000c4", "gen": "2", "ip": "192.0.2.4", "port": 80, "status": "offline"},
    {"id": "AABBCC0000E6", "name": "Door", "hostname": "sbdw-e6", "gen": "bth", "ip": "", "port": 0, "status": "online"},
    {"id": "AABBCC0000D5", "name": "Have", "hostname": "shellyplus1-aabbcc0000d5", "gen": "2", "ip": "192.0.2.5", "port": 80, "status": "online"},
]
INFO = {  # GET /shelly per address
    "192.0.2.1": {"mac": "AABBCC0000A1", "gen": 2, "model": "SNSW-001X16EU", "auth_en": False},
    "192.0.2.2": {"mac": "AABBCC0000B2", "type": "SHPLG-S", "auth": False},
    "192.0.2.3": {"mac": "AABBCC0000B3", "gen": 3, "model": "S3SW-001X16EU", "auth_en": True},
}
PASSWORD = "s3cret"


def mock_shellylanman(aioclient_mock: AiohttpClientMocker, token: bool = True) -> None:
    aioclient_mock.get(f"{URL}/api/v1/about", json={"name": "ShellyLanMan", "version": "v0.7.0", "instanceId": INSTANCE})
    aioclient_mock.get(f"{URL}/api/v1/devices", json=DEVICES)
    aioclient_mock.get(f"{URL}/api/v1/checklist", json=CHECKLIST)
    aioclient_mock.get(f"{URL}/api/v1/backups", json=BACKUPS)
    if token:
        aioclient_mock.get(f"{URL}/api/v1/devices/AABBCC0000B3/credentials", json={"user": "admin", "password": PASSWORD})
    else:
        aioclient_mock.get(f"{URL}/api/v1/devices/AABBCC0000B3/credentials", status=403)


async def fake_get_info(session: Any, host: str, port: int = 80, **_: Any) -> dict[str, Any]:
    return INFO[host]


async def fake_validate(hass: HomeAssistant, host: str, port: int, info: dict[str, Any], data: dict[str, Any], verify_ssl: bool = False) -> dict[str, Any]:
    from homeassistant.components.shelly.config_flow import InvalidAuthError

    if info.get("auth_en") and data.get("password") != PASSWORD:
        raise InvalidAuthError
    gen = info.get("gen", 1)
    return {"title": INFO[host]["mac"], "sleep_period": 0, "model": info.get("model") or info.get("type"), "gen": gen}


@pytest.fixture
def shelly_mocks(hass: HomeAssistant):
    """Home Assistant's Shelly integration without network (and without its
    Bluetooth, zeroconf and USB stacks, marked as loaded)."""
    hass.config.components.update({"bluetooth", "usb", "zeroconf", "http", "network", "bluetooth_adapters"})
    with (
        patch("homeassistant.components.shelly.config_flow.get_info", side_effect=fake_get_info),
        patch("homeassistant.components.shelly.config_flow.validate_input", side_effect=fake_validate),
        patch("homeassistant.components.shelly.config_flow.ShellyConfigFlow._async_discover_zeroconf_devices", return_value={}),
        patch("homeassistant.components.shelly.config_flow.ShellyConfigFlow._async_discover_bluetooth_devices", return_value={}),
        patch("homeassistant.components.shelly.async_setup_entry", return_value=True),
    ):
        yield


async def _setup(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, token: bool = True) -> MockConfigEntry:
    mock_shellylanman(aioclient_mock, token)
    data = {"url": URL}
    if token:
        data["mcp_token"] = "tok"
        aioclient_mock.post(f"{URL}/mcp", json={"jsonrpc": "2.0", "id": 1, "result": {"tools": []}})
    entry = MockConfigEntry(domain=DOMAIN, data=data, unique_id=INSTANCE, title="ShellyLanMan")
    entry.add_to_hass(hass)
    # The Shelly integration already has D5, and discovered A1 itself (zeroconf).
    MockConfigEntry(domain="shelly", unique_id="AABBCC0000D5", data={"host": "192.0.2.5"}).add_to_hass(hass)
    await hass.config_entries.flow.async_init("shelly", context={"source": SOURCE_ZEROCONF}, data=ZeroconfServiceInfo(
        ip_address=ip_address("192.0.2.1"), ip_addresses=[ip_address("192.0.2.1")], hostname="shellyplus1-aabbcc0000a1.local.",
        name="shellyplus1-aabbcc0000a1._http._tcp.local.", port=80, type="_http._tcp.local.", properties={}))
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _shelly_ids(hass: HomeAssistant) -> set[str]:
    return {e.unique_id for e in hass.config_entries.async_entries("shelly") if e.source != SOURCE_IGNORE}


async def test_list_and_issue(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, shelly_mocks: None) -> None:
    entry = await _setup(hass, aioclient_mock)
    issue = ir.async_get(hass).async_get_issue(DOMAIN, f"shellys_missing_{entry.entry_id}")
    assert issue and issue.translation_placeholders == {"count": "3"}  # A1, B2, B3 (not C4 offline, BLU, D5)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM and result["step_id"] == "add"
    assert result["description_placeholders"]["discovered"] == "1"
    assert result["description_placeholders"]["missed"] == "2"
    assert "Away (192.0.2.4)" in result["description_placeholders"]["offline"]


async def test_add_all(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, shelly_mocks: None) -> None:
    entry = await _setup(hass, aioclient_mock)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"devices": ["AABBCC0000A1", "AABBCC0000B2", "AABBCC0000B3"]})
    assert result["type"] is FlowResultType.FORM and result["step_id"] == "result"
    assert result["description_placeholders"]["added"] == "3", result["description_placeholders"]["details"]
    # A1 through Home Assistant's own discovery, B2 and B3 through the manual flow,
    # B3 with the password ShellyLanMan passed on.
    assert _shelly_ids(hass) >= {"AABBCC0000A1", "AABBCC0000B2", "AABBCC0000B3", "AABBCC0000D5"}
    b3 = next(e for e in hass.config_entries.async_entries("shelly") if e.unique_id == "AABBCC0000B3")
    assert b3.data["password"] == PASSWORD and b3.data["host"] == "192.0.2.3"
    assert not [f for f in hass.config_entries.flow.async_progress_by_handler("shelly")]  # nothing left behind
    result = await hass.config_entries.options.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    # Nothing left to add: the issue is gone and Configure says so.
    await entry.runtime_data.state.async_refresh()
    assert ir.async_get(hass).async_get_issue(DOMAIN, f"shellys_missing_{entry.entry_id}") is None
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.ABORT and result["reason"] == "nothing_to_add"


async def test_password_not_passed_without_trusted_path(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, shelly_mocks: None) -> None:
    entry = await _setup(hass, aioclient_mock, token=False)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"devices": ["AABBCC0000B3"]})
    assert result["description_placeholders"]["added"] == "0"
    assert "AABBCC0000B3" not in _shelly_ids(hass)
    # Our own manual flow was ended; Home Assistant's A1 discovery is untouched.
    flows = hass.config_entries.flow.async_progress_by_handler("shelly")
    assert [f["context"]["unique_id"] for f in flows] == ["AABBCC0000A1"]


async def test_repair_flow_adds(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, shelly_mocks: None) -> None:
    from custom_components.shellylanman.repairs import async_create_fix_flow

    entry = await _setup(hass, aioclient_mock)
    flow = await async_create_fix_flow(hass, f"shellys_missing_{entry.entry_id}", {"entry_id": entry.entry_id})
    flow.hass = hass
    result = await flow.async_step_init()
    assert result["step_id"] == "add"
    result = await flow.async_step_add({"devices": ["AABBCC0000B2"]})
    assert result["step_id"] == "result" and result["description_placeholders"]["added"] == "1"
    assert "AABBCC0000B2" in _shelly_ids(hass)
