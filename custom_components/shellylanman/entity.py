"""Base entities: per Shelly device, and for ShellyLanMan itself."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo, format_mac
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN


def device_info(dev: dict[str, Any]) -> DeviceInfo:
    """ShellyLanMan's device for one Shelly, linked to the Shelly integration's by MAC.

    Since Home Assistant 2026.8 a device belongs to one integration only: the
    Shelly integration's device and this one stay two devices, which Home
    Assistant shows as linked through their shared MAC connection. Being our
    own, it gets the name, maker and model directly (the default_* fields are
    deprecated, removed in 2027.9).
    """
    return DeviceInfo(
        connections={(CONNECTION_NETWORK_MAC, format_mac(dev["id"]))},
        identifiers={(DOMAIN, dev["id"])},
        name=dev.get("name") or dev.get("hostname") or dev["id"],
        manufacturer="Shelly",
        model=dev.get("typeName") or None,
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
