"""The answers to the Shelly integration's flow steps, one case at a time.

test_shelly_add.py runs the real Shelly flows for the usual paths; these cover
what those flows seldom do (errors, odd steps), with a stand-in flow manager.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

from homeassistant.data_entry_flow import AbortFlow, FlowResultType, UnknownFlow

from custom_components.shellylanman.shelly_add import (
    MISSED,
    PASSWORD,
    STEP_CREDENTIALS,
    STEP_MANUAL,
    Candidate,
    _credentials_input,
    _finish,
    add_one,
    candidates,
)


def _candidate(state: str = MISSED, flow_id: str | None = None) -> Candidate:
    return Candidate(id="AABBCC000001", name="Pump", host="192.0.2.1", port=8080, gen="2", protected=True,
                     battery=False, state=state, flow_id=flow_id)


def _hass(*answers: dict[str, Any], progress: list[dict[str, Any]] | None = None) -> MagicMock:
    hass = MagicMock()
    hass.config_entries.flow.async_configure = AsyncMock(side_effect=list(answers))
    hass.config_entries.flow.async_init = AsyncMock()
    hass.config_entries.flow.async_progress_by_handler.return_value = progress or []
    hass.config_entries.async_entries.return_value = []
    return hass


def _form(step: str, errors: dict[str, str] | None = None) -> dict[str, Any]:
    return {"type": FlowResultType.FORM, "flow_id": "f1", "step_id": step, "errors": errors}


def _client(cred: dict[str, Any] | None = None) -> MagicMock:
    client = MagicMock()
    client.credentials = AsyncMock(return_value=cred)
    return client


def test_candidates_states() -> None:
    """Ghosts are left out; a discovery waiting for its password is "password"."""
    progress = [{"flow_id": "d1", "step_id": STEP_CREDENTIALS, "context": {"unique_id": "aabbcc000001", "source": "zeroconf"}}]
    devices = {
        "AABBCC000001": {"gen": "2", "ip": "192.0.2.1", "status": "online", "name": "Locked"},
        "AABBCC000002": {"gen": "2", "ip": "192.0.2.2", "status": "ghost"},
    }
    found = candidates(_hass(progress=progress), devices)
    assert [(c.id, c.state, c.flow_id) for c in found] == [("AABBCC000001", PASSWORD, "d1")]
    assert found[0].label == "Locked (192.0.2.1)"
    assert _candidate().label == "Pump (192.0.2.1:8080)"


def test_credentials_input() -> None:
    assert _credentials_input("1", {"password": "pw"}) == {"username": "admin", "password": "pw"}
    assert _credentials_input("2", {"user": "admin", "password": "pw"}) == {"password": "pw"}


async def test_finish_outcomes() -> None:
    c = _candidate()
    assert (await _finish(_hass(), c, _client(), {"type": FlowResultType.ABORT, "reason": "already_configured"})).outcome == "added"
    r = await _finish(_hass(), c, _client(), {"type": FlowResultType.ABORT, "reason": "cannot_connect"})
    assert (r.outcome, r.detail) == ("failed", "cannot_connect")
    r = await _finish(_hass(), c, _client(), {"type": FlowResultType.EXTERNAL_STEP, "flow_id": "f1"})
    assert (r.outcome, r.detail) == ("failed", f"unexpected {FlowResultType.EXTERNAL_STEP}")
    r = await _finish(_hass(), c, _client(), _form(STEP_MANUAL, {"base": "cannot_connect"}))
    assert (r.outcome, r.detail) == ("failed", "cannot_connect")
    r = await _finish(_hass(), c, _client(), _form(STEP_CREDENTIALS, {"base": "invalid_auth"}))
    assert (r.outcome, r.detail) == ("failed", "invalid_auth")
    r = await _finish(_hass(), c, _client(), _form("bluetooth_confirm"))
    assert (r.outcome, r.detail) == ("failed", "unexpected step bluetooth_confirm")
    r = await _finish(_hass(*[_form(STEP_MANUAL)] * 6), c, _client(), _form(STEP_MANUAL))
    assert (r.outcome, r.detail) == ("failed", "too many steps")


async def test_finish_password_left_to_the_user() -> None:
    """No stored password: a discovery stays for the user, our own flow is ended."""
    hass = _hass()
    r = await _finish(hass, _candidate(PASSWORD, flow_id="d1"), _client(), _form(STEP_CREDENTIALS))
    assert r.outcome == "password"
    hass.config_entries.flow.async_abort.assert_not_called()
    hass.config_entries.flow.async_abort.side_effect = UnknownFlow  # already gone: fine
    r = await _finish(hass, _candidate(), _client(), _form(STEP_CREDENTIALS))
    assert r.outcome == "password"
    hass.config_entries.flow.async_abort.assert_called_once_with("f1")


async def test_add_one_errors() -> None:
    r = await add_one(_hass(), _client(), _candidate(PASSWORD, flow_id="gone"))
    assert (r.outcome, r.detail) == ("failed", "the discovery is gone")
    hass = _hass()
    hass.config_entries.flow.async_init.side_effect = AbortFlow("already_configured")
    assert (await add_one(hass, _client(), _candidate())).outcome == "added"
    hass.config_entries.flow.async_init.side_effect = AbortFlow("not_supported")
    r = await add_one(hass, _client(), _candidate())
    assert (r.outcome, r.detail) == ("failed", "not_supported")
    hass.config_entries.flow.async_init.side_effect = RuntimeError("boom")
    r = await add_one(hass, _client(), _candidate())
    assert (r.outcome, r.detail) == ("failed", "boom")
