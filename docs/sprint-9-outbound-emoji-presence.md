# Sprint 9 — Outbound Emoji Presence

Sprint 9 adds a **shadow-only contract** for assistant-side emoji reactions.

```text
Presence Intent → Emoji Reaction Choice → Delivery Boundary
```

The goal is deliberately small: Lumi may recommend a tiny emoji reaction when a reaction is less intrusive than a text reply. The public contract does **not** claim that a platform reaction was delivered live.

## Principle

> An outbound emoji reaction is a tiny presence gesture, not a message and not a memory.

This keeps the Sprint 8 rule intact: reactions are presence signals, not durable memory.

## Allowed reaction palette

The Sprint 9 public palette is intentionally tiny:

```text
❤️ 😄 👍 👀 ✨
```

Anything outside that palette fails closed to silence.

## Default behavior

The default is **stay silent**.

Lumi can choose `add_emoji_reaction` only when all of these are true:

- the target message is user-authored;
- the candidate emoji is in the approved tiny palette;
- there is a short `why_now` justification;
- the turn gap is outside the throttle window;
- the runtime keeps delivery shadow-only unless platform delivery has been separately verified.

## Throttle

Sprint 9 uses a minimum gap of 3 turns between outbound emoji reactions in the public contract. If the previous outbound reaction is too recent, the record returns:

```json
{
  "presence_intent": { "gesture": "stay_silent" },
  "emoji_choice": { "emoji": "" },
  "throttle": { "throttled": true }
}
```

## No text replies from this layer

Outbound emoji presence is reaction-only. It never creates paragraph text or even a tiny text reply.

```json
{
  "emoji_choice": {
    "emoji": "❤️",
    "text_reply": "",
    "max_text_words": 0
  }
}
```

If text is useful, that belongs to the normal Presence reply layer, not the emoji reaction layer.

## Delivery boundary

The public repo emits `delivery_mode: shadow_only`.

Even when the host supplies `platform_delivery_verified: true`, the contract still reports:

```json
{
  "delivery_boundary": {
    "delivery_mode": "shadow_only",
    "safe_to_claim_live_delivery": false
  }
}
```

A host adapter must separately prove native platform support, target-message ID safety, authorization, throttling, and user approval before sending an actual platform reaction.

## Memory boundary

Outbound emoji reactions do not write or promote memory.

```json
{
  "memory_boundary": {
    "durable_write": false,
    "promotion_status": "not_promoted",
    "explicit_consent_required_for_promotion": true,
    "outbound_reaction_is_not_consent": true
  }
}
```

A reaction gesture may be useful session texture. It is not consent to learn something durable.

## Forbidden runtime fields

The contract rejects private/runtime fields including:

```text
api_key, token, credential, chat_id, delivery_channel, scheduler_queue,
job_id, runtime_state, connection_string, password
```

These fields must stay outside public records and test fixtures.

## Hermes adapter status

`adapters/hermes/lumi_for_hermes.py` exposes `build_outbound_emoji_presence_card(...)` for host-provided shadow input.

The adapter does not:

- call Telegram APIs;
- send messages;
- send reactions;
- mutate Hermes config;
- mutate schedulers;
- write memory;
- claim live delivery.

It only builds a public-safe Sprint 9 card for review.

## Acceptance criteria

Sprint 9 is accepted when tests prove:

- approved emoji choices are reaction-only;
- unapproved emojis fail closed to silence;
- throttle prevents repeated reactions;
- assistant/unknown target messages are rejected;
- private runtime fields are rejected;
- no text reply is generated;
- no canonical writes occur;
- no Telegram send/reaction API action is claimed;
- durable memory promotion remains impossible without explicit approval.
