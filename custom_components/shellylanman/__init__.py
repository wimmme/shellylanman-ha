"""ShellyLanMan for Home Assistant.

Adds what ShellyLanMan knows about your Shelly devices — ShellyLanMan's status,
the configuration backup and the settings checklist — on a device per Shelly that
Home Assistant links to the Shelly integration's device by MAC address — and, with the MCP token,
ShellyLanMan's tools for Assist. It does not duplicate what the official
Shelly integration does (relays, lights, meters, firmware updates).
"""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr, issue_registry as ir, llm
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .add_flow import issue_id, update_issue
from .api import ShellyLanManClient, ShellyLanManError
from .const import CONF_MCP_TOKEN, DOMAIN, is_mac
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

    # 0.5.0 also made devices for Shellys ShellyLanMan had not identified yet
    # ("addr:<ip:port>"); they are no devices.
    reg = dr.async_get(hass)
    for device in dr.async_entries_for_config_entry(reg, entry.entry_id):
        ids = [i for d, i in device.identifiers if d == DOMAIN]
        if ids and not any(is_mac(i) or i == entry.runtime_data.instance_id for i in ids):
            reg.async_remove_device(device.id)

    # Shellys ShellyLanMan knows and the Shelly integration does not have: a repair
    # issue while there are any (its fix and Configure add them, DECISIONS P13-4).
    @callback
    def _issue() -> None:
        update_issue(hass, entry.entry_id, entry.runtime_data)

    _issue()
    entry.async_on_unload(state.async_add_listener(_issue))

    if client.mcp_token:  # Assist: ShellyLanMan's MCP tools as an LLM API
        entry.async_on_unload(llm.async_register_api(hass, ShellyLanManAPI(hass=hass, id=f"{DOMAIN}-{entry.entry_id}", name="ShellyLanMan", client=client)))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_reload))
    return True


async def _reload(hass: HomeAssistant, entry: ShellyLanManConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_config_entry_device(hass: HomeAssistant, entry: ShellyLanManConfigEntry, device: dr.DeviceEntry) -> bool:
    """Let the user delete a device ShellyLanMan no longer lists (not ShellyLanMan itself)."""
    ids = {i for d, i in device.identifiers if d == DOMAIN}
    return not ids & (set(entry.runtime_data.state.data.devices) | {entry.runtime_data.instance_id})


async def async_unload_entry(hass: HomeAssistant, entry: ShellyLanManConfigEntry) -> bool:
    """Unload an entry."""
    ir.async_delete_issue(hass, DOMAIN, issue_id(entry.entry_id))
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
