# ShellyLanMan for Home Assistant

Home Assistant packaging of [ShellyLanMan](https://github.com/wimmme/shellylanman) — the
web application that discovers, monitors and manages the Shelly devices on your LAN,
based on [ShellyScanner](https://github.com/usnasoft/shellyscanner).

| Part | Status |
|---|---|
| **App** (`shellylanman/`): ShellyLanMan inside Home Assistant OS, in the sidebar | available |
| **Integration** (`custom_components/shellylanman`, HACS): ShellyLanMan's checks next to your Shelly devices, its tools in Assist | planned |

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

## Licence

GPL-3.0-or-later, as ShellyLanMan and ShellyScanner. See [`LICENSE`](LICENSE).
