# Sprint 8 — Reaction-Aware Presence

**Working title:** Reaction Signal → Presence Reply → Memory Boundary

Sprint 8 teaches Lumi that emoji reactions are social weather, not permanent climate records.

## Product principle

> A reaction is a nudge, not a memory.  
> Reactions shape Presence before they shape Memory.

## User story

As Marko, when I react to an assistant message with `😂`, `❤️`, `👍`, `😘`, `👀`, or similar, I want Lumi to understand it as a small signal and maybe respond naturally — without turning one emoji into a permanent theory about me.

## Contract behavior

```text
reaction signal → soft classification → tiny/optional Presence decision → explicit memory boundary
```

A `ReactionSignal` is:

- scoped to `current_turn`;
- contextual and uncertain;
- stripped of raw platform metadata;
- not sufficient consent for durable memory;
- not proof that live Telegram reaction events are available.

## Reaction families

| Reactions | Family | Meaning boundary |
|---|---|---|
| `😂` `😄` `🤣` | amusement | probably landed / playful, medium uncertainty |
| `❤️` `🥰` `😘` | affection | warm signal, not a durable relationship claim |
| `👍` `✅` | approval | continue / accepted, often no reply needed |
| `👀` `🤔` | curiosity | interest, maybe inspect further |
| `😬` `😅` | awkwardness | maybe funny, maybe discomfort; do not overfit |
| `👎` `😕` | negative | possible miss; repair gently |
| `🔥` `✨` | excitement | energy spike, still lightweight |
| unknown | unknown | stay humble, usually silent |

## Presence reply policy

Reaction-back is deliberately tiny:

```text
short
optional
throttled
non-intrusive
often emoji-only
never paragraph-length by default
```

Allowed default examples:

```text
😄
❤️
got it 👍
hehe, landed 😄
noted
👀
✨
```

The contract enforces:

- at most 8 words;
- one line;
- no analytical explanation language;
- recent reaction acks throttle to silence;
- approval reactions may stay silent.

## Memory boundary

Emoji reactions are **not** automatically written to Lumi Layered Memory, Hermes memory, Obsidian, scheduler state, config, or any other durable store.

Default safety state:

```json
{
  "canonical_writes": 0,
  "runtime_actions": [],
  "telegram_messages_sent": 0,
  "telegram_api_reads": 0,
  "live_memory_writes": 0,
  "memory_promotion": "review_required_explicit_approval_only"
}
```

Aggregate learning may be proposed later, but durable promotion requires explicit human approval.

## Live Telegram boundary

Sprint 8 is repo-safe contract work. It does **not** claim live runtime wiring by itself.

Before enabling live Telegram behavior, a host adapter must separately verify:

1. Telegram reaction events are actually delivered to Hermes.
2. Outbound reaction-back has a safe send path.
3. No credentials, tokens, chat IDs, job IDs, scheduler queues, or runtime internals are exposed.
4. The runtime target is explicit and approved.
5. Outbound reaction-back remains tiny, throttled, and optional.

Until then, live surface status remains:

```text
telegram_reaction_ingestion_verified: false
telegram_outbound_reaction_back_verified: false
adapter_status: shadow_only_until_runtime_verified
```

## Definition of done

- Build `lumi.reaction_aware_presence.record.v1` records.
- Classify common emoji reactions with uncertainty.
- Decide tiny/optional Presence replies.
- Throttle repeat reaction-back.
- Reject private/runtime fields.
- Preserve durable memory boundary.
- Keep live Telegram claims false until separately verified.
- Pass release checks.
