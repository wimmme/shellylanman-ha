# Roadmap

What is planned for the Home Assistant app and integration. ShellyLanMan itself has
its own roadmap: [`docs/roadmap.md`](https://github.com/wimmme/shellylanman/blob/main/docs/roadmap.md).
Ideas and wishes are welcome as a [GitHub issue](https://github.com/wimmme/shellylanman-ha/issues).

## Now: towards 1.0.0

- Home Assistant's [integration quality scale](https://contributors.home-assistant.io/core/quality-scale/):
  **Bronze and Silver are met** (self-assessment in [`QUALITY_SCALE.md`](QUALITY_SCALE.md)).
- The integration in ShellyLanMan's 8 languages.

## After Home Assistant 2026.11 (HACS becomes the Marketplace)

- `categories` in the integration's manifest, so the Marketplace shows it under the
  right headings. Home Assistant 2026.10's hassfest does not know the key yet.
- Check that the *Open in HACS* button in the README opens the Marketplace, and
  update the install steps if it does not.

## Quality scale Gold

Each point is a rule of the scale; together they make Gold.

**In the integration**

- **Diagnostics**: a download under the integration with ShellyLanMan's version,
  the devices and the last poll, the MCP token and passwords left out.
- **Icons** per entity in `icons.json` (status, backup, checklist items), instead of
  the defaults.
- **Translated error messages**: the messages of the buttons and of Assist come from
  the translations, not from fixed English text.

**In the documentation**

- How and how often the data is updated (every 30 s, the checklist every 30 min).
- Which Shellys are supported: the ones ShellyLanMan supports (Gen1 to Gen4, BLU
  through a gateway).
- Examples: automations on *Devices needing attention*, *Last configuration backup*
  and the checklist.
- Use cases, known limitations and troubleshooting (ShellyLanMan not reachable, a
  password set later, a Shelly that is not added).

## Quality scale Platinum

- **Strict typing**: the integration fully typed and checked with strict mypy in CI.
  The other two Platinum rules (an async client, Home Assistant's own web session)
  are already met.
