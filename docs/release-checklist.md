# Release Checklist

Before Lumi Social Intelligence is made public or tagged for release, verify each gate.

## Product/documentation gates

- [ ] README presents **Lumi Social Intelligence** as the release doorway.
- [ ] Public-facing docs use **Lumi Layered Memory**, **Nuances**, and **Presence** as product names.
- [ ] Autoresearch is described only as private harness/evidence infrastructure.
- [ ] No OpenClaw adapter, installer, or support claim exists before compatibility research.
- [ ] Module promotion workflow documents read-only audit, review-only plan, and explicit reviewed apply.
- [ ] GitHub About description and topics match the public product story.

## Safety/privacy gates

- [ ] No raw runs, private memories, diaries, or chat logs are tracked.
- [ ] No credentials, tokens, API keys, passwords, connection strings, or chat IDs are tracked.
- [ ] No local runtime state, scheduler internals, cron/job IDs, queues, or wrappers are tracked.
- [ ] No private coordinates or personal identifiers are tracked.

## Verification gates

Run:

```bash
./scripts/release_check.sh
```

The release gate currently checks:

- Python syntax for scripts and tests;
- repository structure tests;
- public/secret scan;
- module release gate validation;
- deterministic release artifact build;
- clean-checkout release artifact smoke test;
- release archive scan for private/local material;
- whitespace/diff hygiene.

## Release artifact gates

Release candidate artifacts are produced with:

```bash
python3 scripts/build_release_artifacts.py --output-dir dist/release
```

The builder creates:

- `lumi-social-intelligence-0.1.0-rc.1.zip`
- `release-manifest.json`
- `SHA256SUMS`

The release archive is built from tracked public doorway files only. It excludes
local/runtime/private material such as `.git/`, `.hermes/`, `runs/`, `logs/`,
cache directories, and generated build outputs. The manifest records package
artifact status for **Lumi Layered Memory**, **Nuances**, and **Presence**, plus
the **Lumi for Hermes** dry-run preview artifact paths.

## Licensing gates

- [ ] `LICENSE` matches the related Lumi repositories.
- [ ] `LICENSE-DOCS.md` matches the related Lumi repositories.
- [ ] `NOTICE.md` matches the related Lumi repositories.
