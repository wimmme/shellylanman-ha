# Roadmap

What is planned for the Home Assistant app and integration. ShellyLanMan itself has
its own roadmap: [`docs/roadmap.md`](https://github.com/wimmme/shellylanman/blob/main/docs/roadmap.md).
Ideas and wishes are welcome as a [GitHub issue](https://github.com/wimmme/shellylanman-ha/issues).

## Now: towards 1.0.0

- Home Assistant's [integration quality scale](https://contributors.home-assistant.io/core/quality-scale/):
  **every tier is met, Platinum included** (self-assessment in [`QUALITY_SCALE.md`](QUALITY_SCALE.md)):
  diagnostics, translated error messages, icons, strict typing, and the README sections
  on updates, supported Shellys, use cases, examples, limitations and troubleshooting.
- The integration in ShellyLanMan's 8 languages.

## After Home Assistant 2026.11 (HACS becomes the Marketplace)

- `categories` in the integration's manifest, so the Marketplace shows it under the
  right headings. Home Assistant 2026.10's hassfest does not know the key yet.
- Check that the *Open in HACS* button in the README opens the Marketplace, and
  update the install steps if it does not.
- Release these as **integration 1.0.0** (decided 2026-10-29): the integration's first
  change after ShellyLanMan 1.0.0, so users get one update that brings something.
