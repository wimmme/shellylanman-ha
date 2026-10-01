"""Buttons: back up a device's configuration; rescan the network."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ShellyLanManConfigEntry
from .api import ShellyLanManError
from .coordinator import StateCoordinator
from .entity import DeviceEntity, ServiceEntity


async def async_setup_entry(hass: HomeAssistant, entry: ShellyLanManConfigEntry, add: AddConfigEntryEntitiesCallback) -> None:
    """Add the buttons, and those of devices that appear later."""
    rt = entry.runtime_data
    add([RescanButton(rt.state, rt.instance_id, "rescan")])
    known: set[str] = set()

    @callback
    def discover() -> None:
        new = [BackupButton(rt.state, dev, "backup") for dev_id, dev in rt.state.data.devices.items() if dev_id not in known]
        known.update(rt.state.data.devices)
        if new:
            add(new)

    discover()
    entry.async_on_unload(rt.state.async_add_listener(discover))


class BackupButton(DeviceEntity, ButtonEntity):
    """Back up the device's configuration to ShellyLanMan's backup folder (.sbk)."""

    coordinator: StateCoordinator

    async def async_press(self) -> None:
        try:
            lines = await self.coordinator.client.backup(self.device_id)
        except ShellyLanManError as err:
            raise HomeAssistantError(str(err)) from err
        failed = [line for line in lines if line.get("result") not in ("ok", "queued", "stored")]
        if failed:
            raise HomeAssistantError(f"Backup failed: {failed[0].get('message') or failed[0].get('result')}")
        await self.coordinator.async_request_refresh()


class RescanButton(ServiceEntity, ButtonEntity):
    """Let ShellyLanMan discover the devices again."""

    coordinator: StateCoordinator

    async def async_press(self) -> None:
        try:
            await self.coordinator.client.rescan()
        except ShellyLanManError as err:
            raise HomeAssistantError(str(err)) from err
