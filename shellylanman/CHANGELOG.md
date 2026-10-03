# Changelog

## 0.6.1

Runs ShellyLanMan 0.6.1.

- Charts follow the selection too: devices ticked on Devices, Checklist or Firmware are
  charted when you open Charts from the menu.

All changes: [ShellyLanMan changelog](https://github.com/wimmme/shellylanman/blob/main/CHANGELOG.md).

## 0.6.0

Runs ShellyLanMan 0.6.0.

- One selection for Devices, Checklist and Firmware: tick devices on one page, the
  others show them (or all, with one click). Checklist has checkboxes.
- Every button says what it does, and a grey button says why it is not available.
- *Rescan*: known devices show *searching* until they are found again, instead of
  *archived* at once.
- Firmware shows its rows at once and fills them in per device.
- The Home Assistant look is the default everywhere; on phones the navigation is a ☰
  menu.
- Device web pages open in a new tab or in this tab (Settings → Appearance), for wall
  tablets with a kiosk browser.
- The app's log says when it announced itself to Home Assistant.

All changes: [ShellyLanMan changelog](https://github.com/wimmme/shellylanman/blob/main/CHANGELOG.md).

## 0.5.0

Runs ShellyLanMan 0.5.0.

- Announces itself to Home Assistant: the ShellyLanMan integration and Home
  Assistant's own MCP client (Assist) are offered as discovered.
- Option *MCP for Home Assistant without token* (on by default): ShellyLanMan's MCP
  server also on `127.0.0.1:8097` without token, for Home Assistant on this host.

All changes: [ShellyLanMan changelog](https://github.com/wimmme/shellylanman/blob/main/CHANGELOG.md).

## 0.4.0

Runs ShellyLanMan 0.4.0. First version of the app.

- ShellyLanMan inside Home Assistant OS, in the sidebar through ingress.
- On the host network, so discovery by mDNS works.
- Its data is part of Home Assistant's backups.

All changes: [ShellyLanMan changelog](https://github.com/wimmme/shellylanman/blob/main/CHANGELOG.md).
