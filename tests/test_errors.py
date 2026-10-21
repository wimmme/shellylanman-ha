"""When ShellyLanMan cannot be reached or answers with an error, and the smaller paths around it."""

from __future__ import annotations

from datetime import timedelta

import aiohttp
import pytest

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr, entity_registry as er, llm
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.shellylanman import async_remove_config_entry_device
from custom_components.shellylanman.const import DOMAIN

from .conftest import DEVICES, INSTANCE, URL, mock_shellylanman


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


def _entity_id(hass: HomeAssistant, domain: str, unique_id: str) -> str:
    entity_id = er.async_get(hass).async_get_entity_id(domain, DOMAIN, unique_id)
    assert entity_id, unique_id
    return entity_id


async def test_not_ready(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry) -> None:
    aioclient_mock.get(f"{URL}/api/v1/about", exc=aiohttp.ClientError())
    entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.SETUP_RETRY


async def test_mcp_off_at_setup(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry) -> None:
    """The MCP server switched off: the entry loads, no reauth (the token was not refused)."""
    mock_shellylanman(aioclient_mock, mcp=False)
    aioclient_mock.post(f"{URL}/mcp", status=404)
    await _setup(hass, entry)
    assert entry.state is ConfigEntryState.LOADED
    assert not hass.config_entries.flow.async_progress_by_handler(DOMAIN)


async def test_unavailable_and_back(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry) -> None:
    mock_shellylanman(aioclient_mock)
    await _setup(hass, entry)
    status = _entity_id(hass, "sensor", "80646F838136-status")
    aioclient_mock.clear_requests()
    aioclient_mock.get(f"{URL}/api/v1/about", status=500)
    aioclient_mock.get(f"{URL}/api/v1/checklist", status=500)
    await entry.runtime_data.state.async_refresh()
    await entry.runtime_data.checklist.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(status).state == STATE_UNAVAILABLE
    assert not entry.runtime_data.checklist.last_update_success

    aioclient_mock.clear_requests()
    mock_shellylanman(aioclient_mock)
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=31))
    await hass.async_block_till_done()
    assert hass.states.get(status).state == "error"


async def test_status_attributes(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry) -> None:
    DEVICES[0]["rebootRequired"] = True
    try:
        mock_shellylanman(aioclient_mock)
        await _setup(hass, entry)
    finally:
        del DEVICES[0]["rebootRequired"]
    attrs = hass.states.get(_entity_id(hass, "sensor", "ECE334F95020-status")).attributes
    assert attrs["reboot_required"] is True and attrs["ip"] == "192.0.2.20"


async def test_button_errors(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry) -> None:
    mock_shellylanman(aioclient_mock)
    await _setup(hass, entry)
    aioclient_mock.clear_requests()
    aioclient_mock.post(f"{URL}/api/v1/backup", status=500)
    aioclient_mock.post(f"{URL}/api/v1/scan", status=500)
    mock_shellylanman(aioclient_mock)
    for unique_id in ("80646F838136-backup", f"{INSTANCE}-rescan"):
        with pytest.raises(HomeAssistantError, match="HTTP 500"):
            await hass.services.async_call("button", "press", {"entity_id": _entity_id(hass, "button", unique_id)}, blocking=True)


async def test_llm_api_errors(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry) -> None:
    """MCP failing: Assist gets an error; a tool with an odd schema is offered without parameters."""
    odd = {"tools": [{"name": "odd", "description": "x", "inputSchema": {"type": "object", "properties": {"a": {"type": "nonsense"}}}}]}
    mock_shellylanman(aioclient_mock, mcp=False)
    aioclient_mock.post(f"{URL}/mcp", json={"jsonrpc": "2.0", "id": 1, "result": odd})
    await _setup(hass, entry)
    ctx = llm.LLMContext(platform="test", context=None, language="en", assistant="conversation", device_id=None)
    instance = await llm.async_get_api(hass, f"{DOMAIN}-{entry.entry_id}", ctx)
    assert [t.name for t in instance.tools] == ["odd"]

    aioclient_mock.clear_requests()
    aioclient_mock.post(f"{URL}/mcp", status=500)
    with pytest.raises(HomeAssistantError, match="ShellyLanMan"):
        await instance.tools[0].async_call(hass, llm.ToolInput(tool_name="odd", tool_args={}), ctx)
    with pytest.raises(HomeAssistantError, match="ShellyLanMan"):
        await llm.async_get_api(hass, f"{DOMAIN}-{entry.entry_id}", ctx)


async def test_reload_on_update(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry) -> None:
    mock_shellylanman(aioclient_mock)
    await _setup(hass, entry)
    first = entry.runtime_data
    hass.config_entries.async_update_entry(entry, options={"x": 1})
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED and entry.runtime_data is not first


async def test_remove_device(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry) -> None:
    """Only a Shelly ShellyLanMan no longer lists may be deleted; ShellyLanMan itself never."""
    mock_shellylanman(aioclient_mock)
    await _setup(hass, entry)
    reg = dr.async_get(hass)
    devices = dr.async_entries_for_config_entry(reg, entry.entry_id)
    listed = next(d for d in devices if (DOMAIN, "80646F838136") in d.identifiers)
    service = next(d for d in devices if (DOMAIN, INSTANCE) in d.identifiers)
    gone = reg.async_get_or_create(config_entry_id=entry.entry_id, identifiers={(DOMAIN, "AABBCCDDEEFF")})
    assert not await async_remove_config_entry_device(hass, entry, listed)
    assert not await async_remove_config_entry_device(hass, entry, service)
    assert await async_remove_config_entry_device(hass, entry, gone)


async def test_add_dialog_edges(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    """The repair fix for an entry that is not loaded; a failed Shelly with its reason in the result."""
    from custom_components.shellylanman.repairs import async_create_fix_flow
    from custom_components.shellylanman.shelly_add import Candidate, Result

    flow = await async_create_fix_flow(hass, "shellys_missing_x", {"entry_id": "unknown"})
    flow.hass, flow.handler, flow.flow_id = hass, DOMAIN, "fix"
    result = await flow.async_step_init()
    assert result["type"] == "abort" and result["reason"] == "not_loaded"

    c = Candidate(id="AABBCC000001", name="Pump", host="192.0.2.1", port=80, gen="2", protected=False, battery=False, state="missed")
    flow._results = [Result(c, "failed", "cannot_connect")]
    result = await flow.async_step_result()
    assert "Pump (192.0.2.1): not added (cannot_connect)" in result["description_placeholders"]["details"]
    result = await flow.async_step_result({})
    assert result["type"] == "create_entry"
