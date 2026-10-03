"""Constants of the ShellyLanMan integration."""

from __future__ import annotations

from datetime import timedelta
import re
from typing import Any, Final

from homeassistant.helpers import config_validation as cv

DOMAIN: Final = "shellylanman"

CONF_MCP_TOKEN: Final = "mcp_token"

# State from ShellyLanMan's own cache: cheap, it does not touch the devices.
SCAN_INTERVAL: Final = timedelta(seconds=30)
# The checklist costs one RPC per device: read it seldom.
CHECKLIST_INTERVAL: Final = timedelta(minutes=30)

# Home Assistant 2026.9 validates with voluptuous, later versions with probatio
# (same API). Use whichever Home Assistant itself uses.
vol = getattr(cv, "vol", None) or cv.probatio  # type: ignore[attr-defined]

# "searching": listed before a rescan, not found again yet (ShellyLanMan 0.6.0).
STATUSES: Final = ["online", "offline", "login", "reading", "error", "ghost", "searching"]
_MAC = re.compile(r"[0-9A-Fa-f]{12}")


def is_mac(value: Any) -> bool:
    """True for an identified device's id: its MAC, twelve hex digits."""
    return isinstance(value, str) and _MAC.fullmatch(value) is not None


# Devices that need a look: they answer with an error or want a password.
ATTENTION: Final = {"error", "login"}
