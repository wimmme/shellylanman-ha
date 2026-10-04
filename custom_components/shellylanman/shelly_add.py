"""Add the Shellys ShellyLanMan knows to Home Assistant's Shelly integration.

DECISIONS P13-1..4 of ShellyLanMan (docs/phase-13-option-b.md there). Everything
goes through the Shelly integration's own config flows, so its checks, its entry
data and its de-duplication by MAC stay in charge:

- a Shelly Home Assistant already discovered (a zeroconf flow waiting in
  ``confirm_discovery``) is confirmed; one waiting in ``credentials`` gets the
  password ShellyLanMan stores;
- a Shelly Home Assistant missed is added through the Shelly integration's manual
  flow, answered as the user would: device list → "manual" → host and port →
  credentials when the device asks for them.

Nothing is added without the user's choice in the options or repair flow.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.config_entries import SOURCE_IGNORE, SOURCE_USER
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import AbortFlow, FlowResultType, UnknownFlow

from .api import ShellyLanManClient
from .const import is_mac

_LOGGER = logging.getLogger(__name__)

SHELLY = "shelly"
# The Shelly integration's manual flow (homeassistant/components/shelly/config_flow.py).
STEP_PICK, STEP_MANUAL, STEP_CREDENTIALS, STEP_CONFIRM = "user", "user_manual", "credentials", "confirm_discovery"
MANUAL_ENTRY = "manual"
WIFI_GENS = ("1", "2", "3", "4")
# How many Shellys are added at the same time.
PARALLEL = 4

# Why a Shelly is listed (and whether it can be added now).
DISCOVERED = "discovered"  # Home Assistant found it, waits for a click
PASSWORD = "password"  # Home Assistant found it, waits for its password
MISSED = "missed"  # Home Assistant did not offer it
OFFLINE = "offline"  # not answering now (ShellyLanMan's status)
ADDABLE = (DISCOVERED, PASSWORD, MISSED)


@dataclass
class Candidate:
    """A Shelly known to ShellyLanMan that is not in the Shelly integration."""

    id: str  # MAC, upper case
    name: str
    host: str
    port: int
    gen: str
    protected: bool
    battery: bool
    state: str
    flow_id: str | None = None

    @property
    def label(self) -> str:
        """Name and address, for the list."""
        return f"{self.name} ({self.host})" if self.port == 80 else f"{self.name} ({self.host}:{self.port})"


@dataclass
class Result:
    """What happened to one Shelly."""

    candidate: Candidate
    outcome: str  # "added", "password", "failed"
    detail: str = ""


@callback
def candidates(hass: HomeAssistant, devices: dict[str, dict[str, Any]]) -> list[Candidate]:
    """The Wi-Fi Shellys ShellyLanMan knows and the Shelly integration does not have.

    Ignored ones (the user chose "Ignore" in Home Assistant) are left out.
    """
    have = {(e.unique_id or "").upper() for e in hass.config_entries.async_entries(SHELLY, include_ignore=True, include_disabled=True)}
    flows: dict[str, dict[str, Any]] = {}
    for flow in hass.config_entries.flow.async_progress_by_handler(SHELLY):
        uid = (flow["context"].get("unique_id") or "").upper()
        if uid and flow["context"].get("source") != SOURCE_IGNORE:
            flows[uid] = dict(flow)
    out: list[Candidate] = []
    for dev_id, dev in devices.items():
        if not is_mac(dev_id) or dev.get("gen") not in WIFI_GENS or dev_id.upper() in have:
            continue
        status = dev.get("status")
        if status in ("ghost", "searching"):
            continue
        flow = flows.get(dev_id.upper())
        if flow and flow.get("step_id") == STEP_CONFIRM:
            state = DISCOVERED
        elif flow and flow.get("step_id") == STEP_CREDENTIALS:
            state = PASSWORD
        elif status in ("online", "login", "reading"):
            state = MISSED
        else:
            state = OFFLINE
        out.append(Candidate(
            id=dev_id.upper(),
            name=dev.get("name") or dev.get("hostname") or dev_id,
            host=dev.get("ip", ""),
            port=int(dev.get("port") or 80),
            gen=str(dev.get("gen")),
            protected=bool(dev.get("protected")),
            battery=bool(dev.get("battery")),
            state=state,
            flow_id=flow["flow_id"] if flow and state in (DISCOVERED, PASSWORD) else None,
        ))
    out.sort(key=lambda c: (ADDABLE.index(c.state) if c.state in ADDABLE else 9, c.name.lower()))
    return out


def _credentials_input(gen: str, cred: dict[str, Any]) -> dict[str, Any]:
    """The Shelly credentials step's fields: Gen2+ only the password (user admin)."""
    if gen == "1":
        return {"username": cred.get("user") or "admin", "password": cred.get("password", "")}
    return {"password": cred.get("password", "")}


async def _finish(hass: HomeAssistant, c: Candidate, client: ShellyLanManClient, result: dict[str, Any]) -> Result:
    """Answer the Shelly flow's steps until it creates the entry, aborts or needs what we lack."""
    for _ in range(6):  # user → user_manual → credentials → entry, with room to spare
        kind = result.get("type")
        if kind == FlowResultType.CREATE_ENTRY:
            return Result(c, "added")
        if kind == FlowResultType.ABORT:
            reason = result.get("reason", "")
            return Result(c, "added" if reason == "already_configured" else "failed", "" if reason == "already_configured" else reason)
        if kind != FlowResultType.FORM:
            return _abandon(hass, result, Result(c, "failed", f"unexpected {kind}"))
        step, errors = result.get("step_id"), result.get("errors") or {}
        flow_id = result["flow_id"]
        if step == STEP_PICK:
            result = await hass.config_entries.flow.async_configure(flow_id, {"device": MANUAL_ENTRY})
        elif step == STEP_MANUAL:
            if errors:
                return _abandon(hass, result, Result(c, "failed", errors.get("base", "error")))
            result = await hass.config_entries.flow.async_configure(flow_id, {"host": c.host, "port": c.port, "verify_ssl": False})
        elif step == STEP_CREDENTIALS:
            if errors:
                return _abandon(hass, result, Result(c, "failed", errors.get("base", "invalid_auth")))
            cred = await client.credentials(c.id)
            if not cred:
                # Discovered by Home Assistant: the flow stays under "Discovered" for the
                # user to type the password; our own manual flow is ended.
                if c.state == PASSWORD:
                    return Result(c, "password")
                return _abandon(hass, result, Result(c, "password"))
            result = await hass.config_entries.flow.async_configure(flow_id, _credentials_input(c.gen, cred))
        elif step == STEP_CONFIRM:
            result = await hass.config_entries.flow.async_configure(flow_id, {})
        else:
            return _abandon(hass, result, Result(c, "failed", f"unexpected step {step}"))
    return _abandon(hass, result, Result(c, "failed", "too many steps"))


def _abandon(hass: HomeAssistant, result: dict[str, Any], r: Result) -> Result:
    """End a flow we started and cannot finish (never one Home Assistant discovered)."""
    if r.candidate.flow_id is None and result.get("flow_id"):
        try:
            hass.config_entries.flow.async_abort(result["flow_id"])
        except UnknownFlow:
            pass
    return r


async def add_one(hass: HomeAssistant, client: ShellyLanManClient, c: Candidate) -> Result:
    """Add one Shelly to the Shelly integration."""
    try:
        if c.flow_id:  # Home Assistant's own discovery
            flow = next((f for f in hass.config_entries.flow.async_progress_by_handler(SHELLY) if f["flow_id"] == c.flow_id), None)
            if flow is None:
                return Result(c, "failed", "the discovery is gone")
            return await _finish(hass, c, client, {"type": FlowResultType.FORM, "flow_id": c.flow_id, "step_id": flow.get("step_id")})
        result = await hass.config_entries.flow.async_init(SHELLY, context={"source": SOURCE_USER})
        return await _finish(hass, c, client, dict(result))
    except AbortFlow as err:
        return Result(c, "added" if err.reason == "already_configured" else "failed", "" if err.reason == "already_configured" else err.reason)
    except Exception as err:  # noqa: BLE001 - one Shelly must not stop the others
        _LOGGER.warning("Adding %s (%s) to the Shelly integration failed: %s", c.name, c.host, err)
        return Result(c, "failed", str(err) or type(err).__name__)


async def add(hass: HomeAssistant, client: ShellyLanManClient, chosen: list[Candidate]) -> list[Result]:
    """Add the chosen Shellys, a few at a time."""
    sem = asyncio.Semaphore(PARALLEL)

    async def one(c: Candidate) -> Result:
        async with sem:
            return await add_one(hass, client, c)

    return list(await asyncio.gather(*(one(c) for c in chosen)))
