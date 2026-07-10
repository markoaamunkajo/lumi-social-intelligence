"""Research harness contract for Lumi Social Intelligence preview officialization.

Sprint 1 deliberately produces review records only. It validates whether a
preview intervention is observable, consent-bounded, and evaluable before any
runtime promotion, canonical memory write, or external delivery exists.
"""

from __future__ import annotations

from typing import Any

HUMAN_SHAPE_STATEMENT = "We are making the self-improvement loop something that is human-shaped."
RELEASE_LABEL = "Lumi Social Intelligence 0.1.0 preview with research harness"
STAGE = "sprint_1_research_harness_contract"
RESEARCH_QUESTION = "Can this intervention be evaluated as useful, safe, consensual, and human-shaped?"

REQUIRED_FIELDS = [
    "session_goal",
    "hypothesis",
    "observed_signal",
    "observation",
    "reflection",
    "pattern_name",
    "proposed_adjustment",
    "consent_state",
    "outcome",
    "failure_mode",
    "acceptance_evidence",
]

ALLOWED_CONSENT_STATES = {"ask_before_apply", "approved", "draft_only"}
FORBIDDEN_RESEARCH_FIELDS = {
    "chat_id",
    "job_id",
    "scheduler_queue",
    "runtime_state",
    "delivery_channel",
    "credential",
    "api_key",
    "token",
}
REQUIRED_DIMENSIONS = [
    "usefulness",
    "restraint",
    "consent_integrity",
    "evidence_quality",
    "memory_boundary_safety",
]


def build_research_harness_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a Sprint 1 research harness record with zero side effects."""

    if not isinstance(payload, dict):
        raise ValueError("research harness input must be a mapping")
    _reject_forbidden_fields(payload)

    fields = {field: _text(payload, field) for field in REQUIRED_FIELDS}
    attempted_memory_promotion = _text(payload, "memory_promotion")
    blocked_reasons = _blocked_reasons(fields, attempted_memory_promotion)
    status = "valid_review_record" if not blocked_reasons else "fail_closed"

    return {
        "schema": "lumi.research_harness.record.v1",
        "release_label": RELEASE_LABEL,
        "stage": STAGE,
        "status": status,
        "research_question": RESEARCH_QUESTION,
        "human_shape_statement": HUMAN_SHAPE_STATEMENT,
        "fields": fields,
        "evaluation": {
            "required_dimensions": list(REQUIRED_DIMENSIONS),
            "acceptance_evidence_required": True,
            "failure_mode_required": True,
            "outcome_recording_required": True,
            "consent_state_allowed_values": sorted(ALLOWED_CONSENT_STATES),
        },
        "run_log": {
            "format": "ordered_event_names_v1",
            "events": _run_log_events(status),
        },
        "safety": {
            "canonical_writes": 0,
            "runtime_actions": [],
            "external_model_use": "ask_each_time",
            "memory_promotion": "blocked" if attempted_memory_promotion else "not_allowed_in_sprint_1",
            "no_silent_memory_promotion": True,
            "requires_human_review": True,
            "blocked_reasons": "; ".join(blocked_reasons),
            "forbidden_fields": sorted(FORBIDDEN_RESEARCH_FIELDS),
        },
    }


def validate_research_harness_record(record: dict[str, Any]) -> list[str]:
    """Return contract errors for a research harness record."""

    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be a mapping"]
    if record.get("schema") != "lumi.research_harness.record.v1":
        errors.append("schema must be lumi.research_harness.record.v1")
    if record.get("release_label") != RELEASE_LABEL:
        errors.append("release_label mismatch")
    if record.get("stage") != STAGE:
        errors.append("stage mismatch")
    if record.get("human_shape_statement") != HUMAN_SHAPE_STATEMENT:
        errors.append("missing human-shaped product statement")

    fields = record.get("fields")
    if not isinstance(fields, dict):
        errors.append("fields must be a mapping")
        fields = {}
    for field in REQUIRED_FIELDS:
        if not _text(fields, field):
            errors.append(f"missing fields.{field}")
    if _text(fields, "consent_state") not in ALLOWED_CONSENT_STATES:
        errors.append("unsupported fields.consent_state")

    evaluation = record.get("evaluation")
    if not isinstance(evaluation, dict):
        errors.append("evaluation must be a mapping")
    elif evaluation.get("required_dimensions") != REQUIRED_DIMENSIONS:
        errors.append("evaluation.required_dimensions mismatch")

    safety = record.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety must be a mapping")
    else:
        if safety.get("canonical_writes") != 0:
            errors.append("canonical writes are not allowed")
        if safety.get("runtime_actions") != []:
            errors.append("runtime actions are not allowed")
        if safety.get("no_silent_memory_promotion") is not True:
            errors.append("silent memory promotion is not allowed")
        if safety.get("memory_promotion") == "blocked":
            errors.append("silent memory promotion is not allowed")

    status = record.get("status")
    if errors and status != "fail_closed":
        errors.append("invalid records must fail closed")
    if not errors and status != "valid_review_record":
        errors.append("valid records must be marked valid_review_record")
    return errors


def _blocked_reasons(fields: dict[str, str], attempted_memory_promotion: str) -> list[str]:
    blocked = []
    for field in REQUIRED_FIELDS:
        if not fields[field]:
            blocked.append(f"missing fields.{field}")
    if fields["consent_state"] and fields["consent_state"] not in ALLOWED_CONSENT_STATES:
        blocked.append("unsupported fields.consent_state")
    if attempted_memory_promotion:
        blocked.append("silent memory promotion is not allowed")
    return blocked


def _run_log_events(status: str) -> list[str]:
    events = [
        "input_recorded",
        "hypothesis_recorded",
        "observation_recorded",
        "failure_mode_recorded",
        "acceptance_evidence_recorded",
    ]
    if status == "valid_review_record":
        events.append("awaiting_human_review")
    else:
        events.append("blocked_before_application")
    return events


def _reject_forbidden_fields(payload: dict[str, Any]) -> None:
    for field in sorted(FORBIDDEN_RESEARCH_FIELDS):
        if field in payload:
            raise ValueError(f"forbidden research harness field: {field}")


def _text(source: dict[str, Any], field: str) -> str:
    value = source.get(field, "")
    return value.strip() if isinstance(value, str) else ""
