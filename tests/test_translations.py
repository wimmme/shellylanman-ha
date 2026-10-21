"""Every language has every text, with the same placeholders (like ShellyLanMan's catalogues)."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import pytest

from custom_components.shellylanman.add_flow import _OUTCOMES, _STATES

COMPONENT = Path(__file__).parent.parent / "custom_components" / "shellylanman"
LANGUAGES = ["bg", "de", "en", "es", "fr", "it", "nl", "zh-Hans"]


def _flat(node: Any, prefix: str = "") -> dict[str, str]:
    if isinstance(node, dict):
        return {k: v for key, child in node.items() for k, v in _flat(child, f"{prefix}{key}.").items()}
    return {prefix.rstrip("."): node}


def _placeholders(text: str) -> set[str]:
    return set(re.findall(r"\{(\w+)\}", text))


STRINGS = _flat(json.loads((COMPONENT / "strings.json").read_text(encoding="utf-8")))


def test_languages() -> None:
    assert sorted(p.stem for p in (COMPONENT / "translations").glob("*.json")) == LANGUAGES


@pytest.mark.parametrize("language", LANGUAGES)
def test_same_keys_and_placeholders(language: str) -> None:
    texts = _flat(json.loads((COMPONENT / "translations" / f"{language}.json").read_text(encoding="utf-8")))
    assert texts.keys() == STRINGS.keys()
    for key, text in texts.items():
        assert text.strip(), key
        assert _placeholders(text) == _placeholders(STRINGS[key]), key


def test_english_is_strings_json() -> None:
    assert _flat(json.loads((COMPONENT / "translations" / "en.json").read_text(encoding="utf-8"))) == STRINGS


def test_add_dialog_texts() -> None:
    """The texts the add dialog builds itself: one table per language (Home Assistant's zh-Hans is "zh")."""
    wanted = sorted(lang.split("-")[0] for lang in LANGUAGES)
    for table in (_STATES, _OUTCOMES):
        assert sorted(table) == wanted
        assert all(table[lang].keys() == table["en"].keys() for lang in table)
