"""Checklist items per device (read-only, disabled by default — DECISIONS P11-14)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ShellyLanManConfigEntry
from .checklist import ITEMS, NOT_APPLICABLE, cell_detail, cell_state
from .coordinator import ChecklistCoordinator
from .entity import DeviceEntity


async def async_setup_entry(hass: HomeAssistant, entry: ShellyLanManConfigEntry, add: AddConfigEntryEntitiesCallback) -> None:
    """Add a checklist entity for every item that applies to a device; more when devices appear."""
    rt = entry.runtime_data
    known: set[str] = set()

    @callback
    def discover() -> None:
        new: list[ChecklistItem] = []
        for dev_id, row in rt.checklist.data.items():
            dev = rt.state.data.devices.get(dev_id)
            if dev is None:
                continue
            for cell, key in ITEMS.items():
                uid = f"{dev_id}-{key}"
                if uid not in known and cell_state(row.get(cell)) is not NOT_APPLICABLE:
                    known.add(uid)
                    new.append(ChecklistItem(rt.checklist, dev, cell, key))
        if new:
            add(new)

    discover()
    entry.async_on_unload(rt.checklist.async_add_listener(discover))


class ChecklistItem(DeviceEntity, BinarySensorEntity):
    """One checklist cell of one device."""

    coordinator: ChecklistCoordinator
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: ChecklistCoordinator, dev: dict[str, Any], cell: str, key: str) -> None:
        super().__init__(coordinator, dev, key)
        self._cell = cell

    def _value(self) -> Any:
        return (self.coordinator.data.get(self.device_id) or {}).get(self._cell)

    @property
    def available(self) -> bool:
        return super().available and cell_state(self._value()) is not NOT_APPLICABLE

    @property
    def is_on(self) -> bool | None:
        state = cell_state(self._value())
        return None if state is NOT_APPLICABLE else bool(state)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        detail = cell_detail(self._value())
        return {"detail": detail} if detail else None
