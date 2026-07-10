# Sprint 6 — Official 0.1.0 Packaging / Release Notes

**Product label:** Lumi Social Intelligence 0.1.0 preview with research harness
**Stage:** `sprint_6_official_packaging_release_notes`
**Status:** release-note packaging candidate, human-review required before publication

> We are making the self-improvement loop something that is human-shaped.

Sprint 6 reconciles two truths that must stay separate:

```text
Technical v0.1.0 public release exists.
Official/product-ready 0.1.0 packaging is a reviewed product-readiness note.
```

This sprint creates a schema for packaging and release notes. It does **not**
publish a release, move tags, edit GitHub releases, wire runtime services, or
claim live Telegram integration.

## Why this exists

The original `v0.1.0` release is a technical public artifact. Since then, the
product-readiness story gained a proper officialization chain:

1. Sprint 1 — Research Harness Contract;
2. Sprint 2 — Preview Loop Protocol;
3. Sprint 3 — Signal / Reflection Schema;
4. Sprint 4 — Consent, Memory Boundary, and Safety;
5. Sprint 5 — Evaluation and Acceptance Criteria.

Sprint 6 packages that evidence into release-note structure without pretending
that a live service exists.

## Record schema

A Sprint 6 record uses:

```text
schema: lumi.official_packaging.record.v1
stage: sprint_6_official_packaging_release_notes
status: valid_official_packaging_record | fail_closed
```

Required fields:

| Field | Meaning |
|---|---|
| `session_goal` | Why this packaging record exists |
| `technical_release` | Existing public technical release/tag status |
| `product_release` | Product-readiness packaging candidate status |
| `officialization_evidence` | Required Sprint 1–5 + release-check evidence |
| `release_note_sections` | Required sections for official 0.1.0 notes |
| `packaging_decision` | Review-gated allowed/blocked action |
| `review_status` | Must require human review |
| `acceptance_evidence` | Why the packaging is bounded and evidence-based |

## Required officialization evidence

A valid record must include:

```text
sprint_1_research_harness_contract_passed
sprint_2_preview_loop_protocol_passed
sprint_3_signal_reflection_schema_passed
sprint_4_consent_memory_boundary_passed
sprint_5_evaluation_acceptance_criteria_passed
release_check_passed
```

## Required release-note sections

A valid release-note candidate must include these sections:

```text
technical_release_exists
product_readiness_delta
officialization_sprints
safety_boundaries
verification_evidence
not_included
human_review_next_step
```

The `not_included` section is required on purpose. It prevents packaging from
accidentally implying a hidden runtime, live Telegram sender, scheduler mutation,
credential wiring, or automatic durable learning.

## Decision contract

Valid packaging decision:

```text
status: ready_for_human_release_note_review
allowed_action: draft_official_0_1_0_release_notes
blocked_action: publish_without_human_review
```

This keeps Sprint 6 as release-note preparation, not publication.

## Safety contract

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
no_publish_without_human_review: true
no_release_claim_without_evidence: true
requires_human_review: true
```

Forbidden private/runtime fields remain rejected:

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

A record becomes `fail_closed` if it:

- blurs the existing technical release with the product-readiness candidate;
- omits Sprint 1–5 evidence;
- omits release-check evidence;
- omits required release-note sections;
- attempts publication without review;
- weakens zero-side-effect safety metadata;
- includes private/runtime fields.

Fail-closed records end their run log with:

```text
blocked_before_publication
```

Valid records end with:

```text
awaiting_human_review_for_release_notes
```

## Acceptance checks

Focused Sprint 6 test:

```bash
pytest tests/test_official_packaging_release_notes.py -q
```

Adjacent officialization tests:

```bash
pytest tests/test_official_packaging_release_notes.py tests/test_evaluation_acceptance_criteria.py tests/test_consent_memory_boundary.py tests/test_signal_reflection_schema.py tests/test_preview_loop_protocol.py tests/test_research_harness_contract.py tests/test_lumi_for_hermes_adapter.py -q
```

Full release gate:

```bash
./scripts/release_check.sh
```
