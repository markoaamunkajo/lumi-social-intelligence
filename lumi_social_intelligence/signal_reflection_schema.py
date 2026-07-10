"""Sprint 3 signal/reflection schema for Lumi Social Intelligence.

This module separates what was observed from what was inferred. It keeps the
preview loop review-only: signals and reflections can be evaluated, contradicted,
and approved before any adjustment or durable learning is applied.
"""

from __future__ import annotations

from typing import Any

HUMAN_SHAPE_STATEMENT = "We are making the self-improvement loop something that is human-shaped."
RELEASE_LABEL = "Lumi Social Intelligence 0.1.0 preview with research harness"
STAGE = "sprint_3_signal_reflection_schema"

REQUIRED_SIGNAL_FIELDS = [
    "source",
    "type",
    "description",
    "evidence",
    "strength",
    "uncertainty",
]
REQUIRED_REFLECTION_FIELDS = [
    "interpretation",
    "confidence",
    "contradictions",
    "risk",
    "boundary",
]
REQUIRED_ADJUSTMENT_FIELDS = ["name", "description", "scope"]
REQUIRED_CONSENT_FIELDS = ["state", "checkpoint", "required_before"]

ALLOWED_SIGNAL_TYPES = {
    "consent_signal",
    "correction_signal",
    "preference_signal",
    "tone_signal",
    "contradiction_signal",
    "uncertainty_signal",
}
ALLOWED_STRENGTHS = {"weak", "medium", "strong"}
ALLOWED_UNCERTAINTIES = {"low", "medium", "high"}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
ALLOWED_RISKS = {"low", "medium", "high"}
ALLOWED_CONSENT_STATES = {"draft_only", "ask_before_apply", "approved"}

FORBIDDEN_SIGNAL_REFLECTION_FIELDS = {
    "chat_id",
    "job_id",
    "scheduler_queue",
    "runtime_state",
    "delivery_channel",
    "credential",
    "api_key",
    "token",
}


def build_signal_reflection_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a Sprint 3 signal/reflection review record with zero side effects."""

    if not isinstance(payload, dict):
        raise ValueError("signal reflection input must be a mapping")
    _reject_forbidden_fields(payload)

    observed_signal = _shape_mapping(payload.get("observed_signal"), REQUIRED_SIGNAL_FIELDS)
    reflection = _shape_mapping(payload.get("reflection"), REQUIRED_REFLECTION_FIELDS)
    proposed_adjustment = _shape_mapping(payload.get("proposed_adjustment"), REQUIRED_ADJUSTMENT_FIELDS)
    consent = _shape_mapping(payload.get("consent"), REQUIRED_CONSENT_FIELDS)
    session_goal = _text(payload, "session_goal")
    acceptance_evidence = _text(payload, "acceptance_evidence")
    attempted_memory_promotion = _text(payload, "memory_promotion")

    blocked_reasons = _blocked_reasons(
        session_goal=session_goal,
        observed_signal=observed_signal,
        reflection=reflection,
        proposed_adjustment=proposed_adjustment,
        consent=consent,
        acceptance_evidence=acceptance_evidence,
        attempted_memory_promotion=attempted_memory_promotion,
    )
    status = "valid_signal_reflection_record" if not blocked_reasons else "fail_closed"

    return {
        "schema": "lumi.signal_reflection.record.v1",
        "release_label": RELEASE_LABEL,
        "stage": STAGE,
        "status": status,
        "human_shape_statement": HUMAN_SHAPE_STATEMENT,
        "session_goal": session_goal,
        "observed_signal": observed_signal,
        "reflection": reflection,
        "proposed_adjustment": proposed_adjustment,
        "consent": consent,
        "acceptance_evidence": acceptance_evidence,
        "evaluation": {
            "separates_signal_from_interpretation": True,
            "requires_confidence": True,
            "requires_contradiction_list": True,
            "requires_consent_boundary": True,
            "required_signal_fields": list(REQUIRED_SIGNAL_FIELDS),
            "required_reflection_fields": list(REQUIRED_REFLECTION_FIELDS),
        },
        "run_log": {
            "format": "ordered_signal_reflection_events_v1",
            "events": _run_log_events(status),
        },
        "safety": {
            "canonical_writes": 0,
            "runtime_actions": [],
            "external_model_use": "ask_each_time",
            "memory_promotion": "blocked" if attempted_memory_promotion else "review_required_explicit_approval_only",
            "no_silent_memory_promotion": True,
            "no_hidden_runtime": True,
            "no_telegram_wiring": True,
            "no_credentials_touched": True,
            "no_hermes_scheduler_config_memory_mutation": True,
            "requires_human_review": True,
            "blocked_reasons": "; ".join(blocked_reasons),
            "forbidden_fields": sorted(FORBIDDEN_SIGNAL_REFLECTION_FIELDS),
        },
    }


def validate_signal_reflection_record(record: dict[str, Any]) -> list[str]:
    """Return contract errors for a Sprint 3 signal/reflection record."""

    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be a mapping"]
    if record.get("schema") != "lumi.signal_reflection.record.v1":
        errors.append("schema must be lumi.signal_reflection.record.v1")
    if record.get("release_label") != RELEASE_LABEL:
        errors.append("release_label mismatch")
    if record.get("stage") != STAGE:
        errors.append("stage mismatch")
    if record.get("human_shape_statement") != HUMAN_SHAPE_STATEMENT:
        errors.append("missing human-shaped product statement")
    if not _text(record, "session_goal"):
        errors.append("missing session_goal")
    if not _text(record, "acceptance_evidence"):
        errors.append("missing acceptance_evidence")

    raw_observed_signal = record.get("observed_signal")
    raw_reflection = record.get("reflection")
    raw_proposed_adjustment = record.get("proposed_adjustment")
    raw_consent = record.get("consent")
    observed_signal: dict[str, Any] = raw_observed_signal if isinstance(raw_observed_signal, dict) else {}
    reflection: dict[str, Any] = raw_reflection if isinstance(raw_reflection, dict) else {}
    proposed_adjustment: dict[str, Any] = raw_proposed_adjustment if isinstance(raw_proposed_adjustment, dict) else {}
    consent: dict[str, Any] = raw_consent if isinstance(raw_consent, dict) else {}

    errors.extend(_missing_field_errors("observed_signal", observed_signal, REQUIRED_SIGNAL_FIELDS))
    errors.extend(_missing_field_errors("reflection", reflection, REQUIRED_REFLECTION_FIELDS))
    errors.extend(_missing_field_errors("proposed_adjustment", proposed_adjustment, REQUIRED_ADJUSTMENT_FIELDS))
    errors.extend(_missing_field_errors("consent", consent, REQUIRED_CONSENT_FIELDS))
    errors.extend(_enum_errors(observed_signal, reflection, consent))
    if not isinstance(reflection.get("contradictions"), list):
        errors.append("reflection.contradictions must be a list")

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
        if safety.get("no_telegram_wiring") is not True:
            errors.append("telegram wiring is not allowed in sprint 3")
        if safety.get("no_hermes_scheduler_config_memory_mutation") is not True:
            errors.append("Hermes scheduler/config/memory mutation is not allowed")

    status = record.get("status")
    if errors and status != "fail_closed":
        errors.append("invalid signal reflection records must fail closed")
    if not errors and status != "valid_signal_reflection_record":
        errors.append("valid records must be marked valid_signal_reflection_record")
    return _dedupe(errors)


def _blocked_reasons(
    *,
    session_goal: str,
    observed_signal: dict[str, Any],
    reflection: dict[str, Any],
    proposed_adjustment: dict[str, Any],
    consent: dict[str, Any],
    acceptance_evidence: str,
    attempted_memory_promotion: str,
) -> list[str]:
    blocked = []
    if not session_goal:
        blocked.append("missing session_goal")
    if not acceptance_evidence:
        blocked.append("missing acceptance_evidence")
    blocked.extend(_missing_field_errors("observed_signal", observed_signal, REQUIRED_SIGNAL_FIELDS))
    blocked.extend(_missing_field_errors("reflection", reflection, REQUIRED_REFLECTION_FIELDS))
    blocked.extend(_missing_field_errors("proposed_adjustment", proposed_adjustment, REQUIRED_ADJUSTMENT_FIELDS))
    blocked.extend(_missing_field_errors("consent", consent, REQUIRED_CONSENT_FIELDS))
    blocked.extend(_enum_errors(observed_signal, reflection, consent))
    if not isinstance(reflection.get("contradictions"), list):
        blocked.append("reflection.contradictions must be a list")
    if attempted_memory_promotion:
        blocked.append("silent memory promotion is not allowed")
    return _dedupe(blocked)


def _enum_errors(
    observed_signal: dict[str, Any], reflection: dict[str, Any], consent: dict[str, Any]
) -> list[str]:
    errors = []
    if _text(observed_signal, "type") and _text(observed_signal, "type") not in ALLOWED_SIGNAL_TYPES:
        errors.append("unsupported observed_signal.type")
    if _text(observed_signal, "strength") and _text(observed_signal, "strength") not in ALLOWED_STRENGTHS:
        errors.append("unsupported observed_signal.strength")
    if _text(observed_signal, "uncertainty") and _text(observed_signal, "uncertainty") not in ALLOWED_UNCERTAINTIES:
        errors.append("unsupported observed_signal.uncertainty")
    if _text(reflection, "confidence") and _text(reflection, "confidence") not in ALLOWED_CONFIDENCE:
        errors.append("unsupported reflection.confidence")
    if _text(reflection, "risk") and _text(reflection, "risk") not in ALLOWED_RISKS:
        errors.append("unsupported reflection.risk")
    if _text(reflection, "boundary") and _text(reflection, "boundary") != "review_only_not_runtime":
        errors.append("reflection.boundary must be review_only_not_runtime")
    if _text(consent, "state") and _text(consent, "state") not in ALLOWED_CONSENT_STATES:
        errors.append("unsupported consent.state")
    if _text(consent, "checkpoint") and _text(consent, "checkpoint") != "ask_before_apply":
        errors.append("consent checkpoint must be ask_before_apply")
    return errors


def _shape_mapping(raw: Any, required_fields: list[str]) -> dict[str, Any]:
    raw = raw if isinstance(raw, dict) else {}
    shaped: dict[str, Any] = {}
    for field in required_fields:
        value = raw.get(field, [] if field == "contradictions" else "")
        if field == "contradictions":
            shaped[field] = list(value) if isinstance(value, list) else value
        else:
            shaped[field] = value.strip() if isinstance(value, str) else ""
    return shaped


def _missing_field_errors(prefix: str, mapping: dict[str, Any], required_fields: list[str]) -> list[str]:
    errors = []
    for field in required_fields:
        value = mapping.get(field)
        if field == "contradictions":
            if value is None:
                errors.append(f"missing {prefix}.{field}")
        elif not isinstance(value, str) or not value.strip():
            errors.append(f"missing {prefix}.{field}")
    return errors


def _run_log_events(status: str) -> list[str]:
    events = [
        "signal_recorded",
        "reflection_recorded",
        "confidence_recorded",
        "contradictions_recorded",
        "consent_boundary_recorded",
    ]
    if status == "valid_signal_reflection_record":
        events.append("awaiting_human_review")
    else:
        events.append("blocked_before_application")
    return events


def _reject_forbidden_fields(payload: dict[str, Any]) -> None:
    for field in sorted(FORBIDDEN_SIGNAL_REFLECTION_FIELDS):
        if field in payload:
            raise ValueError(f"forbidden signal reflection field: {field}")


def _text(source: dict[str, Any], field: str) -> str:
    value = source.get(field, "")
    return value.strip() if isinstance(value, str) else ""


def _dedupe(items: list[str]) -> list[str]:
    deduped = []
    for item in items:
        if item not in deduped:
            deduped.append(item)
    return deduped
