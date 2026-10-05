# How this repository and ShellyLanMan work together

Two repositories, one product:

| Repository | Holds | Language | Releases |
|---|---|---|---|
| [`wimmme/shellylanman`](https://github.com/wimmme/shellylanman) | The application: server, web UI, REST API, WebSocket, MCP server | Go, TypeScript | `vX.Y.Z` tags → `ghcr.io/wimmme/shellylanman:X.Y.Z` (amd64, arm64) |
| `wimmme/shellylanman-ha` (this one) | Home Assistant packaging: the app, later the integration | YAML, shell; Python for the integration | `vX.Y.Z` tags → `ghcr.io/wimmme/shellylanman-ha:X.Y.Z` (amd64, aarch64) |

## The app

- **Version = ShellyLanMan version.** App `0.4.0` runs ShellyLanMan `0.4.0`: its image is
  built `FROM ghcr.io/wimmme/shellylanman:0.4.0` and adds only `run.sh` and `su-exec`.
  App-only fixes get a fourth number in the app changelog and rebuild the same
  ShellyLanMan version (`0.4.0-1` → `FROM …:0.4.0`).
- **What the app relies on in ShellyLanMan** (part of ShellyLanMan's interface; a change
  there is a breaking change for the app):
  - environment `SHELLYLANMAN_DATA`, `SHELLYLANMAN_INGRESS` (`172.30.32.1:8099`) and
    `SHELLYLANMAN_INGRESS_FROM` (default `172.30.32.2`, the Supervisor);
  - user `shellylanman` (uid 10001) and the binary at `/usr/local/bin/shellylanman`;
  - the image `HEALTHCHECK` (`shellylanman -healthcheck`, following the port in the settings);
  - a web UI that works under a path prefix (relative URLs) and `GET /api/v1/status`
    reporting `"ingress": true` for requests through ingress.
- **Releasing:** release ShellyLanMan first (its tag publishes the base image), then bump
  `version` in `shellylanman/config.yaml` and `SHELLYLANMAN_VERSION` in
  `shellylanman/Dockerfile`, add the changelog entry and tag this repository with the
  same version. The workflow builds and pushes the app image; Home Assistant offers the
  update once `config.yaml` on `main` has the new version.

## The integration

**Needs ShellyLanMan 0.5.0 or newer** (`instanceId` in `/api/v1/about`). Home Assistant
2026.9 or newer (`hacs.json`); tested against 2026.9.4 and the newest release.

What it uses of ShellyLanMan (a change there is a breaking change for the integration):

| Call | For |
|---|---|
| `GET /api/v1/about` → `instanceId`, `version` | unique id of the entry, version sensor |
| `GET /api/v1/devices` (every 30 s) → `id` (MAC), `name`, `hostname`, `typeName`, `status`, `ip`, `gen`, `error`, `rebootRequired` | status sensors, counters, device matching |
| `GET /api/v1/devices` → `port`, `battery`, `protected` (0.7.0) | the list *Add Shellys to Home Assistant* |
| `GET /api/v1/devices/{id}/credentials` (0.7.0; MCP token at access *configure*, or the app's loopback listener `127.0.0.1:8097`) | the password of a protected Shelly for the Shelly integration's credentials step |
| Home Assistant's Shelly config flow: steps `confirm_discovery`, `user` (field `device` = `manual`), `user_manual` (`host`, `port`, `verify_ssl`), `credentials` (`password`; Gen1 also `username`) | adding Shellys; tested against the real flow on both Home Assistant versions |
| `GET /api/v1/backups` → `deviceId`, `time` | last backup sensor |
| `POST /api/v1/backup` `{"ids": [...]}` → `{"results": [{"result": "ok" / "queued" / "stored" / "fail", "message"}]}` | backup button |
| `GET /api/v1/checklist` (every 30 min) → the ChecklistRow cells | checklist binary sensors |
| `POST /api/v1/scan` | rescan button |
| `POST /mcp` with the bearer token: `tools/list`, `tools/call` | the LLM API for Assist |
| `Authorization: Bearer <MCP token>` on every `/api/v1` call; `401` with `login required` when ShellyLanMan has a UI password (0.9.0) and no valid token came | a ShellyLanMan with a password: the token is then needed; a read-only token allows reading, the backup and rescan buttons need *control* or *configure* |

It polls on purpose and does not keep ShellyLanMan's WebSocket open: an open
WebSocket counts as a viewer, and with viewers ShellyLanMan polls every device every
two seconds.

**App discovery** (ShellyLanMan 0.5.0+, app `discovery:`): `shellylanman`
`{"url": "http://127.0.0.1:<port>"}` and `mcp` `{"url": "http://127.0.0.1:8097/mcp"}`,
sent again after a port change (the integration then updates its URL).

## Where decisions are recorded

Design and decisions: `docs/phase-11-ha-mcp.md` and `DECISIONS.md` §20 in the
ShellyLanMan repository.
