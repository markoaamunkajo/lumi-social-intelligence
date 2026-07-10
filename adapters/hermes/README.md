# Lumi for Hermes adapter

This directory contains the first host-specific preview: **Lumi for Hermes**.

The adapter binds **Lumi Layered Memory**, **Nuances**, and **Presence** into Hermes Agent through explicit inputs, review surfaces, and safety gates. Sprint 4 keeps this preview dry-run/review-card only: it produces inspectable output and performs no runtime actions.

## Adapter contract

Input schema:

```json
{
  "schema": "lumi.hermes.adapter_input.v1",
  "mode": "dry_run",
  "memory_context": {
    "provider": "hermes-memory",
    "source_id": "synthetic://memory/context/1",
    "text": "Public-safe context summary.",
    "confidence": 0.9
  },
  "nuance_appraisal": {
    "why_now": "short reason this moment may matter",
    "grounded": true,
    "confidence": 0.8
  }
}
```

Output schema:

```json
{
  "schema": "lumi.hermes.review_card.v1",
  "status": "ready_for_review",
  "mode": "dry_run",
  "memory": {},
  "nuance": {},
  "decision": {},
  "safety": {
    "canonical_writes": 0,
    "runtime_actions": [],
    "requires_human_review": true
  }
}
```

Flow:

```text
memory context → compatibility packet → nuance appraisal → Presence decision → review card
```

## Modes

- `dry_run` — produce a review card only.
- `review_gated` — same zero-write behavior, but labeled for future human approval workflows.
- `reaction_presence_shadow` — Sprint 8 reaction-aware Presence card from explicit host-provided reaction input; no Telegram API reads/sends and no memory promotion.
- `outbound_emoji_presence_shadow` — Sprint 9 assistant-side emoji Presence card from explicit host-provided intent; reaction-only, throttled, shadow-only, and no memory promotion.

Both regular modes currently have:

- `canonical_writes: 0`
- `runtime_actions: []`
- `requires_human_review: true`

Reaction presence shadow mode additionally keeps:

- `telegram_reaction_ingestion_verified: false`
- `telegram_outbound_reaction_back_verified: false`
- `telegram_messages_sent: 0`
- `live_memory_writes: 0`
- reaction-back replies tiny, optional, and throttled

Outbound emoji presence shadow mode additionally keeps:

- allowed emoji palette: `❤️ 😄 👍 👀 ✨`
- `delivery_mode: shadow_only`
- `safe_to_claim_live_delivery: false`
- `telegram_reactions_sent: 0`
- `telegram_messages_sent: 0`
- `text_reply: ""`
- `max_text_words: 0`
- `durable_write: false`
- `outbound_reaction_is_not_consent: true`

## Fail-closed behavior

The adapter returns `status: fail_closed` and a `hold` Presence decision when confidence, grounding, or the why-now justification is insufficient.

The adapter rejects private Hermes runtime fields at the contract boundary:

- `chat_id`
- `job_id`
- `scheduler_queue`
- `runtime_state`
- `api_key`
- `token`
- `credential`
- `delivery_channel`
- `connection_string`
- `password`

## Memory-provider boundary

Hermes may use different durable memory setups, including built-in memory tooling, file-backed notes, Obsidian-like vault workflows, or future provider integrations. **Lumi for Hermes** must not assume it owns that memory layer.

Adapter stance:

- Hermes' selected memory provider remains authoritative.
- Lumi reads selected context only through explicit host configuration.
- Lumi preserves provenance and confidence for memory-derived context.
- Lumi emits proposals and receipts before any durable write.
- Lumi does not silently rewrite Hermes memory, Obsidian notes, vault files, or provider internals.
- If memory sources conflict, Lumi should preserve ambiguity and route to Presence for ask/wait/repair behavior.

Default preview mode is read-only plus reviewable proposal/receipt output.

See `docs/memory-provider-compatibility.md` for the shared contract.

Do not add OpenClaw support here. OpenClaw compatibility must be researched before any adapter, installer, or support claim is added.
