"""Diagnostics: what the integration knows of ShellyLanMan, without the token or passwords."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import ShellyLanManConfigEntry
from .const import CONF_MCP_TOKEN

# ShellyLanMan's device list has no secrets; these keys are left out all the same,
# should a later version add them.
TO_REDACT = {CONF_MCP_TOKEN, "password", "pass", "token", "user", "username", "ssid"}


def _poll(coordinator: DataUpdateCoordinator[Any]) -> dict[str, Any]:
    return {
        "last_update_success": coordinator.last_update_success,
        "last_exception": repr(coordinator.last_exception) if coordinator.last_exception else None,
        "update_interval_s": coordinator.update_interval.total_seconds() if coordinator.update_interval else None,
    }


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ShellyLanManConfigEntry) -> dict[str, Any]:
    """The entry, ShellyLanMan's version, the last poll and the devices."""
    rt = entry.runtime_data
    return {
        "entry": {"title": entry.title, "data": async_redact_data(dict(entry.data), TO_REDACT)},
        "shellylanman": {
            "version": rt.state.data.version,
            "instance_id": rt.instance_id,
            "url": rt.client.url,
            "mcp_token_set": rt.client.mcp_token is not None,
        },
        "state": _poll(rt.state),
        "checklist": _poll(rt.checklist),
        "devices": async_redact_data(rt.state.data.devices, TO_REDACT),
        "last_backup": rt.state.data.last_backup,
        "checklist_rows": async_redact_data(rt.checklist.data, TO_REDACT),
    }
