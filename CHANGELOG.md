# Changelog of the integration

The app has its own changelog in `shellylanman/CHANGELOG.md`.

## Unreleased

- The integration is in the HACS default list (2026-10-21): search for ShellyLanMan in HACS, no custom repository needed (README).
- **The integration in 8 languages**, like ShellyLanMan: German, French, Spanish, Italian, Bulgarian and Chinese (simplified) next to English and Dutch, including the *Add Shellys* dialog. A test keeps the keys and placeholders equal.
- **Asks for a new MCP token** (reauthentication) when ShellyLanMan refuses the token, or when ShellyLanMan got a UI password after the integration was set up. Before, the integration stopped working or Assist failed, and you had to use *Reconfigure*.
- One backup at a time when several *Back up configuration* buttons are pressed together.
- Quality scale: Silver met. Tests for the error paths: 99 % coverage.
- Quality scale: a self-assessment against Home Assistant's integration quality scale (`QUALITY_SCALE.md`); the Bronze rules are met. For that: field descriptions in the set-up and reconfigure forms, tests for the whole config flow (already configured, discovery failing, reconfigure), and removal instructions in the README.
- README: more badges (app build, Home Assistant 2026.9+, Docker image, platforms, Shelly generations, languages), like ShellyLanMan's.
- README: from Home Assistant 2026.11 the integration is found in the Marketplace (*Settings → Marketplace*), which replaces HACS.

## 0.9.10

Works with ShellyLanMan 0.5.0 or newer (0.7.0 for passwords, 0.9.0 for a ShellyLanMan with a UI password); Home Assistant 2026.9 or newer.

- No changes to the integration; same version as the app (ShellyLanMan 0.9.10).

## 0.9.9

Works with ShellyLanMan 0.5.0 or newer (0.7.0 for passwords, 0.9.0 for a ShellyLanMan with a UI password); Home Assistant 2026.9 or newer.

- No changes to the integration; same version as the app (ShellyLanMan 0.9.9).

## 0.9.8

Works with ShellyLanMan 0.5.0 or newer (0.7.0 for passwords, 0.9.0 for a ShellyLanMan with a UI password); Home Assistant 2026.9 or newer.

- An error from ShellyLanMan without a message is reported with its code instead of an empty text.

## 0.9.7

Works with ShellyLanMan 0.5.0 or newer (0.7.0 for passwords, 0.9.0 for a ShellyLanMan with a UI password); Home Assistant 2026.9 or newer.

- Reads ShellyLanMan's coded errors (`{"error": {"code", "message"}}`, ShellyLanMan 0.9.7) and still the
  plain ones of earlier versions; a password-protected ShellyLanMan is recognised by the code `login_required`.

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
