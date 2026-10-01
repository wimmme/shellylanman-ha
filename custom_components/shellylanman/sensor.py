"""ShellyLanMan status and last backup per device; counters for ShellyLanMan itself."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ShellyLanManConfigEntry
from .const import ATTENTION, STATUSES
from .coordinator import StateCoordinator
from .entity import DeviceEntity, ServiceEntity


async def async_setup_entry(hass: HomeAssistant, entry: ShellyLanManConfigEntry, add: AddConfigEntryEntitiesCallback) -> None:
    """Add the sensors, and those of devices that appear later."""
    rt = entry.runtime_data
    add([
        CountSensor(rt.state, rt.instance_id, "devices_online", lambda d: d.get("status") == "online"),
        CountSensor(rt.state, rt.instance_id, "devices_offline", lambda d: d.get("status") in ("offline", "ghost")),
        CountSensor(rt.state, rt.instance_id, "devices_attention", lambda d: d.get("status") in ATTENTION),
        VersionSensor(rt.state, rt.instance_id, "version"),
    ])
    known: set[str] = set()

    @callback
    def discover() -> None:
        new: list[SensorEntity] = []
        for dev_id, dev in rt.state.data.devices.items():
            if dev_id not in known:
                known.add(dev_id)
                new += [StatusSensor(rt.state, dev, "status"), LastBackupSensor(rt.state, dev, "last_backup")]
        if new:
            add(new)

    discover()
    entry.async_on_unload(rt.state.async_add_listener(discover))


class StatusSensor(DeviceEntity, SensorEntity):
    """ShellyLanMan's view of the device: online, offline, login, error, …"""

    coordinator: StateCoordinator
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = STATUSES

    @property
    def native_value(self) -> str | None:
        dev = self.coordinator.data.devices.get(self.device_id)
        status = dev.get("status") if dev else None
        return status if status in STATUSES else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        dev = self.coordinator.data.devices.get(self.device_id) or {}
        attrs = {k: dev[k] for k in ("ip", "gen", "typeName", "error") if dev.get(k)}
        if dev.get("rebootRequired"):
            attrs["reboot_required"] = True
        return attrs or None


class LastBackupSensor(DeviceEntity, SensorEntity):
    """When ShellyLanMan last backed up the device's configuration."""

    coordinator: StateCoordinator
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        ms = self.coordinator.data.last_backup.get(self.device_id)
        return datetime.fromtimestamp(ms / 1000, UTC) if ms else None


class CountSensor(ServiceEntity, SensorEntity):
    """How many devices are on line, off line or need attention."""

    coordinator: StateCoordinator
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: StateCoordinator, instance_id: str, key: str, match: Any) -> None:
        super().__init__(coordinator, instance_id, key)
        self._match = match

    @property
    def native_value(self) -> int:
        return sum(1 for d in self.coordinator.data.devices.values() if self._match(d))


class VersionSensor(ServiceEntity, SensorEntity):
    """ShellyLanMan's version."""

    coordinator: StateCoordinator
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.version or None
