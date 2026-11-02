# ShellyLanMan for Home Assistant

<p>
  <a href="https://github.com/wimmme/shellylanman-ha/releases"><img src="https://img.shields.io/github/v/release/wimmme/shellylanman-ha?style=flat-square&amp;color=0ea5e9&amp;label=integration" alt="Integration release"></a>
  <a href="shellylanman/CHANGELOG.md"><img src="https://img.shields.io/github/v/tag/wimmme/shellylanman-ha?filter=app-v*&amp;style=flat-square&amp;color=0ea5e9&amp;label=app" alt="App version"></a>
  <a href="https://github.com/wimmme/shellylanman-ha/actions/workflows/integration.yml"><img src="https://img.shields.io/github/actions/workflow/status/wimmme/shellylanman-ha/integration.yml?branch=main&amp;style=flat-square&amp;label=tests" alt="Tests"></a>
  <a href="https://github.com/wimmme/shellylanman-ha/actions/workflows/app.yml"><img src="https://img.shields.io/github/actions/workflow/status/wimmme/shellylanman-ha/app.yml?branch=main&amp;style=flat-square&amp;label=app" alt="App"></a>
  <a href="https://github.com/wimmme/shellylanman-ha/actions/workflows/github-code-scanning/codeql"><img src="https://img.shields.io/github/actions/workflow/status/wimmme/shellylanman-ha/dynamic%2Fgithub-code-scanning%2Fcodeql?branch=main&amp;style=flat-square&amp;label=CodeQL" alt="CodeQL"></a>
  <a href="https://hacs.xyz"><img src="https://img.shields.io/badge/HACS-default-41BDF5?style=flat-square" alt="HACS default"></a>
  <a href="https://www.home-assistant.io"><img src="https://img.shields.io/badge/Home%20Assistant-2026.9%2B-41BDF5?style=flat-square" alt="Home Assistant 2026.9+"></a>
  <a href="QUALITY_SCALE.md"><img src="https://img.shields.io/badge/quality%20scale-platinum%20(self--assessed)-7E8C9A?style=flat-square" alt="Quality scale: Platinum (self-assessed)"></a>
  <a href="https://github.com/wimmme/shellylanman-ha/pkgs/container/shellylanman-ha"><img src="https://img.shields.io/badge/docker-ghcr.io%2Fwimmme%2Fshellylanman--ha-2496ED?style=flat-square&amp;logo=docker&amp;logoColor=white" alt="Docker image"></a>
  <img src="https://img.shields.io/badge/platforms-amd64%20%7C%20arm64-6b7280?style=flat-square" alt="Platforms">
  <img src="https://img.shields.io/badge/Shelly-Gen1%20%7C%20Gen2%20%7C%20Gen3%20%7C%20Gen4%20%7C%20BLU-1e40af?style=flat-square" alt="Shelly generations">
  <img src="https://img.shields.io/badge/languages-8-0f766e?style=flat-square" alt="Languages">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/wimmme/shellylanman-ha?style=flat-square&amp;color=161a3a" alt="Licence"></a>
  <a href="https://www.paypal.com/donate/?business=LPS62D2BRTD2Y&amp;no_recurring=0&amp;item_name=You+help+me+buying+coffee+and+tokens+for+coding+%3A-%29&amp;currency_code=EUR"><img src="https://img.shields.io/badge/donate-PayPal-0070BA?style=flat-square&amp;logo=paypal&amp;logoColor=white" alt="Donate with PayPal"></a>
</p>

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

Needs ShellyLanMan **0.5.0** or newer (the app, or the Docker version). The integration
is in the HACS default list, so it is in Home Assistant's **Marketplace** too (Home
Assistant 2026.11 and newer, *Settings → Marketplace*, where HACS moved).

1. Search for **ShellyLanMan** in the Marketplace (or in HACS before Home Assistant
   2026.11), download it, then restart Home Assistant. With HACS this button opens it:

   [![Open the repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=wimmme&repository=shellylanman-ha&category=integration)
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

### Supported Shellys

Every Shelly ShellyLanMan knows: Gen1, Gen2 (Plus and Pro), Gen3 and Gen4, and BLU
devices through their gateways. A Shelly gets its device in Home Assistant once
ShellyLanMan has identified it (read its MAC address); until then ShellyLanMan lists it
by address only. The checklist entities exist only for the items that apply to a
device: a Gen1 plug has no Bluetooth, a BLU device no Wi-Fi.

### How the data is updated

The integration polls ShellyLanMan; it never talks to the Shellys itself.

- **Every 30 seconds**: the devices, their status and their newest configuration
  backup. ShellyLanMan answers from its own cache, so this costs the Shellys nothing.
  A change on a Shelly reaches Home Assistant after ShellyLanMan has seen it, plus up
  to 30 seconds.
- **Every 30 minutes**: the checklist. It reads every device's settings (one request
  per Shelly), so it is read seldom.
- **On demand**: after *Back up configuration*, and when the *Add Shellys* dialog opens.

A new Shelly gets its entities without a reload, at the next poll (its checklist
entities at the next checklist poll). When ShellyLanMan cannot be reached, the
entities become unavailable and the integration logs it once; they come back by
themselves.

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

Either way the MCP server must be on in ShellyLanMan (*Settings → MCP*; on, read only,
in a new installation since 0.9.12), and its access level (read / control / configure)
decides what Assist may do. Home Assistant offers *Model Context Protocol* only while
it is on.

### Use cases

- **See at a glance** which Shellys are off line or need attention (an error, a
  password ShellyLanMan lacks), on a dashboard and in the history.
- **Back up every Shelly's configuration on a schedule** from an automation, and see
  per device when it was last backed up.
- **Keep an eye on settings** that should stay as they are: a debug log left on,
  automatic firmware updates, the access point, eco mode.
- **Add the Shellys Home Assistant missed** in one go (*Configure* or the repair notice).
- **Ask Assist** about your Shellys, or let it act through ShellyLanMan's tools.

### Examples

Entity ids depend on your device names; *Kitchen* is an example. Notify when Shellys
need attention for five minutes:

```yaml
automation:
  - alias: "Shellys need attention"
    triggers:
      - trigger: numeric_state
        entity_id: sensor.shellylanman_devices_needing_attention
        above: 0
        for: "00:05:00"
    actions:
      - action: notify.notify
        data:
          message: >
            {{ states('sensor.shellylanman_devices_needing_attention') }} Shelly(s)
            need attention in ShellyLanMan.
```

Back up every Shelly on Sunday night (the buttons run one backup at a time):

```yaml
automation:
  - alias: "Weekly Shelly configuration backup"
    triggers:
      - trigger: time
        at: "03:00:00"
    conditions:
      - condition: time
        weekday: sun
    actions:
      - action: button.press
        target:
          entity_id: >
            {{ integration_entities('shellylanman')
               | select('search', '_back_up_configuration$') | list }}
```

Warn when a Shelly's debug log has been on for a day (enable the *Debug log* entity
first; checklist entities are disabled by default):

```yaml
automation:
  - alias: "Shelly debug log left on"
    triggers:
      - trigger: state
        entity_id: binary_sensor.kitchen_debug_log
        to: "on"
        for: "24:00:00"
    actions:
      - action: notify.notify
        data:
          message: "The debug log of the kitchen Shelly is still on."
```

### Known limitations

- It needs a running ShellyLanMan (0.5.0 or newer): the app, or the Docker version.
- It does not switch or measure anything: that is the Shelly integration's work.
- It polls: a change reaches Home Assistant up to 30 seconds after ShellyLanMan saw
  it, and the checklist can be 30 minutes old.
- The checklist entities are read only: change a setting in ShellyLanMan
  (*Checklist* page), and it shows at the next checklist poll.
- A battery-powered Shelly sleeps most of the time and may show *Offline* while it
  sleeps.
- *Add Shellys* adds Wi-Fi Shellys (Gen1 to Gen4); BLU devices are added in Home
  Assistant through Bluetooth or a Shelly gateway, as usual.
- Shelly passwords are handed to Home Assistant only on a trusted path (the app on
  the same host, or the MCP token with access level *configure*).

### Troubleshooting

- **"Cannot reach ShellyLanMan at this address"**: open the same URL in a browser on a
  machine in the same network as Home Assistant. Use `http://`, the host and the port
  (`3082` unless you changed it). With the app, use the entry Home Assistant
  discovers instead of typing an address.
- **Home Assistant asks for the MCP token** (a notice under *Settings → Devices &
  services*): ShellyLanMan refused the token, or got a UI password after the
  integration was set up. Copy the token from ShellyLanMan → *Settings → MCP*.
- **All entities unavailable**: ShellyLanMan is stopped or not reachable. Start it;
  the entities come back at the next poll.
- **Status *Password needed***: ShellyLanMan has no (correct) password for that Shelly.
  Enter it in ShellyLanMan: *Login* on the device, or the default credentials under
  *Settings → Network*.
- **A Shelly is missing in *Add Shellys***: the dialog lists Wi-Fi Shellys that
  ShellyLanMan has identified and that are not in the Shelly integration. A Shelly you
  once *ignored* there stays hidden until you un-ignore it (*Settings → Devices &
  services → Shelly → Ignored*). A Shelly that does not answer is listed but cannot be
  added now.
- **No checklist entities**: they are disabled by default. Open the device and enable
  the ones you want; only the items that apply to the device exist.
- **Assist has no ShellyLanMan tools**: the MCP server must be on in ShellyLanMan
  (*Settings → MCP*) and the MCP token set in the integration (*Reconfigure*); the
  access level decides which tools Assist gets.

When you report a problem, add the integration's diagnostics (*Settings → Devices &
services → ShellyLanMan → ⋮ → Download diagnostics*; the MCP token is left out) and,
if you can, a debug log (*⋮ → Enable debug logging*, repeat the problem, *Disable
debug logging*), in a [GitHub issue](https://github.com/wimmme/shellylanman-ha/issues).

### Remove the integration

1. *Settings → Devices & services → ShellyLanMan* → ⋮ → **Delete**. Its devices and
   entities go with it; the Shellys in Home Assistant's Shelly integration stay, and
   so do ShellyLanMan and its backups.
2. To remove the files too: in the Marketplace (or HACS) open **ShellyLanMan** → ⋮ →
   **Remove**, then restart Home Assistant.

The app is removed separately, under *Settings → Apps*. Home Assistant's *Model Context
Protocol* integration, if you added it for Assist, is its own entry.

How the integration measures up to Home Assistant's
[integration quality scale](https://contributors.home-assistant.io/core/quality-scale/):
[`QUALITY_SCALE.md`](QUALITY_SCALE.md). What comes next: [`ROADMAP.md`](ROADMAP.md).

## Licence

GPL-3.0-or-later, as ShellyLanMan and ShellyScanner. See [`LICENSE`](LICENSE).
