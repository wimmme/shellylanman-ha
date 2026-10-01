#!/bin/sh
# Entry point of the Home Assistant app.
#
# The Supervisor mounts the app's /data as root; ShellyLanMan runs as its own
# user, so /data is handed to that user first. Then ShellyLanMan starts with
# the ingress listener on the Docker gateway (reached by Home Assistant's
# ingress; it accepts only the Supervisor, 172.30.32.2) and its normal LAN
# port as set in its own settings (default 3082).
set -eu

chown -R shellylanman:shellylanman /data

export SHELLYLANMAN_DATA=/data
export SHELLYLANMAN_INGRESS="${SHELLYLANMAN_INGRESS:-172.30.32.1:8099}"

# Option mcp_local (default on): ShellyLanMan's MCP server also on 127.0.0.1
# without token, for Home Assistant on this host (its MCP client cannot send a
# token). Only processes on this machine reach it; MCP must be enabled in
# ShellyLanMan and its access level applies.
if ! grep -Eq '"mcp_local" *: *false' /data/options.json 2>/dev/null; then
  export SHELLYLANMAN_MCP_LOCAL="${SHELLYLANMAN_MCP_LOCAL:-127.0.0.1:8097}"
fi

exec su-exec shellylanman /usr/local/bin/shellylanman
