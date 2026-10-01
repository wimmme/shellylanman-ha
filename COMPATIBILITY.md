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

## The integration (planned, Phase 11c)

It will talk to ShellyLanMan's REST API (`/api/v1`), WebSocket (`/ws`) and MCP server
(`/mcp`). Supported ShellyLanMan versions will be listed here, with the API it needs.

## Where decisions are recorded

Design and decisions: `docs/phase-11-ha-mcp.md` and `DECISIONS.md` §20 in the
ShellyLanMan repository.
