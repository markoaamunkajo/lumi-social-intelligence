# Host Compatibility

Lumi Social Intelligence is host-neutral. Runtime-specific adapters provide installation, context injection, review surfaces, and safety gates.

## Compatibility matrix

| Host | Status | Notes |
|---|---|---|
| Hermes Agent | Planned first | Known local runtime with skills, tools, files, messaging surfaces, and reviewable configuration. |
| OpenClaw | Research needed | Do not add folders, installers, or support claims until its architecture and extension points are verified. |

## Shared Lumi contract

A compatible host should provide or allow:

- context injection with clear precedence;
- file-backed or API-backed review cards;
- explicit dry-run/review/live mode boundaries;
- safe tool/action gating;
- rollback or at least reversible write records;
- public/private boundary separation;
- secret and local-state hygiene before release.

## Adapter rule

Adapters are thin runtime bindings. The core Lumi concepts remain the same across hosts:

- memory input/output;
- nuance appraisal cards;
- presence decision cards;
- review gates;
- receipts;
- fail-closed behavior.
