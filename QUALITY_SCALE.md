# Integration quality scale

Home Assistant's [integration quality scale](https://contributors.home-assistant.io/core/quality-scale/)
grades core integrations: Bronze, Silver, Gold, Platinum. It is awarded to core
integrations in review; a custom integration cannot claim a tier. This is a
self-assessment of `custom_components/shellylanman` against the
[rules](https://contributors.home-assistant.io/core/quality-scale/rules/), so you know
what to expect and what is still open. Last checked: 2026-10-22, version 0.9.10 + main.

**done** — the rule is met · **exempt** — the rule does not apply, with the reason ·
**todo** — not met yet. The plan for the open rules is in [`ROADMAP.md`](ROADMAP.md).

## Bronze — met

| Rule | | How |
|---|---|---|
| action-setup | exempt | The integration registers no actions |
| appropriate-polling | done | State every 30 s from ShellyLanMan's cache (costs the devices nothing), checklist every 30 min |
| brands | done | `brand/icon.png` in the integration folder |
| common-modules | done | `coordinator.py`, `entity.py` |
| config-flow | done | By hand, from the app's discovery, reconfigure; every field has a `data_description` |
| config-flow-test-coverage | done | `config_flow.py` 100 % covered, errors and their recovery included |
| dependency-transparency | done | No requirements: only `aiohttp`, which Home Assistant ships |
| docs-actions | exempt | No actions |
| docs-conditions | exempt | No conditions |
| docs-high-level-description | done | README |
| docs-installation-instructions | done | README, *Install the integration* |
| docs-removal-instructions | done | README, *Remove the integration* |
| docs-triggers | exempt | No triggers |
| entity-event-setup | exempt | Entities subscribe to no events; coordinators only |
| entity-unique-id | done | `<device id>-<key>` and `<instance id>-<key>` |
| has-entity-name | done | All entities, names from translations |
| runtime-data | done | `ConfigEntry.runtime_data` |
| test-before-configure | done | The flow reads `/api/v1/about` (and, with a token, the MCP tools) first |
| test-before-setup | done | `ConfigEntryNotReady` when ShellyLanMan cannot be reached |
| unique-config-entry | done | Unique id = ShellyLanMan's instance id |

## Silver — met

| Rule | | How |
|---|---|---|
| action-exceptions | exempt | No actions (the buttons raise `HomeAssistantError` all the same) |
| config-entry-unloading | done | `async_unload_entry`, tested |
| docs-configuration-parameters | exempt | *Configure* has no settings: it is the *Add Shellys* dialog, described in the README |
| docs-installation-parameters | done | URL and MCP token, in the README and the form |
| entity-unavailable | done | Coordinator entities |
| integration-owner | done | `codeowners` |
| log-when-unavailable | done | The coordinators log once on loss and once on return |
| parallel-updates | done | 0 for the sensors (coordinator), 1 for the buttons (one backup at a time) |
| reauthentication-flow | done | A refused MCP token, or a UI password set after set-up, asks for a new token |
| test-coverage | done | 99 % overall, every module 96 % or more |

## Gold

| Rule | | How |
|---|---|---|
| devices | done | A device per Shelly (linked to the Shelly integration's by MAC) and one for ShellyLanMan |
| diagnostics | todo | |
| discovery | done | From the app (Supervisor discovery) |
| discovery-update-info | done | A new address from the app updates the entry |
| docs-data-update | todo | The intervals are not in the README |
| docs-examples | todo | |
| docs-known-limitations | todo | |
| docs-supported-devices | todo | The Shellys ShellyLanMan supports; not listed here |
| docs-supported-functions | done | README, the entity table |
| docs-troubleshooting | todo | |
| docs-use-cases | todo | Partly in the README |
| dynamic-devices | done | New Shellys get entities without a reload |
| entity-category | done | Per-device entities are diagnostic |
| entity-device-class | done | Status `enum`, last backup `timestamp` |
| entity-disabled-by-default | done | The checklist items |
| entity-translations | done | |
| exception-translations | todo | Button errors are plain text |
| icon-translations | todo | No `icons.json` |
| reconfiguration-flow | done | |
| repair-issues | done | *Shellys not in Home Assistant*, with a fix |
| stale-devices | done | A Shelly ShellyLanMan no longer lists can be deleted |

## Platinum

| Rule | | How |
|---|---|---|
| async-dependency | done | The client is the integration's own aiohttp code |
| inject-websession | done | `async_get_clientsession` |
| strict-typing | todo | No strict mypy run |
