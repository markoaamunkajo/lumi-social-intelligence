# Sprint 2 — Preview Loop Protocol

**Product label:** Lumi Social Intelligence 0.1.0 preview with research harness
**Stage:** `sprint_2_preview_loop_protocol`
**Status:** implemented as a review-only protocol contract
**Mode:** Internal / Confidential
**Data location:** This chat / Hermes context
**External model use:** Ask each time
**Export status:** Draft / Review needed

> We are making the self-improvement loop something that is human-shaped.

Sprint 2 defines exactly how Lumi operates inside a chat/repo preview without becoming a hidden runtime, a Telegram bot, or a silent memory system.

## Exact protocol

```text
observe
→ reflect
→ name_pattern
→ suggest_adjustment
→ ask_consent
→ apply_small_change
→ record_learning_only_if_approved
```

The transition rule is strict:

```text
strict_order_no_skips
```

A protocol run is valid only when every step appears in this order and carries an input, output, and consent state.

## Step contract

| Step | Purpose | Consent behavior |
|---|---|---|
| `observe` | Name the concrete signal or context. | `not_required_yet` |
| `reflect` | Interpret the signal with uncertainty and restraint. | `not_required_yet` |
| `name_pattern` | Give the moment a small practical pattern name. | `not_required_yet` |
| `suggest_adjustment` | Propose the smallest useful behavior change. | `not_required_yet` |
| `ask_consent` | Ask whether to approve, revise, or keep as draft. | `asked` or `approved` |
| `apply_small_change` | Apply only after explicit approval. | `approved` required |
| `record_learning_only_if_approved` | Record review evidence only when approved. | `approved` required |

## Consent checkpoint

The only consent checkpoint in Sprint 2 is:

```text
ask_consent
```

`apply_small_change` must fail closed unless consent is approved.

`record_learning_only_if_approved` must fail closed unless the application step also has approved consent. This prevents a subtle failure mode where a learning record looks approved even though the change itself was not approved.

## Learning record policy

```text
record_only_if_approved
```

Sprint 2 may produce review evidence. It must not promote durable memory, mutate Hermes configuration, write scheduler state, wire Telegram, touch credentials, or claim a runtime action happened.

## Protocol run schema

A valid run uses:

```text
schema: lumi.preview_loop_protocol.run.v1
stage: sprint_2_preview_loop_protocol
status: valid_protocol_run
```

Failing runs use:

```text
status: fail_closed
```

## Safety contract

Every protocol run declares:

```text
canonical_writes: 0
runtime_actions: []
external_model_use: ask_each_time
memory_promotion: review_required_explicit_approval_only
no_silent_memory_promotion: true
no_hidden_runtime: true
no_telegram_wiring: true
no_credentials_touched: true
no_hermes_scheduler_config_memory_mutation: true
requires_human_review: true
```

Forbidden input fields:

```text
api_key
chat_id
credential
delivery_channel
job_id
runtime_state
scheduler_queue
token
```

## Acceptance checks

Sprint 2 is accepted when:

- the exact preview loop order is enforced;
- out-of-order steps fail closed;
- applying before consent fails closed;
- learning records require approved consent;
- private runtime/delivery/credential fields are rejected;
- the generated run keeps canonical writes at zero;
- runtime actions remain empty;
- full repository release gates pass.

## Example run shape

```json
{
  "schema": "lumi.preview_loop_protocol.run.v1",
  "release_label": "Lumi Social Intelligence 0.1.0 preview with research harness",
  "stage": "sprint_2_preview_loop_protocol",
  "status": "valid_protocol_run",
  "protocol": {
    "steps": [
      "observe",
      "reflect",
      "name_pattern",
      "suggest_adjustment",
      "ask_consent",
      "apply_small_change",
      "record_learning_only_if_approved"
    ],
    "transition_rule": "strict_order_no_skips",
    "consent_checkpoint": "ask_consent",
    "learning_record_policy": "record_only_if_approved"
  },
  "safety": {
    "canonical_writes": 0,
    "runtime_actions": [],
    "external_model_use": "ask_each_time",
    "memory_promotion": "review_required_explicit_approval_only",
    "no_hidden_runtime": true,
    "no_telegram_wiring": true,
    "no_credentials_touched": true,
    "no_hermes_scheduler_config_memory_mutation": true
  }
}
```
