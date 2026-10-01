"""ShellyLanMan's checklist cells as on/off values.

The cells follow ShellyScanner's checklist table (ShellyLanMan's
service.ChecklistRow): true/false, "✓"/"✗", "-" (not applicable to the
device's generation), null (the device lacks the setting), a list (BLE
gateways), a number (range extender clients) or a text (log targets,
firmware update stage, roaming threshold).
"""

from __future__ import annotations

from typing import Any, Final

NOT_APPLICABLE: Final = object()

# Checklist key in ShellyLanMan → entity key here. "led" is ShellyScanner's
# "LED off" column (Gen1). "wifi1" is "static IP on Wi-Fi 1".
ITEMS: Final = {
    "eco": "eco_mode",
    "led": "led_off",
    "logs": "debug_log",
    "ble": "bluetooth",
    "ap": "access_point",
    "roaming": "roaming",
    "wifi1": "static_ip",
    "extender": "range_extender",
    "autoFW": "auto_firmware_update",
}


def cell_state(value: Any) -> Any:
    """True / False for a checklist cell, NOT_APPLICABLE when it does not apply."""
    if value is None or value == "-":
        return NOT_APPLICABLE
    if isinstance(value, bool):
        return value
    if value == "✓":
        return True
    if value == "✗":
        return False
    if isinstance(value, list):  # BLE: the gateway relays these BLU devices — Bluetooth is on
        return True
    if isinstance(value, (int, float)):  # range extender: number of clients — it is on
        return True
    if isinstance(value, str) and value:  # log targets, update stage, roaming threshold — on
        return True
    return NOT_APPLICABLE


def cell_detail(value: Any) -> str | None:
    """Extra detail worth an attribute: log targets, update stage, roaming threshold."""
    if isinstance(value, str) and value not in ("", "-", "✓", "✗"):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, list):
        return str(len(value))
    return None
