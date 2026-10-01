"""ShellyLanMan for Home Assistant.

Adds what ShellyLanMan knows about your Shelly devices to the devices Home
Assistant already has (matched by MAC address): ShellyLanMan's status, the
configuration backup and the settings checklist — and, with the MCP token,
ShellyLanMan's tools for Assist. It does not duplicate what the official
Shelly integration does (relays, lights, meters, firmware updates).
"""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr, llm
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ShellyLanManClient, ShellyLanManError
from .const import CONF_MCP_TOKEN, DOMAIN
from .coordinator import ChecklistCoordinator, StateCoordinator
from .llm_api import ShellyLanManAPI

PLATFORMS = [Platform.BINARY_SENSOR, Platform.BUTTON, Platform.SENSOR]


@dataclass
class RuntimeData:
    """What the platforms of one entry share."""

    client: ShellyLanManClient
    state: StateCoordinator
    checklist: ChecklistCoordinator
    instance_id: str


type ShellyLanManConfigEntry = ConfigEntry[RuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: ShellyLanManConfigEntry) -> bool:
    """Set up one ShellyLanMan installation."""
    client = ShellyLanManClient(async_get_clientsession(hass), entry.data[CONF_URL], entry.data.get(CONF_MCP_TOKEN))
    try:
        about = await client.about()
    except ShellyLanManError as err:
        raise ConfigEntryNotReady(str(err)) from err

    state = StateCoordinator(hass, entry, client)
    checklist = ChecklistCoordinator(hass, entry, client)
    await state.async_config_entry_first_refresh()
    await checklist.async_config_entry_first_refresh()
    entry.runtime_data = RuntimeData(client, state, checklist, entry.unique_id or about.get("instanceId", entry.entry_id))

    dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.runtime_data.instance_id)},
        name="ShellyLanMan",
        manufacturer="ShellyLanMan",
        model="ShellyLanMan",
        sw_version=state.data.version,
        configuration_url=client.url,
        entry_type=dr.DeviceEntryType.SERVICE,
    )

    if client.mcp_token:  # Assist: ShellyLanMan's MCP tools as an LLM API
        entry.async_on_unload(llm.async_register_api(hass, ShellyLanManAPI(hass=hass, id=f"{DOMAIN}-{entry.entry_id}", name="ShellyLanMan", client=client)))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_reload))
    return True


async def _reload(hass: HomeAssistant, entry: ShellyLanManConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ShellyLanManConfigEntry) -> bool:
    """Unload an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
