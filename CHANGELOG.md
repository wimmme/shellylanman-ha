# Changelog of the integration

The app has its own changelog in `shellylanman/CHANGELOG.md`.

## 0.9.6

Works with ShellyLanMan 0.5.0 or newer (0.7.0 for passwords, 0.9.0 for a ShellyLanMan with a UI password); Home Assistant 2026.9 or newer.

- No code changes; released with the app.

## 0.9.5

Works with ShellyLanMan 0.5.0 or newer (0.7.0 for passwords, 0.9.0 for a ShellyLanMan with a UI password); Home Assistant 2026.9 or newer.

- No code changes; released with the app.

## 0.9.4

Works with ShellyLanMan 0.5.0 or newer (0.7.0 for passwords, 0.9.0 for a ShellyLanMan with a UI password); Home Assistant 2026.9 or newer.

- No code changes; released with the app.

## 0.9.3

Works with ShellyLanMan 0.5.0 or newer (0.7.0 for passwords, 0.9.0 for a ShellyLanMan with a UI password); Home Assistant 2026.9 or newer.

- Next to the app, the integration finds the app's local access itself, also when its
  port was changed (option `mcp_local_port`).

## 0.9.2

Works with ShellyLanMan 0.5.0 or newer (0.7.0 for passwords, 0.9.0 for a ShellyLanMan with a UI password); Home Assistant 2026.9 or newer.

- No code changes; released with the app.

## 0.9.1

Works with ShellyLanMan 0.5.0 or newer (0.7.0 for passwords, 0.9.0 for a ShellyLanMan with a UI password); Home Assistant 2026.9 or newer.

- No code changes; released with the app.

## 0.9.0

Works with ShellyLanMan 0.5.0 or newer (0.7.0 for passwords, 0.9.0 for a ShellyLanMan with a UI password); Home Assistant 2026.9 or newer.

- A ShellyLanMan protected with a password: the integration sends the MCP token with
  every call, and asks for it when it is missing.
- Next to the Home Assistant app it needs no token: it then uses the app's own local
  address.

## 0.8.0

Works with ShellyLanMan 0.5.0 or newer (0.7.0 for passwords); Home Assistant 2026.9 or newer.

- No code changes. With ShellyLanMan 0.8.0, BLU devices that a gateway only relays
  appear as devices with their status; *Add Shellys* leaves them out, as it does all
  BLU devices.

## 0.7.0

Works with ShellyLanMan 0.5.0 or newer (0.7.0 for passwords); Home Assistant 2026.9 or newer.

- **Add Shellys to Home Assistant** (Configure, and a repair notice while Shellys are
  missing): the Shellys ShellyLanMan knows that are not in the Shelly integration,
  with the reason for each; the ticked ones are added through the Shelly integration's
  own flows — confirming Home Assistant's own discoveries, or its manual flow for the
  ones it missed — and a protected Shelly gets the password ShellyLanMan stores when
  it may hand it out.

## 0.6.4

Works with ShellyLanMan 0.5.0 or newer; Home Assistant 2026.9 or newer.

- No changes; same version as the app.

## 0.6.3

Works with ShellyLanMan 0.5.0 or newer; Home Assistant 2026.9 or newer.

- No changes; same version as the app.

## 0.6.2

Works with ShellyLanMan 0.5.0 or newer; Home Assistant 2026.9 or newer.

- No changes; same version as the app.

## 0.6.1

Works with ShellyLanMan 0.5.0 or newer; Home Assistant 2026.9 or newer.

- No changes; same version as the app.

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
