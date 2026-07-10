"""Sprint 5 evaluation and acceptance criteria for Lumi Social Intelligence.

This module defines what "good enough for official 0.1.0" means before any
packaging/release-note sprint can proceed. It is intentionally review-only: it
records acceptance gates and evidence expectations, not runtime actions.
"""

from __future__ import annotations

from typing import Any

HUMAN_SHAPE_STATEMENT = "We are making the self-improvement loop something that is human-shaped."
RELEASE_LABEL = "Lumi Social Intelligence 0.1.0 preview with research harness"
STAGE = "sprint_5_evaluation_acceptance_criteria"

REQUIRED_ACCEPTANCE_FIELDS = [
    "session_goal",
    "candidate_version",
    "evaluation_dimensions",
    "acceptance_checks",
    "minimum_evidence",
    "decision",
    "review_status",
    "acceptance_evidence",
]
REQUIRED_EVALUATION_DIMENSIONS = [
    "research_harness_contract",
    "preview_loop_protocol",
    "signal_reflection_schema",
    "consent_memory_boundary",
    "public_release_safety",
]
REQUIRED_ACCEPTANCE_CHECKS = {
    "focused_tests_pass",
    "combined_officialization_tests_pass",
    "release_check_passes",
    "public_secret_scan_passes",
    "clean_checkout_smoke_passes",
}
REQUIRED_MINIMUM_EVIDENCE_FIELDS = ["focused_tests", "combined_tests", "release_gate"]
REQUIRED_DECISION_FIELDS = ["status", "allowed_next_step", "blocked_until"]
FORBIDDEN_EVALUATION_ACCEPTANCE_FIELDS = {
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


def build_evaluation_acceptance_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a Sprint 5 officialization acceptance record with no side effects."""

    if not isinstance(payload, dict):
        raise ValueError("evaluation acceptance input must be a mapping")
    _reject_forbidden_fields(payload)

    session_goal = _text(payload, "session_goal")
    candidate_version = _text(payload, "candidate_version")
    evaluation_dimensions = _dimension_list(payload.get("evaluation_dimensions"))
    acceptance_checks = _string_list(payload.get("acceptance_checks"))
    minimum_evidence = _shape_mapping(payload.get("minimum_evidence"), REQUIRED_MINIMUM_EVIDENCE_FIELDS)
    decision = _shape_mapping(payload.get("decision"), REQUIRED_DECISION_FIELDS)
    review_status = _text(payload, "review_status")
    acceptance_evidence = _text(payload, "acceptance_evidence")

    blocked_reasons = _blocked_reasons(
        session_goal=session_goal,
        candidate_version=candidate_version,
        evaluation_dimensions=evaluation_dimensions,
        acceptance_checks=acceptance_checks,
        minimum_evidence=minimum_evidence,
        decision=decision,
        review_status=review_status,
        acceptance_evidence=acceptance_evidence,
    )
    status = "valid_evaluation_acceptance_record" if not blocked_reasons else "fail_closed"

    return {
        "schema": "lumi.evaluation_acceptance.record.v1",
        "release_label": RELEASE_LABEL,
        "stage": STAGE,
        "status": status,
        "human_shape_statement": HUMAN_SHAPE_STATEMENT,
        "session_goal": session_goal,
        "candidate_version": candidate_version,
        "evaluation_dimensions": evaluation_dimensions,
        "acceptance_checks": acceptance_checks,
        "minimum_evidence": minimum_evidence,
        "decision": decision,
        "review_status": review_status,
        "acceptance_evidence": acceptance_evidence,
        "evaluation": {
            "definition": "good_enough_for_official_0_1_0",
            "required_dimensions": list(REQUIRED_EVALUATION_DIMENSIONS),
            "required_checks": sorted(REQUIRED_ACCEPTANCE_CHECKS),
            "blocks_packaging_without_evidence": True,
        },
        "run_log": {
            "format": "ordered_evaluation_acceptance_events_v1",
            "events": _run_log_events(status),
        },
        "safety": {
            "canonical_writes": 0,
            "runtime_actions": [],
            "external_model_use": "ask_each_time",
            "memory_promotion": "review_required_explicit_approval_only",
            "no_silent_memory_promotion": True,
            "no_thinking_space_extraction": True,
            "no_hidden_runtime": True,
            "no_telegram_wiring": True,
            "no_credentials_touched": True,
            "no_hermes_scheduler_config_memory_mutation": True,
            "no_official_release_without_evidence": True,
            "requires_human_review": True,
            "blocked_reasons": "; ".join(blocked_reasons),
            "forbidden_fields": sorted(FORBIDDEN_EVALUATION_ACCEPTANCE_FIELDS),
        },
    }


def validate_evaluation_acceptance_record(record: dict[str, Any]) -> list[str]:
    """Return contract errors for a Sprint 5 evaluation/acceptance record."""

    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be a mapping"]
    if record.get("schema") != "lumi.evaluation_acceptance.record.v1":
        errors.append("schema must be lumi.evaluation_acceptance.record.v1")
    if record.get("release_label") != RELEASE_LABEL:
        errors.append("release_label mismatch")
    if record.get("stage") != STAGE:
        errors.append("stage mismatch")
    if record.get("human_shape_statement") != HUMAN_SHAPE_STATEMENT:
        errors.append("missing human-shaped product statement")

    raw_dimensions = record.get("evaluation_dimensions")
    raw_acceptance_checks = record.get("acceptance_checks")
    raw_minimum_evidence = record.get("minimum_evidence")
    raw_decision = record.get("decision")
    evaluation_dimensions = raw_dimensions if isinstance(raw_dimensions, list) else []
    acceptance_checks = raw_acceptance_checks if isinstance(raw_acceptance_checks, list) else []
    minimum_evidence = raw_minimum_evidence if isinstance(raw_minimum_evidence, dict) else {}
    decision = raw_decision if isinstance(raw_decision, dict) else {}

    errors.extend(
        _contract_errors(
            session_goal=_text(record, "session_goal"),
            candidate_version=_text(record, "candidate_version"),
            evaluation_dimensions=evaluation_dimensions,
            acceptance_checks=acceptance_checks,
            minimum_evidence=minimum_evidence,
            decision=decision,
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
        if safety.get("requires_human_review") is not True:
            errors.append("human review is required")
        if safety.get("no_official_release_without_evidence") is not True:
            errors.append("official release cannot proceed without evidence")
        if safety.get("no_hermes_scheduler_config_memory_mutation") is not True:
            errors.append("Hermes scheduler/config/memory mutation is not allowed")

    status = record.get("status")
    if errors and status != "fail_closed":
        errors.append("invalid evaluation acceptance records must fail closed")
    if not errors and status != "valid_evaluation_acceptance_record":
        errors.append("valid records must be marked valid_evaluation_acceptance_record")
    return _dedupe(errors)


def _blocked_reasons(
    *,
    session_goal: str,
    candidate_version: str,
    evaluation_dimensions: list[dict[str, Any]],
    acceptance_checks: list[str],
    minimum_evidence: dict[str, Any],
    decision: dict[str, Any],
    review_status: str,
    acceptance_evidence: str,
) -> list[str]:
    return _dedupe(
        _contract_errors(
            session_goal=session_goal,
            candidate_version=candidate_version,
            evaluation_dimensions=evaluation_dimensions,
            acceptance_checks=acceptance_checks,
            minimum_evidence=minimum_evidence,
            decision=decision,
            review_status=review_status,
            acceptance_evidence=acceptance_evidence,
        )
    )


def _contract_errors(
    *,
    session_goal: str,
    candidate_version: str,
    evaluation_dimensions: list[dict[str, Any]],
    acceptance_checks: list[str],
    minimum_evidence: dict[str, Any],
    decision: dict[str, Any],
    review_status: str,
    acceptance_evidence: str,
) -> list[str]:
    errors: list[str] = []
    for field, value in {
        "session_goal": session_goal,
        "candidate_version": candidate_version,
        "review_status": review_status,
        "acceptance_evidence": acceptance_evidence,
    }.items():
        if not value:
            errors.append(f"missing {field}")

    dimensions_by_name: dict[str, dict[str, Any]] = {}
    for item in evaluation_dimensions:
        if not isinstance(item, dict):
            errors.append("evaluation_dimensions entries must be mappings")
            continue
        name = _str(item.get("name"))
        if not name:
            errors.append("evaluation dimension missing name")
            continue
        dimensions_by_name[name] = item
        if _str(item.get("required_status")) != "pass":
            errors.append(f"evaluation dimension {name} must require pass")
        if not _str(item.get("evidence")):
            errors.append(f"evaluation dimension {name} missing evidence")

    for required in REQUIRED_EVALUATION_DIMENSIONS:
        if required not in dimensions_by_name:
            errors.append(f"missing evaluation dimension: {required}")

    checks = set(acceptance_checks)
    for required in sorted(REQUIRED_ACCEPTANCE_CHECKS):
        if required not in checks:
            errors.append(f"acceptance_checks must include {required}")

    for field in REQUIRED_MINIMUM_EVIDENCE_FIELDS:
        if not _str(minimum_evidence.get(field)):
            errors.append(f"missing minimum_evidence.{field}")

    if _str(decision.get("status")) != "candidate_under_review":
        errors.append("decision.status must be candidate_under_review")
    if _str(decision.get("allowed_next_step")) != "official_0_1_0_packaging_review":
        errors.append("decision.allowed_next_step must be official_0_1_0_packaging_review")
    if _str(decision.get("blocked_until")) != "all_acceptance_checks_pass_with_evidence":
        errors.append("decision.blocked_until must be all_acceptance_checks_pass_with_evidence")
    if review_status != "requires_human_review":
        errors.append("review_status must be requires_human_review")
    return errors


def _dimension_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    shaped: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            shaped.append({"name": "", "required_status": "", "evidence": ""})
            continue
        shaped.append(
            {
                "name": _str(item.get("name")),
                "required_status": _str(item.get("required_status")),
                "evidence": _str(item.get("evidence")),
            }
        )
    return shaped


def _shape_mapping(value: Any, required_fields: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {field: "" for field in required_fields}
    return {field: _str(value.get(field)) for field in required_fields}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_str(item) for item in value if _str(item)]


def _run_log_events(status: str) -> list[str]:
    events = [
        "evaluation_acceptance_record_created",
        "official_0_1_0_candidate_scored_against_required_dimensions",
        "release_evidence_required_before_packaging",
    ]
    if status == "valid_evaluation_acceptance_record":
        events.append("awaiting_human_review_for_official_packaging")
    else:
        events.append("blocked_before_official_packaging")
    return events


def _reject_forbidden_fields(payload: dict[str, Any]) -> None:
    for key in payload:
        if key in FORBIDDEN_EVALUATION_ACCEPTANCE_FIELDS:
            raise ValueError(f"forbidden evaluation acceptance field: {key}")


def _text(mapping: dict[str, Any], key: str) -> str:
    return _str(mapping.get(key))


def _str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _dedupe(errors: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for error in errors:
        if error not in seen:
            deduped.append(error)
            seen.add(error)
    return deduped
