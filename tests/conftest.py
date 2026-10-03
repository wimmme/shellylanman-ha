"""Fixtures: a fake ShellyLanMan answered by aioclient_mock."""

from __future__ import annotations

from typing import Any

import pytest

from homeassistant.const import CONF_URL
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.shellylanman.const import CONF_MCP_TOKEN, DOMAIN

URL = "http://192.0.2.10:3082"
INSTANCE = "0123456789abcdef"

DEVICES: list[dict[str, Any]] = [
    {"id": "ECE334F95020", "name": "LedBerging", "hostname": "shellyprorgbwwpm-ece334f95020", "typeName": "Shelly Pro RGBWW PM",
     "gen": "2", "ip": "192.0.2.20", "status": "online"},
    {"id": "80646F838136", "name": "Grondwaterpomp", "hostname": "shellyplug-s-80646F838136", "typeName": "PlugS",
     "gen": "1", "ip": "192.0.2.86", "status": "error", "error": "timeout"},
    # Not identified yet (ShellyLanMan lists it by address): no device in Home Assistant.
    {"id": "addr:192.0.2.150:80", "name": "", "hostname": "shellytestplug", "typeName": "Generic",
     "gen": "-", "ip": "192.0.2.150", "status": "error", "error": "timeout"},
]

CHECKLIST: list[dict[str, Any]] = [
    {"id": "ECE334F95020", "gen": "2", "eco": False, "led": "-", "logs": "socket", "ble": [], "ap": False,
     "roaming": "-80", "wifi1": "-", "wifi2": "-", "extender": "✗", "scripts": "0 / 0", "autoFW": "stable"},
    {"id": "80646F838136", "gen": "1", "eco": True, "led": False, "logs": False, "ble": None, "ap": "-",
     "roaming": "✗", "wifi1": "✓", "wifi2": "-", "extender": "-", "scripts": "-", "autoFW": "-"},
]

BACKUPS = [
    {"deviceId": "80646F838136", "name": "b2.sbk", "time": 1790843574000},
    {"deviceId": "80646F838136", "name": "b1.sbk", "time": 1790000000000},
]

TOOLS = {"tools": [
    {"name": "shelly_list_devices", "description": "All devices", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "additionalProperties": False}},
    {"name": "shelly_switch", "description": "Switch a relay", "inputSchema": {"type": "object", "properties": {
        "device": {"type": "string"}, "action": {"type": "string", "enum": ["on", "off", "toggle"]}}, "required": ["device", "action"]}},
]}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Load custom_components/shellylanman."""


def mock_shellylanman(aioclient_mock: AiohttpClientMocker, url: str = URL, instance: str = INSTANCE) -> None:
    """Answer ShellyLanMan's API and MCP like version 0.5.0."""
    aioclient_mock.get(f"{url}/api/v1/about", json={"name": "ShellyLanMan", "version": "v0.5.0", "instanceId": instance})
    aioclient_mock.get(f"{url}/api/v1/devices", json=DEVICES)
    aioclient_mock.get(f"{url}/api/v1/checklist", json=CHECKLIST)
    aioclient_mock.get(f"{url}/api/v1/backups", json=BACKUPS)
    aioclient_mock.post(f"{url}/api/v1/backup", json={"results": [{"id": "80646F838136", "name": "shellyplug-s-80646F838136", "result": "ok"}]})
    aioclient_mock.post(f"{url}/api/v1/scan", status=202)


@pytest.fixture
def entry() -> MockConfigEntry:
    """A set-up entry with an MCP token."""
    return MockConfigEntry(domain=DOMAIN, unique_id=INSTANCE, title="ShellyLanMan", data={CONF_URL: URL, CONF_MCP_TOKEN: "tok"})
