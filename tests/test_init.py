"""Set-up: entities on the devices, the ShellyLanMan device, buttons, the LLM API."""

from __future__ import annotations

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr, entity_registry as er, llm
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.shellylanman.const import DOMAIN

from .conftest import INSTANCE, TOOLS, URL, mock_shellylanman


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


def _entity(hass: HomeAssistant, unique_id: str, domain: str) -> er.RegistryEntry:
    ent = er.async_get(hass).async_get_entity_id(domain, DOMAIN, unique_id)
    assert ent, unique_id
    return er.async_get(hass).async_get(ent)


async def test_entities(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry) -> None:
    mock_shellylanman(aioclient_mock)
    await _setup(hass, entry)

    # Status and last backup per device, on the device with that MAC.
    status = _entity(hass, "80646F838136-status", "sensor")
    assert hass.states.get(status.entity_id).state == "error"
    dev = dr.async_get(hass).async_get(status.device_id)
    assert (dr.CONNECTION_NETWORK_MAC, "80:64:6f:83:81:36") in dev.connections
    assert dev.name == "Grondwaterpomp" and dev.model == "PlugS"
    backup = _entity(hass, "80646F838136-last_backup", "sensor")
    assert hass.states.get(backup.entity_id).state == "2026-10-01T08:32:54+00:00"
    assert hass.states.get(_entity(hass, "ECE334F95020-last_backup", "sensor").entity_id).state == "unknown"

    # ShellyLanMan itself: counters, version.
    assert hass.states.get(_entity(hass, f"{INSTANCE}-devices_online", "sensor").entity_id).state == "1"
    assert hass.states.get(_entity(hass, f"{INSTANCE}-devices_attention", "sensor").entity_id).state == "1"
    assert hass.states.get(_entity(hass, f"{INSTANCE}-version", "sensor").entity_id).state == "v0.5.0"

    # Checklist: only items that apply, disabled by default.
    eco = _entity(hass, "80646F838136-eco_mode", "binary_sensor")
    assert eco.disabled_by is er.RegistryEntryDisabler.INTEGRATION
    assert er.async_get(hass).async_get_entity_id("binary_sensor", DOMAIN, "ECE334F95020-led_off") is None  # Gen2: no LED cell
    assert er.async_get(hass).async_get_entity_id("binary_sensor", DOMAIN, "80646F838136-access_point") is None


async def test_checklist_entity_values(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry) -> None:
    mock_shellylanman(aioclient_mock)
    entry.add_to_hass(hass)
    reg = er.async_get(hass)
    for uid in ("ECE334F95020-debug_log", "ECE334F95020-auto_firmware_update", "80646F838136-static_ip", "80646F838136-roaming"):
        reg.async_get_or_create("binary_sensor", DOMAIN, uid, config_entry=entry)  # pre-registered = enabled
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    log = hass.states.get(reg.async_get_entity_id("binary_sensor", DOMAIN, "ECE334F95020-debug_log"))
    assert log.state == "on" and log.attributes["detail"] == "socket"
    assert hass.states.get(reg.async_get_entity_id("binary_sensor", DOMAIN, "ECE334F95020-auto_firmware_update")).attributes["detail"] == "stable"
    assert hass.states.get(reg.async_get_entity_id("binary_sensor", DOMAIN, "80646F838136-static_ip")).state == "on"
    assert hass.states.get(reg.async_get_entity_id("binary_sensor", DOMAIN, "80646F838136-roaming")).state == "off"


async def test_buttons(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry) -> None:
    mock_shellylanman(aioclient_mock)
    await _setup(hass, entry)
    await hass.services.async_call("button", "press", {"entity_id": _entity(hass, "80646F838136-backup", "button").entity_id}, blocking=True)
    posts = [c for c in aioclient_mock.mock_calls if c[0] == "POST" and str(c[1]).endswith("/api/v1/backup")]
    assert posts and posts[0][2] == {"ids": ["80646F838136"]}
    await hass.services.async_call("button", "press", {"entity_id": _entity(hass, f"{INSTANCE}-rescan", "button").entity_id}, blocking=True)
    assert any(c[0] == "POST" and str(c[1]).endswith("/api/v1/scan") for c in aioclient_mock.mock_calls)


async def test_llm_api(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry) -> None:
    mock_shellylanman(aioclient_mock)
    aioclient_mock.post(f"{URL}/mcp", json={"jsonrpc": "2.0", "id": 1, "result": TOOLS})
    await _setup(hass, entry)
    api_id = f"{DOMAIN}-{entry.entry_id}"
    assert api_id in [a.id for a in llm.async_get_apis(hass)]
    ctx = llm.LLMContext(platform="test", context=None, language="en", assistant="conversation", device_id=None)
    instance = await llm.async_get_api(hass, api_id, ctx)
    assert [t.name for t in instance.tools] == ["shelly_list_devices", "shelly_switch"]

    aioclient_mock.clear_requests()
    mock_shellylanman(aioclient_mock)
    aioclient_mock.post(f"{URL}/mcp", json={"jsonrpc": "2.0", "id": 2, "result": {"content": [{"type": "text", "text": "done"}]}})
    tool = next(t for t in instance.tools if t.name == "shelly_switch")
    tool_input = llm.ToolInput(tool_name="shelly_switch", tool_args={"device": "Grondwaterpomp", "action": "on"})
    out = await tool.async_call(hass, tool_input, ctx)  # what APIInstance.async_call_tool calls
    assert out["content"][0]["text"] == "done"
    sent = [c for c in aioclient_mock.mock_calls if str(c[1]).endswith("/mcp")][-1][2]
    assert sent["method"] == "tools/call" and sent["params"]["arguments"] == {"device": "Grondwaterpomp", "action": "on"}


async def test_no_llm_api_without_token(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    mock_shellylanman(aioclient_mock)
    entry = MockConfigEntry(domain=DOMAIN, unique_id=INSTANCE, data={"url": URL})
    await _setup(hass, entry)
    assert not [a for a in llm.async_get_apis(hass) if a.id.startswith(DOMAIN)]


async def test_unload(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry) -> None:
    mock_shellylanman(aioclient_mock)
    await _setup(hass, entry)
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert not [a for a in llm.async_get_apis(hass) if a.id.startswith(DOMAIN)]


async def test_backup_failure_reported(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry) -> None:
    mock_shellylanman(aioclient_mock)
    await _setup(hass, entry)
    aioclient_mock.clear_requests()
    aioclient_mock.post(f"{URL}/api/v1/backup", json={"results": [{"id": "80646F838136", "result": "fail", "message": "Status-OFFLINE"}]})
    mock_shellylanman(aioclient_mock)  # registered after: the failure answer wins
    with pytest.raises(HomeAssistantError, match="Status-OFFLINE"):
        await hass.services.async_call("button", "press", {"entity_id": _entity(hass, "80646F838136-backup", "button").entity_id}, blocking=True)
