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

## Configuration (the app's options)

| Option | Default | What |
|---|---|---|
| `port` | 3082 | ShellyLanMan's web UI and API on your LAN, e.g. `http://homeassistant.local:3082` |
| `mcp_local` | on | Local access on 127.0.0.1 without token, for Home Assistant on this host: Assist's MCP client and the ShellyLanMan integration (also when ShellyLanMan has a password) |
| `mcp_local_port` | 8097 | The port of that local access |

Change a port when another program on this host already uses it; the app's log then
says which port is taken. ShellyLanMan's *Settings → General → Ports* shows the ports
in use and where they are set.

## How it runs

| | |
|---|---|
| Network | On the host network, so it can find devices with mDNS and reach them directly |
| Web UI in Home Assistant | Through ingress, on a free port Home Assistant chooses on its internal network |
| Web UI and API on the LAN | The option `port`, **3082** by default — for the MCP server (AI assistants) and direct access |
| Data | The app's data folder: settings (passwords encrypted), device archive, scenes and configuration backups. It is part of Home Assistant backups |

**Protect the LAN port with a password** (ShellyLanMan → Settings → Security): without
one, anyone who can reach that port of your Home Assistant host can use ShellyLanMan
there. The sidebar stays behind Home Assistant's login. Do not forward the port to the
internet.

## Support

Issues: https://github.com/wimmme/shellylanman/issues
