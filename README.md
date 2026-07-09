# Lumi Social Intelligence

Memory, nuance, and presence for AI agents.

Lumi Social Intelligence is a portable social-intelligence layer for agent runtimes. It helps assistants remember with receipts, read the moment with reviewable nuance, and choose presence safely: speak, wait, ask, act, repair, or stay quiet.

> Status: private playground. This repository is not public-release-ready yet.

## Architecture

```text
Lumi Layered Memory -> Nuances -> Presence

Memory gives context.
Nuances reads the moment.
Presence decides whether to speak, wait, ask, act, or repair.
```

## Repository role

This repository is the curated release doorway for tested Lumi Social Intelligence updates.

Development happens in private module repositories:

- `lumi-layered-memory`
- `nuances`
- `presence`
- `autoresearch`

Release candidates are promoted here only after review, tests, public-boundary checks, and secret/privacy scans pass.

## Initial host target

- Hermes adapter: planned first.
- OpenClaw adapter: intentionally not added yet; compatibility is unknown and must be researched before shaping folders or installers.

## Project layout

```text
core/
  layered-memory/   # curated memory layer release surface
  nuances/          # curated nuance/appraisal release surface
  presence/         # curated presence/initiative release surface
adapters/
  hermes/           # Hermes-specific integration boundary
installers/
  lumi-for-hermes/  # first installer/distribution target
docs/
examples/
scripts/
tests/
```

## Public-release rule

No raw runs, private memories, chat logs, credentials, local runtime state, scheduler/job IDs, private coordinates, or unreviewed dev artifacts belong in this repository.
