# Lumi for Hermes installer

This directory contains the preview installer surface for **Lumi for Hermes**.

Sprint 4 intentionally ships an inspectable dry-run preview, not a live installer. It reports which reviewed artifacts belong to the preview and confirms that the preview performs no writes.

## Inspect the preview

```bash
python3 installers/lumi-for-hermes/preview.py --dry-run --root /tmp/lumi-hermes-preview
```

The command prints JSON with:

- `mode: dry_run`
- `would_write: []`
- `canonical_writes: 0`
- reviewed adapter artifact paths
- safety notes

## Rollback / uninstall notes

There is nothing to uninstall in Sprint 4 because the preview writes no files. Future installer modes must include a manifest and a rollback command before they are allowed to write under a Hermes profile.

Before release, any non-preview installer must install only reviewed public artifacts and must not expose private Hermes runtime state.
