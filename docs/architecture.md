# Architecture

Lumi Social Intelligence is a host-neutral layer composed of three cooperating parts:

```text
Lumi Layered Memory -> Nuances -> Presence
```

## Layered Memory

Remembers useful continuity with review, citations, and inspectable state. It should not silently rewrite identity, preferences, or durable user facts.

## Nuances

Reads the moment: corrections, tone, consent signals, uncertainty, risk, and context shifts. Nuances proposes interpretations; it does not mutate durable behavior on its own.

## Presence

Chooses timing and action: speak, wait, ask, act, repair, or stay quiet. Presence is the fail-closed gate when continuity, memory, or context is uncertain.

## Host adapters

Host adapters translate the Lumi contract into a specific agent runtime.

Initial adapter:

- Hermes Agent

Deferred adapter:

- OpenClaw, pending compatibility research.
