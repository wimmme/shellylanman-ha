# Changelog of the integration

The app has its own changelog in `shellylanman/CHANGELOG.md`.

## 0.6.0

Works with ShellyLanMan 0.5.0 or newer; Home Assistant 2026.9 or newer.

- Name, maker and model of a device are set directly instead of the `default_*`
  fields, which Home Assistant deprecated (warning in the log; removed in 2027.9).
- Since Home Assistant 2026.8 a device belongs to one integration: ShellyLanMan's
  device for a Shelly is its own device, linked to the Shelly integration's one by MAC
  address.
- Shellys that ShellyLanMan has not identified yet (listed by address) get no device;
  such devices made by 0.5.0 are removed.
- A device that ShellyLanMan no longer lists can be deleted in Home Assistant.
- Status `searching` (ShellyLanMan 0.6.0: listed before a rescan, not found again yet).
- The counters are called *Devices online* and *Devices offline*.
- Manifest key order (hassfest).

## 0.5.0

Works with ShellyLanMan 0.5.0 or newer; Home Assistant 2026.9 or newer. First version
of the integration (`custom_components/shellylanman`).

- ShellyLanMan status, last configuration backup and a *Back up configuration* button
  for every Shelly device, matched by MAC address.
- The settings checklist as diagnostic sensors, disabled by default.
- A *ShellyLanMan* device with counters, version and a *Scan the network again* button.
- Set up from the app's discovery with one click, or by hand with ShellyLanMan's
  address.
- With the MCP token: ShellyLanMan's MCP tools as an LLM API for Assist.
