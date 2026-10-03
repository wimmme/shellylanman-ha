# Changelog of the integration

The app has its own changelog in `shellylanman/CHANGELOG.md`.

## 0.6.0

- Devices: name, maker and model are set directly instead of the `default_*` fields,
  which Home Assistant deprecated (warning in the log; removed in 2027.9). Since Home
  Assistant 2026.8 a device belongs to one integration, so ShellyLanMan's device for a
  Shelly is its own device, linked to the Shelly integration's one by MAC address.
- Shellys that ShellyLanMan has not identified yet (listed by address) get no device;
  such devices made by 0.5.0 are removed. A device ShellyLanMan no longer lists can be
  deleted in Home Assistant.
- Status `searching` (ShellyLanMan 0.6.0: a device listed before a rescan and not found
  again yet). Counters are called *Devices online* / *Devices offline*.
- Manifest key order (hassfest).

## 0.5.0

First version of the ShellyLanMan integration (`custom_components/shellylanman`):
ShellyLanMan status, last configuration backup and a backup button on every Shelly
device (on the device of Home Assistant's Shelly integration, matched by MAC), the
settings checklist as diagnostic sensors (disabled by default), a ShellyLanMan device
with counters, version and a rescan button, set-up from the app's discovery or by
hand, and — with the MCP token — ShellyLanMan's MCP tools as an LLM API for Assist.
Needs ShellyLanMan 0.5.0 and Home Assistant 2026.9 or newer.
