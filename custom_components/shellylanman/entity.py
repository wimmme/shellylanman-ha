"""Base entities: per Shelly device, and for ShellyLanMan itself."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo, format_mac
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN


def device_info(dev: dict[str, Any]) -> DeviceInfo:
    """Device info that lands on the Shelly integration's device with the same MAC.

    The official Shelly integration registers its devices by MAC connection; a
    device with the same connection is the same device in Home Assistant. When
    that integration does not have the device, this creates one of our own.
    Only default_* values: they never overwrite the name, maker and model the
    Shelly integration (or the user) gave the device.
    """
    mac = format_mac(dev.get("id", ""))
    return DeviceInfo(
        connections={(CONNECTION_NETWORK_MAC, mac)},
        identifiers={(DOMAIN, dev["id"])},
        default_name=dev.get("name") or dev.get("hostname") or dev["id"],
        default_manufacturer="Shelly",
        default_model=dev.get("typeName") or None,
    )


class DeviceEntity(CoordinatorEntity[DataUpdateCoordinator[Any]]):
    """An entity about one Shelly device."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: DataUpdateCoordinator[Any], dev: dict[str, Any], key: str) -> None:
        super().__init__(coordinator)
        self.device_id: str = dev["id"]
        self._attr_unique_id = f"{self.device_id}-{key}"
        self._attr_translation_key = key
        self._attr_device_info = device_info(dev)


class ServiceEntity(CoordinatorEntity[DataUpdateCoordinator[Any]]):
    """An entity about ShellyLanMan itself."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DataUpdateCoordinator[Any], instance_id: str, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{instance_id}-{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, instance_id)})
