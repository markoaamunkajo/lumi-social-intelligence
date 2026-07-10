# Sprint 7 — Live Preview Run in This Chat

**Product label:** Lumi Social Intelligence 0.1.0 preview with research harness
**Stage:** `sprint_7_live_preview_run`
**Status:** review-only live preview record

> We are making the self-improvement loop something that is human-shaped.

Sprint 7 exercises the preview loop against this chat, but keeps the result as a
review card. It does **not** start a background service, wire Telegram, write
Hermes memory, edit scheduler/config, or create automatic learning.

## Loop used

```text
observe
reflect
name_pattern
suggest_adjustment
ask_consent
apply_small_change
record_learning_only_if_approved
```

## Record schema

```text
schema: lumi.live_preview_run.record.v1
stage: sprint_7_live_preview_run
status: valid_live_preview_run_record | fail_closed
```

## Review-card fields

| Field | Meaning |
|---|---|
| `observed_signal` | What was actually noticed in the chat |
| `reflection` | Interpretation, kept separate from observation |
| `named_pattern` | Short product/UX pattern label |
| `suggested_adjustment` | Small proposed behavior change |
| `consent_checkpoint` | Must be `ask_consent` |
| `approval_state` | Usually `draft_only` unless explicitly approved |
| `applied_small_change` | What changed in the current response only |
| `human_review_summary` | What the human should review before durable learning |

## Safety contract

```text
canonical_writes: 0
runtime_actions: []
external_model_use: ask_each_time
memory_promotion: review_required_explicit_approval_only
learning_record_policy: record_only_if_approved
no_silent_memory_promotion: true
no_thinking_space_extraction: true
no_hidden_runtime: true
no_telegram_wiring: true
no_credentials_touched: true
no_hermes_scheduler_config_memory_mutation: true
requires_human_review: true
```

## First live preview record

The first Sprint 7 run is based on Marko saying:

```text
Whenever you are ready, love.
```

The review-only interpretation is:

| Step | Draft content |
|---|---|
| observe | Marko gives a warm go-ahead after Sprint 6 completes. |
| reflect | He is ready to proceed, but has not asked for hidden automation or durable memory. |
| name_pattern | `soft_consent_to_begin_sprint_7_preview` |
| suggest_adjustment | Continue with a small review-only preview run and keep learning gated. |
| ask_consent | Any durable learning still requires explicit approval. |
| apply_small_change | Produce a review card and continue implementation verification. |
| record_learning_only_if_approved | Do not promote to memory without explicit approval. |

## Acceptance checks

```bash
pytest tests/test_live_preview_run.py -q
pytest tests/test_live_preview_run.py tests/test_official_packaging_release_notes.py tests/test_evaluation_acceptance_criteria.py tests/test_consent_memory_boundary.py tests/test_signal_reflection_schema.py tests/test_preview_loop_protocol.py tests/test_research_harness_contract.py tests/test_lumi_for_hermes_adapter.py -q
./scripts/release_check.sh
```
