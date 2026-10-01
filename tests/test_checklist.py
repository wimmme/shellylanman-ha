"""Checklist cells as on/off values (ShellyLanMan's ChecklistRow conventions)."""

from custom_components.shellylanman.checklist import NOT_APPLICABLE, cell_detail, cell_state


def test_cell_state() -> None:
    assert cell_state(True) is True
    assert cell_state(False) is False
    assert cell_state("✓") is True
    assert cell_state("✗") is False
    assert cell_state("-") is NOT_APPLICABLE
    assert cell_state(None) is NOT_APPLICABLE
    assert cell_state([]) is True  # BLE on, relays nothing
    assert cell_state(2) is True  # range extender with two clients
    assert cell_state("socket") is True  # log target
    assert cell_state("-80") is True  # roaming threshold


def test_cell_detail() -> None:
    assert cell_detail("socket, mqtt") == "socket, mqtt"
    assert cell_detail("stable") == "stable"
    assert cell_detail(["a", "b"]) == "2"
    assert cell_detail(3) == "3"
    assert cell_detail(True) is None
    assert cell_detail("✓") is None
    assert cell_detail("-") is None
