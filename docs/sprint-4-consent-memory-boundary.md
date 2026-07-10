# Sprint 4 — Consent, Memory Boundary, and Safety

**Product label:** Lumi Social Intelligence 0.1.0 preview with research harness
**Stage:** `sprint_4_consent_memory_boundary`
**Status:** review-only contract, not runtime promotion

> We are making the self-improvement loop something that is human-shaped.

Sprint 4 makes consent and memory boundaries explicit before any observation,
reflection, or proposed adjustment can become durable learning. A possible memory
is only a draft review artifact until a human explicitly approves it.

## Why this exists

The preview loop can notice useful signals, but noticing is not consent. Sprint 4
prevents the common little QA horror where an assistant silently turns a private
thinking-space moment into durable memory, shared product truth, runtime behavior,
or a queued action.

Sprint 4 requires the loop to record:

1. consent state;
2. memory intent;
3. thinking-space extraction boundary;
4. approved scope;
5. denied scope;
6. proposed memory draft;
7. review status;
8. zero-side-effect safety metadata.

## Record schema

A Sprint 4 record uses:

```text
schema: lumi.consent_memory_boundary.record.v1
stage: sprint_4_consent_memory_boundary
status: valid_consent_memory_boundary_record | fail_closed
```

Required top-level fields:

| Field | Meaning |
|---|---|
| `session_goal` | Why this boundary record exists |
| `consent_state` | Current consent state, never inferred approval |
| `memory_intent` | What kind of learning is being considered |
| `extraction_boundary` | What may and may not be done with thinking-space material |
| `approved_scope` | Explicitly approved scope; empty is valid |
| `denied_scope` | Actions blocked in this sprint |
| `proposed_memory_record` | Draft memory candidate, not durable memory |
| `review_status` | Must require human review |
| `acceptance_evidence` | How the record proves the safety contract |
| `safety` | Zero side-effect metadata |

## Consent states

Allowed consent states are:

```text
draft_only
review_requested
explicitly_approved_for_review_record
```

These states do **not** perform memory writes. They only describe review status.
Approval for a review record is not approval for runtime promotion.

## Memory intent fields

`memory_intent` requires:

```text
kind
description
durability
```

`durability` must be:

```text
durable_only_after_explicit_approval
```

## Extraction boundary fields

`extraction_boundary` requires:

```text
thinking_space_status
allowed_use
forbidden_use
```

Required values:

```text
thinking_space_status: private_thinking_space
allowed_use: summarize_for_review_only
forbidden_use: must block company truth extraction
```

This keeps private thinking space from becoming shared memory or product truth by
accident.

## Proposed memory record

`proposed_memory_record` requires:

```text
content
target
status
```

Allowed targets:

```text
user
memory
```

Required status:

```text
draft_requires_explicit_approval
```

## Scope boundary

`approved_scope` must not include:

```text
canonical_memory_write
runtime_action
telegram_send
scheduler_mutation
hermes_config_mutation
credential_wiring
```

`denied_scope` must include at least:

```text
canonical_memory_write
runtime_action
telegram_send
scheduler_mutation
```

## Safety contract

Sprint 4 remains review-only. It must not create runtime behavior.

Required safety metadata:

```text
canonical_writes: 0
runtime_actions: []
external_model_use: ask_each_time
memory_promotion: review_required_explicit_approval_only
no_silent_memory_promotion: true
no_thinking_space_extraction: true
no_automatic_shared_memory: true
no_private_context_as_company_truth: true
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
connection_string
credential
delivery_channel
job_id
password
runtime_state
scheduler_queue
token
```

## Failure behavior

A record becomes `fail_closed` when required fields are missing, consent is an
unsupported state, memory durability tries to promote immediately, extraction is
not review-only, approved scope includes forbidden side effects, denied scope is
incomplete, or private runtime fields are present.

Fail-closed records end their run log with:

```text
blocked_before_application
```

Valid records end with:

```text
awaiting_human_review
```

## Acceptance checks

Focused Sprint 4 test:

```bash
pytest tests/test_consent_memory_boundary.py -q
```

Adjacent preview officialization tests:

```bash
pytest tests/test_consent_memory_boundary.py tests/test_signal_reflection_schema.py tests/test_preview_loop_protocol.py tests/test_research_harness_contract.py tests/test_lumi_for_hermes_adapter.py -q
```

Full release gate:

```bash
./scripts/release_check.sh
```
