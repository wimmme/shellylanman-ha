# ShellyLanMan for Home Assistant

Home Assistant packaging of [ShellyLanMan](https://github.com/wimmme/shellylanman) — the
web application that discovers, monitors and manages the Shelly devices on your LAN,
based on [ShellyScanner](https://github.com/usnasoft/shellyscanner).

| Part | Status |
|---|---|
| **App** (`shellylanman/`): ShellyLanMan inside Home Assistant OS, in the sidebar | available |
| **Integration** (`custom_components/shellylanman`, HACS): ShellyLanMan's status, configuration backup and checklist on your Shelly devices, its tools in Assist | available |

The app needs **Home Assistant OS** (or a Supervised installation): Home Assistant
Container and Core have no apps. There, run ShellyLanMan with Docker as described in its
[README](https://github.com/wimmme/shellylanman#readme).

## Install the app

[![Add repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fwimmme%2Fshellylanman-ha)

Or by hand: **Settings → Apps → App Store → ⋮ → Repositories**, add
`https://github.com/wimmme/shellylanman-ha`, then install **ShellyLanMan**.

See [`shellylanman/DOCS.md`](shellylanman/DOCS.md) for what the app does and how it is
set up, and [`COMPATIBILITY.md`](COMPATIBILITY.md) for how this repository and
ShellyLanMan work together.

## Install the integration

Needs ShellyLanMan **0.5.0** or newer (the app, or the Docker version) and HACS.

1. HACS → ⋮ → **Custom repositories** → `https://github.com/wimmme/shellylanman-ha`,
   type **Integration** → install **ShellyLanMan**, restart Home Assistant.
2. With the app, Home Assistant offers **ShellyLanMan** under *Settings → Devices &
   services → Discovered*: one click. Otherwise *Add integration → ShellyLanMan* and
   ShellyLanMan's address (`http://<host>:3082`).

What you get, on the devices Home Assistant already has (matched by MAC address; a
device of its own when the Shelly integration does not have it):

| Entity | |
|---|---|
| ShellyLanMan status (online / offline / password needed / error / not found) | enabled |
| Last configuration backup, and a button *Back up configuration* | enabled |
| Checklist items: eco mode, LED off, debug log, Bluetooth, access point, Wi-Fi roaming, static IP, range extender, automatic firmware update | disabled — switch on what you want to watch |
| A device *ShellyLanMan*: devices on line / off line / needing attention, version, *Scan the network again* | enabled |

Relays, lights, meters and firmware updates stay with Home Assistant's own Shelly
integration; ShellyLanMan is not in the path of your automations.

### Assist

- **With the app** (Home Assistant 2026.10 or newer offers it with one click): Home
  Assistant's own *Model Context Protocol* integration is discovered too, at
  `http://127.0.0.1:8097/mcp` — ShellyLanMan's MCP server without token, reachable only
  on the Home Assistant host (app option *MCP for Home Assistant without token*). On
  2026.9 add *Model Context Protocol* by hand with that URL.
- **Any installation:** enter the MCP token (ShellyLanMan → Settings → MCP) in the
  integration (*Reconfigure*); it adds an LLM API *ShellyLanMan* for conversation
  agents.

Either way the MCP server must be enabled in ShellyLanMan, and its access level
(read / control / configure) decides what Assist may do.

## Licence

GPL-3.0-or-later, as ShellyLanMan and ShellyScanner. See [`LICENSE`](LICENSE).
