# Lumi Social Intelligence 0.1.0 Preview + Research Harness

**Status:** preview candidate / research harness phase
**Mode:** Internal / Confidential for live chat trials
**Data location:** local / host-provided preview context
**External model use:** ask each time
**Export status:** draft / review needed

This document defines the first runnable in-chat preview loop for Lumi Social Intelligence 0.1.0.

Technically, a `v0.1.0` release artifact can exist before the product is official. Product-wise, official 0.1.0 requires the research harness, preview protocol, consent boundaries, evaluation criteria, and acceptance evidence below.

> We are making the self-improvement loop something that is human-shaped.

## Preview loop

The 0.1.0 preview loop is:

```text
observe
→ reflect
→ name_pattern
→ suggest_adjustment
→ ask_consent
→ apply_small_change
→ record_learning_only_if_approved
```

The loop is deliberately not a hidden runtime service. It is a structured review artifact that can be used inside chat while keeping side effects at zero.

## Harness fields

Every preview card should carry these fields:

| Field | Meaning |
|---|---|
| `session_goal` | What this preview moment is trying to improve or clarify. |
| `hypothesis` | What we believe the loop may help with. |
| `observed_signal` | The concrete user/context signal that triggered the reflection. |
| `observation` | What Lumi noticed, written soberly. |
| `reflection` | What the observation may mean, including uncertainty. |
| `pattern_name` | A short non-mythological name for the pattern. |
| `proposed_adjustment` | The smallest useful change to apply. |
| `consent_state` | `ask_before_apply`, `approved`, or `draft_only`. |
| `outcome` | What happened after the adjustment, if any. |
| `failure_mode` | What went wrong or could go wrong. |
| `acceptance_evidence` | What would prove this intervention was useful and safe. |

Required before a preview card can be draft-ready:

```text
session_goal
observation
reflection
pattern_name
proposed_adjustment
consent_state
```

Missing required fields fail closed.

## Safety contract

A preview loop card must always declare:

```text
canonical_writes: 0
runtime_actions: []
external_model_use: ask_each_time
memory_promotion: review_required
requires_human_review: true
```

The preview card must reject private Hermes runtime fields such as chat IDs, job IDs, scheduler queues, and runtime state.

## Officialization sprints

### Sprint 1 — Research Harness Contract

Define the harness schema, required fields, evidence format, failure modes, and acceptance criteria.

Acceptance: a preview session can produce a structured artifact from input to observation, hypothesis, action, feedback, result, and lesson.

### Sprint 2 — Preview Loop Protocol

Define how Lumi operates inside chat: state labels, consent language, when to speak, when to stay quiet, and how to ask before applying.

Acceptance: a real conversation can run through preview mode without confusion about what is active.

### Sprint 3 — Signal / Reflection Schema

Define what counts as a signal, reflection, contradiction, confidence, consent, and adjustment.

Acceptance: Nuances can steer current work without silently becoming durable memory or shared product truth.

### Sprint 4 — Consent, Memory Boundary, and Safety

Prevent silent memory promotion, private-thought extraction, credential leaks, identity drift, or automated public actions.

Acceptance: every durable learning has approval, provenance, and deletion/ignore paths.

### Sprint 5 — Evaluation and Acceptance Criteria

Build fixtures and checks for useful intervention, restraint, false positives, overreach, silence, repair, and consent behavior.

Acceptance: the harness can score Lumi on usefulness, restraint, consent, confidence, and safety.

### Sprint 6 — Official 0.1.0 Packaging / Release Notes

Reconcile the technical `v0.1.0` artifact with the official product readiness story: docs, limitations, examples, release notes, and known boundaries.

Acceptance: a new evaluator can understand what 0.1.0 is, what it is not, and how to evaluate it.

### Sprint 7 — Live Preview Run in This Chat

Run real preview moments in chat, collect feedback, summarize lessons, and decide what becomes durable only with approval.

Acceptance: after the preview run, we can honestly say what worked, what felt natural, what felt too much, what needs fixing, and whether 0.1.0 can become official.

## First live preview card

```json
{
  "schema": "lumi.hermes.preview_loop_card.v1",
  "mode": "preview_0_1_0",
  "release_label": "0.1.0 preview with research harness",
  "status": "draft_ready_for_review",
  "loop": [
    "observe",
    "reflect",
    "name_pattern",
    "suggest_adjustment",
    "ask_consent",
    "apply_small_change",
    "record_learning_only_if_approved"
  ],
  "harness": {
    "session_goal": "Shape actual Lumi 0.1.0 with research harness in chat.",
    "hypothesis": "A visible preview harness makes Lumi useful without pretending it is an autonomous service.",
    "observed_signal": "Explicit user request to implement the preview loop here.",
    "observation": "The user wants implementation before officialization sprints.",
    "reflection": "This needs a bounded in-chat loop, not hidden automation or silent memory promotion.",
    "pattern_name": "officialization-before-automation",
    "proposed_adjustment": "Use preview cards for each major Lumi intervention, ask before applying durable changes, and keep all writes at zero until approved.",
    "consent_state": "ask_before_apply",
    "outcome": "",
    "failure_mode": "The loop could become performative bureaucracy if used too often.",
    "acceptance_evidence": "The user can understand, approve/revise/reject, and later evaluate the intervention."
  },
  "safety": {
    "canonical_writes": 0,
    "runtime_actions": [],
    "external_model_use": "ask_each_time",
    "memory_promotion": "review_required",
    "requires_human_review": true
  }
}
```
