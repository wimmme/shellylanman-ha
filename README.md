# ShellyLanMan for Home Assistant

Home Assistant packaging of [ShellyLanMan](https://github.com/wimmme/shellylanman) — the
web application that discovers, monitors and manages the Shelly devices on your LAN,
started from [ShellyScanner](https://github.com/usnasoft/shellyscanner), built on its basis
and developed further.

In Home Assistant's colours:

<p>
  <img src="https://raw.githubusercontent.com/wimmme/shellylanman/main/docs/images/screenshot-devices.png" alt="Devices" width="420">
  <img src="https://raw.githubusercontent.com/wimmme/shellylanman/main/docs/images/screenshot-checklist.png" alt="Checklist" width="420">
</p>

Two ways to run ShellyLanMan:

- **As a Home Assistant app** (Home Assistant OS or Supervised): below, *Install the app*.
- **As a standalone Docker container**, on any machine in your LAN: see ShellyLanMan's
  [README](https://github.com/wimmme/shellylanman#readme). The integration works with
  either.

| Part | Status |
|---|---|
| **App** (`shellylanman/`): ShellyLanMan inside Home Assistant OS, in the sidebar | available |
| **Integration** (`custom_components/shellylanman`, HACS): ShellyLanMan's status, configuration backup and checklist on your Shelly devices, its tools in Assist | available |

The app needs **Home Assistant OS** (or a Supervised installation): Home Assistant
Container and Core have no apps. There, run ShellyLanMan with Docker as described in its
[README](https://github.com/wimmme/shellylanman#readme).

## Install the app

1. Add this repository to Home Assistant's app store:

   [![Add the repository to your Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fwimmme%2Fshellylanman-ha)

2. Open the app and install it, then start it:

   [![Open the ShellyLanMan app in your Home Assistant](https://my.home-assistant.io/badges/supervisor_addon.svg)](https://my.home-assistant.io/redirect/supervisor_addon/?addon=505f279b_shellylanman&repository_url=https%3A%2F%2Fgithub.com%2Fwimmme%2Fshellylanman-ha)

Or by hand: **Settings → Apps → App Store → ⋮ → Repositories**, add
`https://github.com/wimmme/shellylanman-ha`, then install **ShellyLanMan**.

See [`shellylanman/DOCS.md`](shellylanman/DOCS.md) for what the app does and how it is
set up, and [`COMPATIBILITY.md`](COMPATIBILITY.md) for how this repository and
ShellyLanMan work together.

## Install the integration

Needs ShellyLanMan **0.5.0** or newer (the app, or the Docker version) and HACS.

1. Open the repository in HACS and download **ShellyLanMan**, then restart Home
   Assistant:

   [![Open the repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=wimmme&repository=shellylanman-ha&category=integration)

   (By hand: HACS → ⋮ → **Custom repositories** → `https://github.com/wimmme/shellylanman-ha`,
   type **Integration**.)
2. With the app, Home Assistant offers **ShellyLanMan** under *Settings → Devices &
   services → Discovered*: one click. Otherwise add it with ShellyLanMan's address
   (`http://<host>:3082`):

   [![Add the ShellyLanMan integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=shellylanman)

**The Shellys themselves come from Home Assistant's own Shelly integration** — add them
there first (Home Assistant usually discovers them). This integration does not add your
Shellys to Home Assistant; it adds what ShellyLanMan knows about them. Per Shelly it
makes a device of its own, which Home Assistant shows as *linked* to the Shelly
integration's device through their MAC address (since Home Assistant 2026.8 a device
belongs to one integration; they are no longer merged into one).

What you get:

| Entity | |
|---|---|
| ShellyLanMan status (online / offline / password needed / error / not found / searching) | enabled |
| Last configuration backup, and a button *Back up configuration* | enabled |
| Checklist items: eco mode, LED off, debug log, Bluetooth, access point, Wi-Fi roaming, static IP, range extender, automatic firmware update | disabled — switch on what you want to watch |
| A device *ShellyLanMan*: devices online / offline / needing attention, version, *Scan the network again* | enabled |

Relays, lights, meters and firmware updates stay with Home Assistant's own Shelly
integration; ShellyLanMan is not in the path of your automations.

### Add your Shellys to Home Assistant

Home Assistant discovers most Shellys itself, but wants one click per device, and it
misses some (a Shelly whose announcement it did not hear). The integration's
**Configure** — and a repair notice while Shellys are missing — lists the Shellys
ShellyLanMan knows that are not in the Shelly integration, with the reason for each
(discovered by Home Assistant, not offered, needs a password, not answering). Tick
the ones you want; they are added **through the Shelly integration's own steps**, as
if you added them there, and the result says what happened to each.

A Shelly with a password gets the one ShellyLanMan stores, but only on a trusted
path: with the app on the same host (its loopback listener), or with the MCP token
(access level *configure*) set in the integration. Otherwise you type the password
in Home Assistant under *Discovered*. Needs ShellyLanMan 0.7.0 for the password and
the "protected" hint; older versions still add Shellys without a password.

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
