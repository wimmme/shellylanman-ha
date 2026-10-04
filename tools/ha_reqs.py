"""Print the Python requirements of Home Assistant integrations (and their dependencies).

The integration tests run Home Assistant's real Shelly config flow; its
requirements (aioshelly, …) are not part of pytest-homeassistant-custom-component.
Usage: pip install $(python tools/ha_reqs.py shelly)
"""

import json
import pathlib
import sys

import homeassistant.components as components

base = pathlib.Path(components.__path__[0])
seen, reqs, todo = set(), [], list(sys.argv[1:])
while todo:
    domain = todo.pop()
    if domain in seen:
        continue
    seen.add(domain)
    manifest = json.loads((base / domain / "manifest.json").read_text())
    reqs += manifest.get("requirements", [])
    todo += manifest.get("dependencies", [])
print(" ".join(sorted(set(reqs))))
