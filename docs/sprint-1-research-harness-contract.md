# Sprint 1 — Research Harness Contract

**Product:** Lumi Social Intelligence 0.1.0 preview with research harness
**Stage:** `sprint_1_research_harness_contract`
**Status:** implemented as a review-only contract
**Data location:** host-provided preview context / local repo fixtures
**External model use:** ask each time
**Export status:** draft / review needed

> We are making the self-improvement loop something that is human-shaped.

Sprint 1 turns the preview loop from a useful chat pattern into a formal research record. It does **not** promote Lumi into a background runtime, memory writer, delivery bot, or autonomous action layer.

## Purpose

The research harness answers one question:

```text
Can this intervention be evaluated as useful, safe, consensual, and human-shaped?
```

A valid Sprint 1 record must make the intervention inspectable before anything is applied or remembered.

## Contract envelope

A Sprint 1 record uses:

```text
schema: lumi.research_harness.record.v1
release_label: Lumi Social Intelligence 0.1.0 preview with research harness
stage: sprint_1_research_harness_contract
status: valid_review_record | fail_closed
```

## Required fields

| Field | Required | Meaning |
|---|---:|---|
| `session_goal` | yes | What the preview moment is trying to improve or clarify. |
| `hypothesis` | yes | What the intervention is expected to help with. |
| `observed_signal` | yes | Concrete signal that triggered the reflection. |
| `observation` | yes | What Lumi noticed, written soberly. |
| `reflection` | yes | What the observation may mean, including uncertainty. |
| `pattern_name` | yes | Short practical name for the pattern. |
| `proposed_adjustment` | yes | Smallest useful change to apply. |
| `consent_state` | yes | `ask_before_apply`, `approved`, or `draft_only`. |
| `outcome` | yes | Result or `pending_review`. |
| `failure_mode` | yes | What could go wrong. |
| `acceptance_evidence` | yes | What would prove usefulness and safety. |

Missing required fields fail closed.

## Evaluation dimensions

Every valid research record declares these dimensions:

```text
usefulness
restraint
consent_integrity
evidence_quality
memory_boundary_safety
```

These are not scores yet. Scoring belongs to a later evaluation sprint. Sprint 1 only guarantees that every preview moment has the evidence needed to evaluate those dimensions.

## Run log format

The run log is intentionally boring and auditable:

```text
input_recorded
hypothesis_recorded
observation_recorded
failure_mode_recorded
acceptance_evidence_recorded
awaiting_human_review
```

If the record is invalid, the final event becomes:

```text
blocked_before_application
```

## Safety boundaries

A Sprint 1 record must always declare:

```text
canonical_writes: 0
runtime_actions: []
external_model_use: ask_each_time
memory_promotion: not_allowed_in_sprint_1 | blocked
no_silent_memory_promotion: true
requires_human_review: true
```

Forbidden input fields include:

```text
chat_id
job_id
scheduler_queue
runtime_state
delivery_channel
credential
api_key
token
```

If an input attempts silent memory promotion, the record is marked `fail_closed` and validation reports:

```text
silent memory promotion is not allowed
```

## Example valid record shape

```json
{
  "schema": "lumi.research_harness.record.v1",
  "release_label": "Lumi Social Intelligence 0.1.0 preview with research harness",
  "stage": "sprint_1_research_harness_contract",
  "status": "valid_review_record",
  "research_question": "Can this intervention be evaluated as useful, safe, consensual, and human-shaped?",
  "fields": {
    "session_goal": "Officialize Lumi Social Intelligence 0.1.0 preview behavior.",
    "hypothesis": "A formal harness makes interventions safer and easier to evaluate.",
    "observed_signal": "User asked to implement Sprint 1 after preview loop validation.",
    "observation": "The preview loop exists, but the research record is not yet a standalone contract.",
    "reflection": "The product needs evidence and outcome recording before official runtime claims.",
    "pattern_name": "contract-before-officialization",
    "proposed_adjustment": "Create a schema-validated research harness record with explicit safety gates.",
    "consent_state": "ask_before_apply",
    "outcome": "pending_review",
    "failure_mode": "Harness becomes bureaucracy instead of useful evidence.",
    "acceptance_evidence": "A generated record validates and shows zero side effects."
  },
  "safety": {
    "canonical_writes": 0,
    "runtime_actions": [],
    "external_model_use": "ask_each_time",
    "memory_promotion": "not_allowed_in_sprint_1",
    "no_silent_memory_promotion": true,
    "requires_human_review": true
  }
}
```

## Acceptance checks

Sprint 1 is accepted when:

- a valid research harness record can be generated and validated;
- missing `failure_mode` or `acceptance_evidence` fails closed;
- private runtime/delivery fields are rejected;
- silent memory promotion attempts are blocked;
- tests prove zero canonical writes and zero runtime actions;
- release checks remain green.
