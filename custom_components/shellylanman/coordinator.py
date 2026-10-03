"""Data from ShellyLanMan: device state every 30 s, the checklist every 30 min.

Polling instead of ShellyLanMan's WebSocket on purpose: an open WebSocket
counts as a viewer, and with viewers ShellyLanMan polls every device every
two seconds; the REST answers come from its cache and cost the devices nothing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ShellyLanManClient, ShellyLanManError
from .const import CHECKLIST_INTERVAL, DOMAIN, SCAN_INTERVAL, is_mac

_LOGGER = logging.getLogger(__name__)


@dataclass
class State:
    """One poll of ShellyLanMan."""

    version: str = ""
    devices: dict[str, dict[str, Any]] = field(default_factory=dict)
    last_backup: dict[str, int] = field(default_factory=dict)  # device id → unix ms of its newest backup


class StateCoordinator(DataUpdateCoordinator[State]):
    """Devices, their state and their newest backup."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: ShellyLanManClient) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=f"{DOMAIN} state", update_interval=SCAN_INTERVAL)
        self.client = client

    async def _async_update_data(self) -> State:
        try:
            about = await self.client.about()
            devices = await self.client.devices()
            backups = await self.client.backups()
        except ShellyLanManError as err:
            raise UpdateFailed(str(err)) from err
        last: dict[str, int] = {}
        for b in backups:  # newest first
            last.setdefault(b.get("deviceId", ""), int(b.get("time", 0)))
        return State(
            version=str(about.get("version", "")),
            # Only identified devices (the id is the MAC): a Shelly that could not be read
            # yet is listed by ShellyLanMan as "addr:<ip:port>" and gets no device here.
            devices={d["id"]: d for d in devices if is_mac(d.get("id"))},
            last_backup=last,
        )


class ChecklistCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """ShellyLanMan's checklist (ShellyScanner's), per device id."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: ShellyLanManClient) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=f"{DOMAIN} checklist", update_interval=CHECKLIST_INTERVAL)
        self.client = client

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            rows = await self.client.checklist()
        except ShellyLanManError as err:
            raise UpdateFailed(str(err)) from err
        return {r["id"]: r for r in rows if r.get("id")}
