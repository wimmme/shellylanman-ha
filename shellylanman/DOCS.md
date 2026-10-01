# ShellyLanMan

ShellyLanMan discovers the Shelly devices on your network (Gen1, Gen2, Gen3, Gen4, Pro and
BLU through their gateways) and lets you monitor and manage them from one page: status,
readings, settings checklist, firmware updates, configuration backups, scripts,
schedules and more. Everything stays on your LAN; the Shelly cloud is not used.

It complements Home Assistant's own Shelly integration: Home Assistant automates your
devices, ShellyLanMan keeps them in shape.

## Using it

After the start, **ShellyLanMan** appears in Home Assistant's sidebar. It opens behind
Home Assistant's login. Settings (scan mode, device passwords, MCP for AI assistants, …)
are made in ShellyLanMan's own **Settings** page.

## How it runs

| | |
|---|---|
| Network | On the host network, so it can find devices with mDNS and reach them directly |
| Web UI in Home Assistant | Through ingress (port 8099 on Home Assistant's internal network only) |
| Web UI and API on the LAN | ShellyLanMan's own port, **3082** unless changed in its settings — for the MCP server (AI assistants) and direct access |
| Data | The app's data folder: settings (passwords encrypted), device archive, scenes and configuration backups. It is part of Home Assistant backups |

**The LAN port has no login of its own.** Anyone who can reach port 3082 of your Home
Assistant host can use ShellyLanMan there. Keep your network trusted; do not forward
this port to the internet.

## Support

Issues: https://github.com/wimmme/shellylanman/issues
