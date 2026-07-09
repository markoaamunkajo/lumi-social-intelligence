# Release Boundary

This repository receives tested, curated updates from private development repositories.

## Private development repositories

- Lumi Layered Memory
- Nuances
- Presence
- Autoresearch

## Promotion rule

Push development work to the private development repositories. Promote into Lumi Social Intelligence only when the update is tested, documented, and safe for a release candidate.

## Do not include

- raw AutoResearch runs;
- private memories or diaries;
- chat logs;
- credentials, tokens, API keys, passwords;
- local runtime state;
- scheduler internals, cron/job IDs, queues, wrappers;
- private coordinates or personal identifiers;
- unreviewed generated artifacts;
- host-specific claims that have not been verified.

## Release gate

Every release candidate should pass:

```bash
./scripts/release_check.sh
```

Before publication, also run a clean-checkout smoke test from the release archive.
