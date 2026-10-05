# Security policy

## Reporting a vulnerability

Please do not open a public issue for security problems. Use GitHub's private
vulnerability reporting on https://github.com/wimmme/shellylanman-ha/security.
Include what is affected, how to reproduce it, and the impact you see. Problems in
ShellyLanMan itself (the web application the app runs) go to
https://github.com/wimmme/shellylanman/security.

Only the latest release receives fixes.

## What the integration and the app do

- The **app** runs ShellyLanMan inside Home Assistant. Through the sidebar
  (ingress) it is behind Home Assistant's login; its own LAN port behaves like a
  standalone ShellyLanMan — see ShellyLanMan's
  [SECURITY.md](https://github.com/wimmme/shellylanman/blob/main/SECURITY.md).
- The **integration** reads ShellyLanMan's API. With the MCP token (stored in the
  config entry) it also uses ShellyLanMan's tools for Assist and receives the
  credentials of protected Shellys when it adds them to Home Assistant's Shelly
  integration; ShellyLanMan hands those out only with the token at access level
  *configure*, or on the app's loopback listener.
- Nothing leaves your LAN: no cloud, no telemetry.

## How this repository is checked

Secret scanning with push protection, Dependabot alerts and security updates,
CodeQL code scanning (Python, workflows), and hassfest and HACS validation in CI.
