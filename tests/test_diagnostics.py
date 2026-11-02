"""Diagnostics: the last poll and the devices, without the MCP token."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.components.diagnostics import get_diagnostics_for_config_entry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from .conftest import INSTANCE, URL, mock_shellylanman


async def test_diagnostics(
    hass: HomeAssistant, hass_client: ClientSessionGenerator, aioclient_mock: AiohttpClientMocker, entry: MockConfigEntry
) -> None:
    mock_shellylanman(aioclient_mock)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    diag = await get_diagnostics_for_config_entry(hass, hass_client, entry)
    assert "'tok'" not in str(diag)  # the entry's token
    assert diag["entry"]["data"] == {"url": URL, "mcp_token": "**REDACTED**"}
    assert diag["shellylanman"] == {"version": "v0.5.0", "instance_id": INSTANCE, "url": URL, "mcp_token_set": True}
    assert diag["state"] == {"last_update_success": True, "last_exception": None, "update_interval_s": 30.0}
    assert diag["checklist"]["update_interval_s"] == 1800.0
    assert sorted(diag["devices"]) == ["80646F838136", "ECE334F95020"]
    assert diag["devices"]["80646F838136"]["status"] == "error"
    assert diag["last_backup"] == {"80646F838136": 1790843574000}
    assert diag["checklist_rows"]["80646F838136"]["eco"] is True
