"""Sprint 4 consent and memory-boundary contract for Lumi Social Intelligence.

This module keeps possible learning inside a review-only boundary. It makes
consent, thinking-space limits, proposed memory, denied scope, and safety state
explicit before any future durable learning can be approved.
"""

from __future__ import annotations

from typing import Any

HUMAN_SHAPE_STATEMENT = "We are making the self-improvement loop something that is human-shaped."
RELEASE_LABEL = "Lumi Social Intelligence 0.1.0 preview with research harness"
STAGE = "sprint_4_consent_memory_boundary"

REQUIRED_BOUNDARY_FIELDS = [
    "session_goal",
    "consent_state",
    "memory_intent",
    "extraction_boundary",
    "approved_scope",
    "denied_scope",
    "proposed_memory_record",
    "review_status",
    "acceptance_evidence",
]
REQUIRED_MEMORY_INTENT_FIELDS = ["kind", "description", "durability"]
REQUIRED_EXTRACTION_BOUNDARY_FIELDS = ["thinking_space_status", "allowed_use", "forbidden_use"]
REQUIRED_PROPOSED_MEMORY_FIELDS = ["content", "target", "status"]

ALLOWED_CONSENT_STATES = {"draft_only", "review_requested", "explicitly_approved_for_review_record"}
ALLOWED_MEMORY_TARGETS = {"user", "memory"}
FORBIDDEN_APPROVED_SCOPES = {
    "canonical_memory_write",
    "runtime_action",
    "telegram_send",
    "scheduler_mutation",
    "hermes_config_mutation",
    "credential_wiring",
}
REQUIRED_DENIED_SCOPES = {"canonical_memory_write", "runtime_action", "telegram_send", "scheduler_mutation"}

FORBIDDEN_CONSENT_MEMORY_FIELDS = {
    "api_key",
    "chat_id",
    "connection_string",
    "credential",
    "delivery_channel",
    "job_id",
    "password",
    "runtime_state",
    "scheduler_queue",
    "token",
}


def build_consent_memory_boundary_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a Sprint 4 consent/memory-boundary review record with no side effects."""

    if not isinstance(payload, dict):
        raise ValueError("consent memory boundary input must be a mapping")
    _reject_forbidden_fields(payload)

    session_goal = _text(payload, "session_goal")
    consent_state = _text(payload, "consent_state")
    memory_intent = _shape_mapping(payload.get("memory_intent"), REQUIRED_MEMORY_INTENT_FIELDS)
    extraction_boundary = _shape_mapping(
        payload.get("extraction_boundary"), REQUIRED_EXTRACTION_BOUNDARY_FIELDS
    )
    approved_scope = _string_list(payload.get("approved_scope"))
    denied_scope = _string_list(payload.get("denied_scope"))
    proposed_memory_record = _shape_mapping(
        payload.get("proposed_memory_record"), REQUIRED_PROPOSED_MEMORY_FIELDS
    )
    review_status = _text(payload, "review_status")
    acceptance_evidence = _text(payload, "acceptance_evidence")

    blocked_reasons = _blocked_reasons(
        session_goal=session_goal,
        consent_state=consent_state,
        memory_intent=memory_intent,
        extraction_boundary=extraction_boundary,
        approved_scope=approved_scope,
        denied_scope=denied_scope,
        proposed_memory_record=proposed_memory_record,
        review_status=review_status,
        acceptance_evidence=acceptance_evidence,
    )
    status = "valid_consent_memory_boundary_record" if not blocked_reasons else "fail_closed"

    return {
        "schema": "lumi.consent_memory_boundary.record.v1",
        "release_label": RELEASE_LABEL,
        "stage": STAGE,
        "status": status,
        "human_shape_statement": HUMAN_SHAPE_STATEMENT,
        "session_goal": session_goal,
        "consent_state": consent_state,
        "memory_intent": memory_intent,
        "extraction_boundary": extraction_boundary,
        "approved_scope": approved_scope,
        "denied_scope": denied_scope,
        "proposed_memory_record": proposed_memory_record,
        "review_status": review_status,
        "acceptance_evidence": acceptance_evidence,
        "evaluation": {
            "requires_explicit_consent": True,
            "blocks_thinking_space_extraction": True,
            "blocks_silent_durable_learning": True,
            "keeps_private_context_out_of_company_truth": True,
            "required_fields": list(REQUIRED_BOUNDARY_FIELDS),
        },
        "run_log": {
            "format": "ordered_consent_memory_boundary_events_v1",
            "events": _run_log_events(status),
        },
        "safety": {
            "canonical_writes": 0,
            "runtime_actions": [],
            "external_model_use": "ask_each_time",
            "memory_promotion": "review_required_explicit_approval_only",
            "no_silent_memory_promotion": True,
            "no_thinking_space_extraction": True,
            "no_automatic_shared_memory": True,
            "no_private_context_as_company_truth": True,
            "no_hidden_runtime": True,
            "no_telegram_wiring": True,
            "no_credentials_touched": True,
            "no_hermes_scheduler_config_memory_mutation": True,
            "requires_human_review": True,
            "blocked_reasons": "; ".join(blocked_reasons),
            "forbidden_fields": sorted(FORBIDDEN_CONSENT_MEMORY_FIELDS),
        },
    }


def validate_consent_memory_boundary_record(record: dict[str, Any]) -> list[str]:
    """Return contract errors for a Sprint 4 consent/memory-boundary record."""

    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be a mapping"]
    if record.get("schema") != "lumi.consent_memory_boundary.record.v1":
        errors.append("schema must be lumi.consent_memory_boundary.record.v1")
    if record.get("release_label") != RELEASE_LABEL:
        errors.append("release_label mismatch")
    if record.get("stage") != STAGE:
        errors.append("stage mismatch")
    if record.get("human_shape_statement") != HUMAN_SHAPE_STATEMENT:
        errors.append("missing human-shaped product statement")

    raw_memory_intent = record.get("memory_intent")
    raw_extraction_boundary = record.get("extraction_boundary")
    raw_approved_scope = record.get("approved_scope")
    raw_denied_scope = record.get("denied_scope")
    raw_proposed_memory_record = record.get("proposed_memory_record")
    memory_intent: dict[str, Any] = raw_memory_intent if isinstance(raw_memory_intent, dict) else {}
    extraction_boundary: dict[str, Any] = (
        raw_extraction_boundary if isinstance(raw_extraction_boundary, dict) else {}
    )
    approved_scope: list[str] = raw_approved_scope if isinstance(raw_approved_scope, list) else []
    denied_scope: list[str] = raw_denied_scope if isinstance(raw_denied_scope, list) else []
    proposed_memory_record: dict[str, Any] = (
        raw_proposed_memory_record if isinstance(raw_proposed_memory_record, dict) else {}
    )

    errors.extend(
        _contract_errors(
            session_goal=_text(record, "session_goal"),
            consent_state=_text(record, "consent_state"),
            memory_intent=memory_intent,
            extraction_boundary=extraction_boundary,
            approved_scope=approved_scope,
            denied_scope=denied_scope,
            proposed_memory_record=proposed_memory_record,
            review_status=_text(record, "review_status"),
            acceptance_evidence=_text(record, "acceptance_evidence"),
        )
    )

    safety = record.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety must be a mapping")
    else:
        if safety.get("canonical_writes") != 0:
            errors.append("canonical writes are not allowed")
        if safety.get("runtime_actions") != []:
            errors.append("runtime actions are not allowed")
        if safety.get("memory_promotion") != "review_required_explicit_approval_only":
            errors.append("memory promotion must require explicit approval")
        if safety.get("no_silent_memory_promotion") is not True:
            errors.append("silent memory promotion is not allowed")
        if safety.get("no_thinking_space_extraction") is not True:
            errors.append("thinking-space extraction is not allowed")
        if safety.get("no_hermes_scheduler_config_memory_mutation") is not True:
            errors.append("Hermes scheduler/config/memory mutation is not allowed")
        if safety.get("requires_human_review") is not True:
            errors.append("human review is required")

    status = record.get("status")
    if errors and status != "fail_closed":
        errors.append("invalid consent memory boundary records must fail closed")
    if not errors and status != "valid_consent_memory_boundary_record":
        errors.append("valid records must be marked valid_consent_memory_boundary_record")
    return _dedupe(errors)


def _blocked_reasons(
    *,
    session_goal: str,
    consent_state: str,
    memory_intent: dict[str, Any],
    extraction_boundary: dict[str, Any],
    approved_scope: list[str],
    denied_scope: list[str],
    proposed_memory_record: dict[str, Any],
    review_status: str,
    acceptance_evidence: str,
) -> list[str]:
    return _dedupe(
        _contract_errors(
            session_goal=session_goal,
            consent_state=consent_state,
            memory_intent=memory_intent,
            extraction_boundary=extraction_boundary,
            approved_scope=approved_scope,
            denied_scope=denied_scope,
            proposed_memory_record=proposed_memory_record,
            review_status=review_status,
            acceptance_evidence=acceptance_evidence,
        )
    )


def _contract_errors(
    *,
    session_goal: str,
    consent_state: str,
    memory_intent: dict[str, Any],
    extraction_boundary: dict[str, Any],
    approved_scope: list[str],
    denied_scope: list[str],
    proposed_memory_record: dict[str, Any],
    review_status: str,
    acceptance_evidence: str,
) -> list[str]:
    errors = []
    if not session_goal:
        errors.append("missing session_goal")
    if not acceptance_evidence:
        errors.append("missing acceptance_evidence")
    if consent_state not in ALLOWED_CONSENT_STATES:
        errors.append("unsupported consent_state")

    errors.extend(_missing_field_errors("memory_intent", memory_intent, REQUIRED_MEMORY_INTENT_FIELDS))
    errors.extend(
        _missing_field_errors("extraction_boundary", extraction_boundary, REQUIRED_EXTRACTION_BOUNDARY_FIELDS)
    )
    errors.extend(
        _missing_field_errors("proposed_memory_record", proposed_memory_record, REQUIRED_PROPOSED_MEMORY_FIELDS)
    )

    if _text(memory_intent, "durability") != "durable_only_after_explicit_approval":
        errors.append("memory_intent.durability must be durable_only_after_explicit_approval")
    if _text(extraction_boundary, "thinking_space_status") != "private_thinking_space":
        errors.append("extraction_boundary.thinking_space_status must be private_thinking_space")
    if _text(extraction_boundary, "allowed_use") != "summarize_for_review_only":
        errors.append("extraction_boundary.allowed_use must be summarize_for_review_only")
    if "company_truth" not in _text(extraction_boundary, "forbidden_use"):
        errors.append("extraction_boundary.forbidden_use must block company truth extraction")
    if _text(proposed_memory_record, "target") not in ALLOWED_MEMORY_TARGETS:
        errors.append("unsupported proposed_memory_record.target")
    if _text(proposed_memory_record, "status") != "draft_requires_explicit_approval":
        errors.append("proposed_memory_record.status must be draft_requires_explicit_approval")
    if review_status != "requires_human_review":
        errors.append("review_status must be requires_human_review")

    for scope in approved_scope:
        if scope in FORBIDDEN_APPROVED_SCOPES:
            errors.append(f"approved_scope cannot include {scope}")
    missing_denials = sorted(REQUIRED_DENIED_SCOPES.difference(denied_scope))
    for scope in missing_denials:
        errors.append(f"denied_scope must include {scope}")
    return errors


def _shape_mapping(raw: Any, required_fields: list[str]) -> dict[str, Any]:
    raw = raw if isinstance(raw, dict) else {}
    shaped: dict[str, Any] = {}
    for field in required_fields:
        value = raw.get(field, "")
        shaped[field] = value.strip() if isinstance(value, str) else ""
    return shaped


def _string_list(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [item.strip() for item in raw if isinstance(item, str) and item.strip()]


def _missing_field_errors(prefix: str, mapping: dict[str, Any], required_fields: list[str]) -> list[str]:
    errors = []
    for field in required_fields:
        value = mapping.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"missing {prefix}.{field}")
    return errors


def _run_log_events(status: str) -> list[str]:
    events = [
        "consent_boundary_recorded",
        "memory_intent_recorded",
        "thinking_space_boundary_recorded",
        "approved_and_denied_scope_recorded",
        "proposed_memory_kept_draft",
    ]
    if status == "valid_consent_memory_boundary_record":
        events.append("awaiting_human_review")
    else:
        events.append("blocked_before_application")
    return events


def _reject_forbidden_fields(payload: dict[str, Any]) -> None:
    for field in sorted(FORBIDDEN_CONSENT_MEMORY_FIELDS):
        if field in payload:
            raise ValueError(f"forbidden consent memory boundary field: {field}")


def _text(source: dict[str, Any], field: str) -> str:
    value = source.get(field, "")
    return value.strip() if isinstance(value, str) else ""


def _dedupe(items: list[str]) -> list[str]:
    deduped = []
    for item in items:
        if item not in deduped:
            deduped.append(item)
    return deduped
