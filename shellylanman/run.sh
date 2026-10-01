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

exec su-exec shellylanman /usr/local/bin/shellylanman
