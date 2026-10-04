"""Repair issue "Shellys not in Home Assistant": its fix is the add dialog."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.repairs import RepairsFlow
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .add_flow import AddShellysSteps

if TYPE_CHECKING:
    from . import RuntimeData


class AddShellysRepairFlow(AddShellysSteps, RepairsFlow):
    """The same list and result as Configure → Add Shellys to Home Assistant."""

    def __init__(self, entry_id: str) -> None:
        self._entry_id = entry_id

    def runtime(self) -> RuntimeData | None:
        entry = self.hass.config_entries.async_get_entry(self._entry_id)
        return entry.runtime_data if entry and entry.state is ConfigEntryState.LOADED else None

    def done(self) -> FlowResult:
        return self.async_create_entry(data={})

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        return await self.async_step_add()


async def async_create_fix_flow(hass: HomeAssistant, issue_id: str, data: dict[str, Any] | None) -> RepairsFlow:
    """The fix of a "shellys_missing" issue."""
    return AddShellysRepairFlow(str((data or {}).get("entry_id", "")))
