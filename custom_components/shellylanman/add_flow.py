"""The dialog "Add Shellys to Home Assistant" (ShellyLanMan DECISIONS P13-4).

One pair of steps — the list, then the result — used by the integration's
options flow (Configure) and by the repair issue "Shellys not in Home Assistant".
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntryState, OptionsFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv, issue_registry as ir

from .const import DOMAIN, vol
from .shelly_add import ADDABLE, DISCOVERED, MISSED, OFFLINE, PASSWORD, Result, add, candidates

if TYPE_CHECKING:
    from . import RuntimeData

ISSUE = "shellys_missing"

# The reason after each name in the list (multi-select labels cannot be translated
# through strings.json).
_STATES: dict[str, dict[str, str]] = {
    "en": {DISCOVERED: "discovered by Home Assistant", PASSWORD: "discovered, needs its password",
           MISSED: "not offered by Home Assistant", OFFLINE: "not answering now"},
    "nl": {DISCOVERED: "ontdekt door Home Assistant", PASSWORD: "ontdekt, wachtwoord nodig",
           MISSED: "niet aangeboden door Home Assistant", OFFLINE: "antwoordt nu niet"},
}
_OUTCOMES: dict[str, dict[str, str]] = {
    "en": {"added": "added", "password": "needs its password — enter it under Settings → Devices & services → Discovered",
           "failed": "not added"},
    "nl": {"added": "toegevoegd", "password": "wachtwoord nodig — vul het in onder Instellingen → Apparaten & diensten → Ontdekt",
           "failed": "niet toegevoegd"},
}


def _texts(hass: HomeAssistant, table: dict[str, dict[str, str]]) -> dict[str, str]:
    return table.get((hass.config.language or "en").split("-")[0], table["en"])


def issue_id(entry_id: str) -> str:
    """The repair issue of one ShellyLanMan entry."""
    return f"{ISSUE}_{entry_id}"


@callback
def update_issue(hass: HomeAssistant, entry_id: str, rt: RuntimeData) -> None:
    """Raise the repair issue while Shellys can be added, clear it when none can."""
    n = sum(1 for c in candidates(hass, rt.state.data.devices) if c.state in ADDABLE)
    if n:
        ir.async_create_issue(
            hass, DOMAIN, issue_id(entry_id), is_fixable=True, is_persistent=False,
            severity=ir.IssueSeverity.WARNING, translation_key=ISSUE,
            translation_placeholders={"count": str(n)}, data={"entry_id": entry_id},
        )
    else:
        ir.async_delete_issue(hass, DOMAIN, issue_id(entry_id))


class AddShellysSteps:
    """Steps "add" and "result"; the flow provides runtime() and done()."""

    hass: HomeAssistant
    _results: list[Result]

    def runtime(self) -> RuntimeData | None:
        raise NotImplementedError

    def done(self) -> FlowResult:
        raise NotImplementedError

    async def async_step_add(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """The Shellys ShellyLanMan knows and Home Assistant does not have; tick, then add."""
        rt = self.runtime()
        if rt is None:
            return self.async_abort(reason="not_loaded")  # type: ignore[attr-defined]
        found = candidates(self.hass, rt.state.data.devices)
        addable = [c for c in found if c.state in ADDABLE]
        if not addable:
            return self.async_abort(reason="nothing_to_add")  # type: ignore[attr-defined]
        if user_input is not None:
            chosen = [c for c in addable if c.id in set(user_input.get("devices") or [])]
            if chosen:
                self._results = await add(self.hass, rt.client, chosen)
                await rt.state.async_request_refresh()
                return await self.async_step_result()
        states = _texts(self.hass, _STATES)
        options = {c.id: f"{c.label} — {states[c.state]}" for c in addable}
        offline = [c for c in found if c.state == OFFLINE]
        return self.async_show_form(  # type: ignore[attr-defined]
            step_id="add",
            data_schema=vol.Schema({vol.Required("devices", default=[c.id for c in addable]): cv.multi_select(options)}),
            description_placeholders={
                "count": str(len(addable)),
                "discovered": str(sum(1 for c in addable if c.state in (DISCOVERED, PASSWORD))),
                "missed": str(sum(1 for c in addable if c.state == MISSED)),
                "offline": ", ".join(c.label for c in offline) or "—",
            },
        )

    async def async_step_result(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """What happened to each Shelly."""
        if user_input is not None:
            return self.done()
        outcomes = _texts(self.hass, _OUTCOMES)
        lines = []
        for r in sorted(self._results, key=lambda r: (r.outcome != "added", r.candidate.name.lower())):
            line = f"- {r.candidate.label}: {outcomes[r.outcome]}"
            if r.detail:
                line += f" ({r.detail})"
            lines.append(line)
        return self.async_show_form(  # type: ignore[attr-defined]
            step_id="result",
            data_schema=vol.Schema({}),
            description_placeholders={
                "added": str(sum(1 for r in self._results if r.outcome == "added")),
                "total": str(len(self._results)),
                "details": "\n".join(lines),
            },
        )


class ShellyLanManOptionsFlow(AddShellysSteps, OptionsFlow):
    """Configure → Add Shellys to Home Assistant."""

    def runtime(self) -> RuntimeData | None:
        entry = self.config_entry
        return entry.runtime_data if entry.state is ConfigEntryState.LOADED else None

    def done(self) -> FlowResult:
        return self.async_create_entry(data=dict(self.config_entry.options))

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """The only option: add Shellys."""
        return await self.async_step_add()
