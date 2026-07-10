"""Sprint 6 official 0.1.0 packaging and release-note review contract.

This module reconciles the already-existing public technical v0.1.0 release
with the product-readiness officialization work from Sprints 1-5. It drafts a
reviewable packaging record; it does not publish, tag, upload, notify, or mutate
runtime state.
"""

from __future__ import annotations

from typing import Any

HUMAN_SHAPE_STATEMENT = "We are making the self-improvement loop something that is human-shaped."
RELEASE_LABEL = "Lumi Social Intelligence 0.1.0 preview with research harness"
STAGE = "sprint_6_official_packaging_release_notes"

REQUIRED_PACKAGING_FIELDS = [
    "session_goal",
    "technical_release",
    "product_release",
    "officialization_evidence",
    "release_note_sections",
    "packaging_decision",
    "review_status",
    "acceptance_evidence",
]
REQUIRED_TECHNICAL_RELEASE_FIELDS = ["tag", "status", "url"]
REQUIRED_PRODUCT_RELEASE_FIELDS = ["version", "status", "positioning"]
REQUIRED_PACKAGING_DECISION_FIELDS = ["status", "allowed_action", "blocked_action"]
REQUIRED_OFFICIALIZATION_EVIDENCE = [
    "sprint_1_research_harness_contract_passed",
    "sprint_2_preview_loop_protocol_passed",
    "sprint_3_signal_reflection_schema_passed",
    "sprint_4_consent_memory_boundary_passed",
    "sprint_5_evaluation_acceptance_criteria_passed",
    "release_check_passed",
]
REQUIRED_RELEASE_NOTE_SECTIONS = [
    "technical_release_exists",
    "product_readiness_delta",
    "officialization_sprints",
    "safety_boundaries",
    "verification_evidence",
    "not_included",
    "human_review_next_step",
]
FORBIDDEN_OFFICIAL_PACKAGING_FIELDS = {
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


def build_official_packaging_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a Sprint 6 official packaging/release-note candidate record."""

    if not isinstance(payload, dict):
        raise ValueError("official packaging input must be a mapping")
    _reject_forbidden_fields(payload)

    session_goal = _text(payload, "session_goal")
    technical_release = _shape_mapping(payload.get("technical_release"), REQUIRED_TECHNICAL_RELEASE_FIELDS)
    product_release = _shape_mapping(payload.get("product_release"), REQUIRED_PRODUCT_RELEASE_FIELDS)
    officialization_evidence = _string_list(payload.get("officialization_evidence"))
    release_note_sections = _string_list(payload.get("release_note_sections"))
    packaging_decision = _shape_mapping(payload.get("packaging_decision"), REQUIRED_PACKAGING_DECISION_FIELDS)
    review_status = _text(payload, "review_status")
    acceptance_evidence = _text(payload, "acceptance_evidence")

    blocked_reasons = _blocked_reasons(
        session_goal=session_goal,
        technical_release=technical_release,
        product_release=product_release,
        officialization_evidence=officialization_evidence,
        release_note_sections=release_note_sections,
        packaging_decision=packaging_decision,
        review_status=review_status,
        acceptance_evidence=acceptance_evidence,
    )
    status = "valid_official_packaging_record" if not blocked_reasons else "fail_closed"

    return {
        "schema": "lumi.official_packaging.record.v1",
        "release_label": RELEASE_LABEL,
        "stage": STAGE,
        "status": status,
        "human_shape_statement": HUMAN_SHAPE_STATEMENT,
        "session_goal": session_goal,
        "technical_release": technical_release,
        "product_release": product_release,
        "officialization_evidence": officialization_evidence,
        "release_note_sections": release_note_sections,
        "packaging_decision": packaging_decision,
        "review_status": review_status,
        "acceptance_evidence": acceptance_evidence,
        "release_notes": _release_notes_draft(
            technical_release=technical_release,
            product_release=product_release,
            officialization_evidence=officialization_evidence,
        ),
        "packaging": {
            "definition": "official_0_1_0_packaging_review",
            "technical_release_already_exists": technical_release.get("status") == "existing_public_technical_release",
            "product_readiness_is_review_candidate": product_release.get("status") == "official_packaging_candidate",
            "required_sections": list(REQUIRED_RELEASE_NOTE_SECTIONS),
            "publishing_requires_human_review": True,
        },
        "run_log": {
            "format": "ordered_official_packaging_events_v1",
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
            "no_publish_without_human_review": True,
            "no_release_claim_without_evidence": True,
            "requires_human_review": True,
            "forbidden_fields": sorted(FORBIDDEN_OFFICIAL_PACKAGING_FIELDS),
        },
        "blocked_reasons": blocked_reasons,
    }


def validate_official_packaging_record(record: dict[str, Any]) -> list[str]:
    """Return validation errors for a Sprint 6 packaging record."""

    if not isinstance(record, dict):
        return ["record must be a mapping"]

    errors: list[str] = []
    for field in REQUIRED_PACKAGING_FIELDS:
        if _is_empty(record.get(field)):
            errors.append(f"missing required packaging field: {field}")

    if record.get("schema") != "lumi.official_packaging.record.v1":
        errors.append("schema must be lumi.official_packaging.record.v1")
    if record.get("stage") != STAGE:
        errors.append(f"stage must be {STAGE}")

    errors.extend(
        _blocked_reasons(
            session_goal=_text(record, "session_goal"),
            technical_release=_shape_mapping(record.get("technical_release"), REQUIRED_TECHNICAL_RELEASE_FIELDS),
            product_release=_shape_mapping(record.get("product_release"), REQUIRED_PRODUCT_RELEASE_FIELDS),
            officialization_evidence=_string_list(record.get("officialization_evidence")),
            release_note_sections=_string_list(record.get("release_note_sections")),
            packaging_decision=_shape_mapping(record.get("packaging_decision"), REQUIRED_PACKAGING_DECISION_FIELDS),
            review_status=_text(record, "review_status"),
            acceptance_evidence=_text(record, "acceptance_evidence"),
        )
    )

    raw_safety = record.get("safety")
    safety: dict[str, Any] = raw_safety if isinstance(raw_safety, dict) else {}
    if safety.get("canonical_writes") != 0:
        errors.append("safety.canonical_writes must be 0")
    if safety.get("runtime_actions") != []:
        errors.append("safety.runtime_actions must be []")
    if safety.get("requires_human_review") is not True:
        errors.append("safety.requires_human_review must be true")
    if safety.get("no_publish_without_human_review") is not True:
        errors.append("safety.no_publish_without_human_review must be true")

    blocked_reasons = record.get("blocked_reasons", [])
    if errors and record.get("status") != "fail_closed":
        errors.append("invalid records with errors must fail closed")
    if not errors and blocked_reasons:
        errors.extend(str(reason) for reason in blocked_reasons)
    return _unique(errors)


def _blocked_reasons(
    *,
    session_goal: str,
    technical_release: dict[str, Any],
    product_release: dict[str, Any],
    officialization_evidence: list[str],
    release_note_sections: list[str],
    packaging_decision: dict[str, Any],
    review_status: str,
    acceptance_evidence: str,
) -> list[str]:
    reasons: list[str] = []
    if not session_goal:
        reasons.append("session_goal is required")
    if not acceptance_evidence:
        reasons.append("acceptance_evidence is required")

    for field in REQUIRED_TECHNICAL_RELEASE_FIELDS:
        if _is_empty(technical_release.get(field)):
            reasons.append(f"technical_release.{field} is required")
    for field in REQUIRED_PRODUCT_RELEASE_FIELDS:
        if _is_empty(product_release.get(field)):
            reasons.append(f"product_release.{field} is required")
    for field in REQUIRED_PACKAGING_DECISION_FIELDS:
        if _is_empty(packaging_decision.get(field)):
            reasons.append(f"packaging_decision.{field} is required")

    if technical_release.get("status") != "existing_public_technical_release":
        reasons.append("technical_release.status must be existing_public_technical_release")
    if product_release.get("status") != "official_packaging_candidate":
        reasons.append("product_release.status must be official_packaging_candidate")
    if product_release.get("version") != "0.1.0":
        reasons.append("product_release.version must be 0.1.0")

    evidence_set = set(officialization_evidence)
    for item in REQUIRED_OFFICIALIZATION_EVIDENCE:
        if item not in evidence_set:
            reasons.append(f"officialization_evidence must include {item}")

    section_set = set(release_note_sections)
    for section in REQUIRED_RELEASE_NOTE_SECTIONS:
        if section not in section_set:
            reasons.append(f"release_note_sections must include {section}")

    if packaging_decision.get("status") != "ready_for_human_release_note_review":
        reasons.append("packaging_decision.status must be ready_for_human_release_note_review")
    if packaging_decision.get("allowed_action") != "draft_official_0_1_0_release_notes":
        reasons.append("packaging_decision.allowed_action must be draft_official_0_1_0_release_notes")
    if packaging_decision.get("blocked_action") != "publish_without_human_review":
        reasons.append("packaging_decision.blocked_action must be publish_without_human_review")
    if review_status != "requires_human_review":
        reasons.append("review_status must be requires_human_review")

    return _unique(reasons)


def _release_notes_draft(
    *,
    technical_release: dict[str, Any],
    product_release: dict[str, Any],
    officialization_evidence: list[str],
) -> dict[str, Any]:
    return {
        "title": "Lumi Social Intelligence 0.1.0 officialization notes",
        "technical_release_exists": {
            "tag": technical_release.get("tag", ""),
            "status": technical_release.get("status", ""),
            "url": technical_release.get("url", ""),
        },
        "product_readiness_delta": {
            "version": product_release.get("version", ""),
            "status": product_release.get("status", ""),
            "positioning": product_release.get("positioning", ""),
        },
        "officialization_sprints": list(officialization_evidence),
        "safety_boundaries": [
            "review-only officialization artifacts",
            "no live Telegram sender or background service claimed",
            "no credentials, scheduler queues, chat metadata, or private runtime state",
            "no durable memory promotion without explicit approval",
        ],
        "not_included": [
            "live Lumi runtime",
            "Telegram bot wiring",
            "Hermes scheduler/config/memory mutation",
            "credential handling",
            "automatic product/company memory extraction",
        ],
        "human_review_next_step": "review notes before any publication or release edit",
    }


def _run_log_events(status: str) -> list[str]:
    events = [
        "received_official_packaging_input",
        "separated_technical_release_from_product_candidate",
        "checked_officialization_evidence",
        "checked_release_note_sections",
        "checked_publication_review_gate",
    ]
    events.append("awaiting_human_review_for_release_notes" if status != "fail_closed" else "blocked_before_publication")
    return events


def _shape_mapping(value: Any, required_fields: list[str]) -> dict[str, Any]:
    source = value if isinstance(value, dict) else {}
    return {field: source.get(field, "") for field in required_fields}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _text(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key, "") if isinstance(mapping, dict) else ""
    return value.strip() if isinstance(value, str) else ""


def _is_empty(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _reject_forbidden_fields(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_OFFICIAL_PACKAGING_FIELDS:
                raise ValueError(f"forbidden official packaging field: {key}")
            _reject_forbidden_fields(nested)
    elif isinstance(value, list):
        for item in value:
            _reject_forbidden_fields(item)


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
