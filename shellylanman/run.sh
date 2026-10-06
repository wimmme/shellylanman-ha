#!/bin/sh
# Entry point of the Home Assistant app.
#
# The Supervisor mounts the app's /data as root; ShellyLanMan runs as its own
# user, so /data is handed to that user first. The app's options
# (/data/options.json) become ShellyLanMan's environment:
#   port            -> SHELLYLANMAN_PORT      web UI and API on the LAN (default 3082)
#   mcp_local       -> SHELLYLANMAN_MCP_LOCAL on or off
#   mcp_local_port  -> its port on 127.0.0.1  (default 8097)
# The ingress listener (Home Assistant's sidebar) is on the Docker gateway; its
# port is the one the Supervisor chose (ingress_port: 0), which ShellyLanMan
# asks the Supervisor for ("172.30.32.1:0"). It accepts only the Supervisor.
set -eu

chown -R shellylanman:shellylanman /data

# opt NAME DEFAULT: a number or true/false from /data/options.json.
opt() {
  v=$(tr -d '\r\n' < /data/options.json 2>/dev/null | sed -n "s/.*[{,][[:space:]]*\"$1\"[[:space:]]*:[[:space:]]*\([0-9a-z]*\).*/\1/p")
  echo "${v:-$2}"
}

export SHELLYLANMAN_DATA=/data
export SHELLYLANMAN_PORT="${SHELLYLANMAN_PORT:-$(opt port 3082)}"
export SHELLYLANMAN_INGRESS="${SHELLYLANMAN_INGRESS:-172.30.32.1:0}"

# MCP and the integration's calls without token on 127.0.0.1, for Home Assistant
# on this host (its MCP client cannot send a token). Only processes on this
# machine reach it; MCP must be enabled in ShellyLanMan and its access level applies.
if [ "$(opt mcp_local true)" != "false" ]; then
  export SHELLYLANMAN_MCP_LOCAL="${SHELLYLANMAN_MCP_LOCAL:-127.0.0.1:$(opt mcp_local_port 8097)}"
fi

exec su-exec shellylanman /usr/local/bin/shellylanman
