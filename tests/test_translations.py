"""Every language has every text, with the same placeholders (like ShellyLanMan's catalogues)."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import pytest
import yaml

from custom_components.shellylanman.add_flow import _OUTCOMES, _STATES

COMPONENT = Path(__file__).parent.parent / "custom_components" / "shellylanman"
APP = Path(__file__).parent.parent / "shellylanman" / "translations"
LANGUAGES = ["bg", "cs", "de", "en", "es", "fr", "it", "nl", "zh-Hans"]


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


def test_app_options() -> None:
    """The app's option texts (Supervisor) in the same languages, every option named and described."""
    assert sorted(p.stem for p in APP.glob("*.yaml")) == LANGUAGES
    en = yaml.safe_load((APP / "en.yaml").read_text(encoding="utf-8"))
    for language in LANGUAGES:
        texts = yaml.safe_load((APP / f"{language}.yaml").read_text(encoding="utf-8"))
        assert texts.keys() == en.keys() and texts["configuration"].keys() == en["configuration"].keys(), language
        for option, text in texts["configuration"].items():
            assert text.keys() == {"name", "description"} and all(v.strip() for v in text.values()), (language, option)


def test_icons() -> None:
    """An icon for every entity, and none for an entity that does not exist."""
    icons = json.loads((COMPONENT / "icons.json").read_text(encoding="utf-8"))["entity"]
    names = json.loads((COMPONENT / "strings.json").read_text(encoding="utf-8"))["entity"]
    assert {p: sorted(e) for p, e in icons.items()} == {p: sorted(e) for p, e in names.items()}
    status = icons["sensor"]["status"]["state"]
    assert sorted(status) == sorted(names["sensor"]["status"]["state"])


def test_exception_keys() -> None:
    """Every translation_key the code raises has a text, and every text is used."""
    code = "".join(p.read_text(encoding="utf-8") for p in COMPONENT.glob("*.py"))
    used = set(re.findall(r'translation_key="(\w+)"', code))
    assert used == set(json.loads((COMPONENT / "strings.json").read_text(encoding="utf-8"))["exceptions"])


def test_add_dialog_texts() -> None:
    """The texts the add dialog builds itself: one table per language (Home Assistant's zh-Hans is "zh")."""
    wanted = sorted(lang.split("-")[0] for lang in LANGUAGES)
    for table in (_STATES, _OUTCOMES):
        assert sorted(table) == wanted
        assert all(table[lang].keys() == table["en"].keys() for lang in table)
