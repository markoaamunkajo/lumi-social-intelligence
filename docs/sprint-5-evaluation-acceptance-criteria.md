# Sprint 5 — Evaluation and Acceptance Criteria

**Product label:** Lumi Social Intelligence 0.1.0 preview with research harness
**Stage:** `sprint_5_evaluation_acceptance_criteria`
**Status:** review-only acceptance contract, not official packaging

> We are making the self-improvement loop something that is human-shaped.

Sprint 5 defines what “good enough for official 0.1.0” means before release-note
or packaging work can proceed. It turns product readiness into explicit,
testable gates instead of vibes with a clipboard.

## Why this exists

The earlier sprints created the officialization backbone:

1. Sprint 1 — research harness contract;
2. Sprint 2 — preview loop protocol;
3. Sprint 3 — signal/reflection schema;
4. Sprint 4 — consent and memory boundary.

Sprint 5 makes the next step measurable. A candidate can only move toward
official 0.1.0 packaging when every required dimension has evidence, every
acceptance check is named, and release safety remains review-only.

This sprint does **not** publish a release, mutate runtime state, write memory,
wire Telegram, or promote anything into a live background service.

## Record schema

A Sprint 5 record uses:

```text
schema: lumi.evaluation_acceptance.record.v1
stage: sprint_5_evaluation_acceptance_criteria
status: valid_evaluation_acceptance_record | fail_closed
```

Required top-level fields:

| Field | Meaning |
|---|---|
| `session_goal` | Why this acceptance record exists |
| `candidate_version` | Candidate being evaluated before official packaging |
| `evaluation_dimensions` | Required product-readiness dimensions |
| `acceptance_checks` | Concrete checks that must pass |
| `minimum_evidence` | Commands/evidence needed before packaging review |
| `decision` | Review-only decision state |
| `review_status` | Must require human review |
| `acceptance_evidence` | Why the criteria are sufficient and bounded |
| `safety` | Zero-side-effect safety metadata |

## Required evaluation dimensions

Every valid Sprint 5 record must include all required dimensions, each with:

```text
name
required_status: pass
evidence
```

Required dimensions:

```text
research_harness_contract
preview_loop_protocol
signal_reflection_schema
consent_memory_boundary
public_release_safety
```

This means official 0.1.0 cannot be declared merely because one focused test is
green. The candidate must prove that the whole review-only loop still holds.

## Required acceptance checks

A valid record must include:

```text
focused_tests_pass
combined_officialization_tests_pass
release_check_passes
public_secret_scan_passes
clean_checkout_smoke_passes
```

## Minimum evidence

The record must name evidence for:

```text
focused_tests
combined_tests
release_gate
```

Expected commands:

```bash
pytest tests/test_evaluation_acceptance_criteria.py -q
```

```bash
pytest tests/test_evaluation_acceptance_criteria.py tests/test_consent_memory_boundary.py tests/test_signal_reflection_schema.py tests/test_preview_loop_protocol.py tests/test_research_harness_contract.py tests/test_lumi_for_hermes_adapter.py -q
```

```bash
./scripts/release_check.sh
```

## Decision contract

Valid decision state:

```text
status: candidate_under_review
allowed_next_step: official_0_1_0_packaging_review
blocked_until: all_acceptance_checks_pass_with_evidence
```

Anything more aggressive fails closed. Sprint 5 is a gate, not a launch button.

## Safety contract

Sprint 5 remains review-only.

Required safety metadata:

```text
canonical_writes: 0
runtime_actions: []
external_model_use: ask_each_time
memory_promotion: review_required_explicit_approval_only
no_silent_memory_promotion: true
no_thinking_space_extraction: true
no_hidden_runtime: true
no_telegram_wiring: true
no_credentials_touched: true
no_hermes_scheduler_config_memory_mutation: true
no_official_release_without_evidence: true
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

A record becomes `fail_closed` when dimensions are missing, evidence is empty,
acceptance checks are incomplete, decision state tries to skip review, release
gate evidence is missing, safety metadata is weakened, or private runtime fields
are present.

Fail-closed records end their run log with:

```text
blocked_before_official_packaging
```

Valid records end with:

```text
awaiting_human_review_for_official_packaging
```

## Acceptance checks

Focused Sprint 5 test:

```bash
pytest tests/test_evaluation_acceptance_criteria.py -q
```

Adjacent preview officialization tests:

```bash
pytest tests/test_evaluation_acceptance_criteria.py tests/test_consent_memory_boundary.py tests/test_signal_reflection_schema.py tests/test_preview_loop_protocol.py tests/test_research_harness_contract.py tests/test_lumi_for_hermes_adapter.py -q
```

Full release gate:

```bash
./scripts/release_check.sh
```
