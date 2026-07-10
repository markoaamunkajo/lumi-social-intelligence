# Sprint 3 — Signal / Reflection Schema

**Product label:** Lumi Social Intelligence 0.1.0 preview with research harness
**Stage:** `sprint_3_signal_reflection_schema`
**Status:** review-only contract, not runtime promotion

> We are making the self-improvement loop something that is human-shaped.

Sprint 3 makes the preview loop's judgment inspectable by separating what was
observed from what was inferred. A signal is evidence. A reflection is an
interpretation that may be wrong, incomplete, useful, risky, or contradicted.

## Why this exists

Without a signal/reflection boundary, an assistant can accidentally treat a
single moment as durable truth. Sprint 3 prevents that drift by requiring the
loop to record:

1. the observed signal;
2. the reflection/interpretation;
3. contradictions or uncertainty;
4. confidence;
5. consent state;
6. proposed adjustment;
7. review-only/no-write safety metadata.

This keeps Lumi useful without letting every tiny vibe become canon. Tiny QA
horror avoided. Clipboard remains tasteful.

## Record schema

A Sprint 3 record uses:

```text
schema: lumi.signal_reflection.record.v1
stage: sprint_3_signal_reflection_schema
status: valid_signal_reflection_record | fail_closed
```

Required top-level fields:

| Field | Meaning |
|---|---|
| `session_goal` | Why this signal/reflection exists |
| `observed_signal` | Evidence-bearing observation, not interpretation |
| `reflection` | Interpretation, confidence, contradiction, and risk |
| `proposed_adjustment` | Small reversible adjustment under review |
| `consent` | Consent state and apply boundary |
| `acceptance_evidence` | How the record proves the schema/safety contract |
| `safety` | Zero side-effect metadata |

## Observed signal fields

| Field | Meaning |
|---|---|
| `source` | Where the signal came from, e.g. `current_chat` |
| `type` | Signal category, e.g. consent/correction/preference/tone |
| `description` | Plain-language observation |
| `evidence` | Quote or public-safe evidence snippet |
| `strength` | `weak`, `medium`, or `strong` |
| `uncertainty` | `low`, `medium`, or `high` |

## Reflection fields

| Field | Meaning |
|---|---|
| `interpretation` | What Lumi thinks the signal may mean |
| `confidence` | `low`, `medium`, or `high` |
| `contradictions` | List of conflicting evidence or uncertainty notes |
| `risk` | `low`, `medium`, or `high` |
| `boundary` | Must be `review_only_not_runtime` |

## Consent and adjustment fields

`proposed_adjustment` requires:

```text
name
description
scope
```

`consent` requires:

```text
state
checkpoint
required_before
```

The consent checkpoint must be:

```text
ask_before_apply
```

## Safety contract

Sprint 3 remains review-only. It must not create runtime behavior.

Required safety metadata:

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

The builder rejects private/runtime fields such as:

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

If a payload attempts memory promotion, the record fails closed and reports:

```text
silent memory promotion is not allowed
```

## Failure behavior

A record becomes `fail_closed` when required fields are missing, unsupported enum
values are used, contradictions are not list-shaped, or silent memory promotion is
attempted.

Fail-closed records end their run log with:

```text
blocked_before_application
```

Valid records end with:

```text
awaiting_human_review
```

## Acceptance checks

Focused Sprint 3 test:

```bash
pytest tests/test_signal_reflection_schema.py -q
```

Adjacent preview officialization tests:

```bash
pytest tests/test_signal_reflection_schema.py tests/test_preview_loop_protocol.py tests/test_research_harness_contract.py tests/test_lumi_for_hermes_adapter.py -q
```

Full release gate:

```bash
./scripts/release_check.sh
```
