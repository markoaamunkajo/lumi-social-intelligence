"""Sprint 7 live preview run record for this chat.

This is a review-only artifact for exercising the Lumi Social Intelligence
preview loop in conversation. It does not start a service, wire Telegram, write
memory, mutate Hermes state, or perform runtime actions.
"""

from __future__ import annotations

from typing import Any

HUMAN_SHAPE_STATEMENT = "We are making the self-improvement loop something that is human-shaped."
RELEASE_LABEL = "Lumi Social Intelligence 0.1.0 preview with research harness"
STAGE = "sprint_7_live_preview_run"

PREVIEW_RUN_STEPS = [
    "observe",
    "reflect",
    "name_pattern",
    "suggest_adjustment",
    "ask_consent",
    "apply_small_change",
    "record_learning_only_if_approved",
]

REQUIRED_PAYLOAD_FIELDS = [
    "session_goal",
    "conversation_context",
    "observed_signal",
    "reflection",
    "named_pattern",
    "suggested_adjustment",
    "consent_checkpoint",
    "approval_state",
    "applied_small_change",
    "learning_record_policy",
    "human_review_summary",
]

FORBIDDEN_LIVE_PREVIEW_FIELDS = {
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


def build_live_preview_run_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a Sprint 7 review-only live preview run record."""

    if not isinstance(payload, dict):
        raise ValueError("live preview input must be a mapping")
    _reject_forbidden_fields(payload)

    step_events = _build_step_events(payload)
    blocked_reasons = _blocked_reasons(payload, step_events)
    status = "valid_live_preview_run_record" if not blocked_reasons else "fail_closed"

    approval_state = _text(payload, "approval_state")
    learning_policy = _text(payload, "learning_record_policy") or "record_only_if_approved"
    runtime_actions = payload.get("runtime_actions", [])

    return {
        "schema": "lumi.live_preview_run.record.v1",
        "release_label": RELEASE_LABEL,
        "stage": STAGE,
        "status": status,
        "human_shape_statement": HUMAN_SHAPE_STATEMENT,
        "preview_run": {
            "surface": "this_chat_review_only",
            "mode": "in_chat_preview_record",
            "conversation_context": _text(payload, "conversation_context"),
            "session_goal": _text(payload, "session_goal"),
            "no_background_service_started": True,
        },
        "step_events": step_events,
        "review_card": {
            "observed_signal": _text(payload, "observed_signal"),
            "reflection": _text(payload, "reflection"),
            "named_pattern": _text(payload, "named_pattern"),
            "suggested_adjustment": _text(payload, "suggested_adjustment"),
            "consent_checkpoint": _text(payload, "consent_checkpoint") or "ask_consent",
            "approval_state": approval_state,
            "apply_small_change_status": "drafted_review_card_only",
            "applied_small_change": _text(payload, "applied_small_change"),
            "human_review_summary": _text(payload, "human_review_summary"),
            "requires_human_review": True,
            "durable_learning_allowed": False,
        },
        "run_log": {
            "format": "live_preview_run_events_v1",
            "events": _run_log_events(status),
        },
        "safety": {
            "canonical_writes": 0,
            "runtime_actions": runtime_actions if isinstance(runtime_actions, list) else runtime_actions,
            "external_model_use": "ask_each_time",
            "memory_promotion": "review_required_explicit_approval_only",
            "learning_record_policy": learning_policy,
            "no_silent_memory_promotion": True,
            "no_thinking_space_extraction": True,
            "no_hidden_runtime": True,
            "no_telegram_wiring": True,
            "no_credentials_touched": True,
            "no_hermes_scheduler_config_memory_mutation": True,
            "requires_human_review": True,
            "blocked_reasons": "; ".join(blocked_reasons),
            "forbidden_fields": sorted(FORBIDDEN_LIVE_PREVIEW_FIELDS),
        },
    }


def validate_live_preview_run_record(record: dict[str, Any]) -> list[str]:
    """Return validation errors for a Sprint 7 live preview record."""

    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be a mapping"]
    if record.get("schema") != "lumi.live_preview_run.record.v1":
        errors.append("schema must be lumi.live_preview_run.record.v1")
    if record.get("release_label") != RELEASE_LABEL:
        errors.append("release_label mismatch")
    if record.get("stage") != STAGE:
        errors.append("stage mismatch")
    if record.get("human_shape_statement") != HUMAN_SHAPE_STATEMENT:
        errors.append("missing human-shaped product statement")
    if record.get("status") not in {"valid_live_preview_run_record", "fail_closed"}:
        errors.append("status must be valid_live_preview_run_record or fail_closed")

    preview_run = record.get("preview_run")
    if not isinstance(preview_run, dict):
        errors.append("preview_run must be a mapping")
        preview_run = {}
    if preview_run.get("surface") != "this_chat_review_only":
        errors.append("preview_run surface must be this_chat_review_only")
    if preview_run.get("no_background_service_started") is not True:
        errors.append("no_background_service_started must be true")

    step_events = record.get("step_events")
    if not isinstance(step_events, list):
        errors.append("step_events must be a list")
        step_events = []
    if [event.get("step") for event in step_events if isinstance(event, dict)] != PREVIEW_RUN_STEPS:
        errors.append("step_events must follow exact live preview order")

    card = record.get("review_card")
    if not isinstance(card, dict):
        errors.append("review_card must be a mapping")
        card = {}
    if card.get("requires_human_review") is not True:
        errors.append("review_card must require human review")
    if card.get("durable_learning_allowed") is not False:
        errors.append("durable_learning_allowed must stay false")
    if card.get("consent_checkpoint") != "ask_consent":
        errors.append("consent_checkpoint must be ask_consent")
    if card.get("apply_small_change_status") != "drafted_review_card_only":
        errors.append("apply_small_change_status must be drafted_review_card_only")

    safety = record.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety must be a mapping")
        safety = {}
    if safety.get("canonical_writes") != 0:
        errors.append("canonical_writes must be 0")
    if safety.get("runtime_actions") != []:
        errors.append("runtime_actions must stay empty")
    if safety.get("learning_record_policy") != "record_only_if_approved":
        errors.append("learning_record_policy must be record_only_if_approved")
    for key in [
        "no_silent_memory_promotion",
        "no_thinking_space_extraction",
        "no_hidden_runtime",
        "no_telegram_wiring",
        "no_credentials_touched",
        "no_hermes_scheduler_config_memory_mutation",
        "requires_human_review",
    ]:
        if safety.get(key) is not True:
            errors.append(f"{key} must be true")

    if record.get("status") == "valid_live_preview_run_record" and errors:
        errors.append("valid record cannot contain contract errors")
    return errors


def _build_step_events(payload: dict[str, Any]) -> list[dict[str, str]]:
    requested_steps = payload.get("steps", PREVIEW_RUN_STEPS)
    if not isinstance(requested_steps, list):
        requested_steps = []
    details = {
        "observe": _text(payload, "observed_signal"),
        "reflect": _text(payload, "reflection"),
        "name_pattern": _text(payload, "named_pattern"),
        "suggest_adjustment": _text(payload, "suggested_adjustment"),
        "ask_consent": _text(payload, "consent_checkpoint") or "ask_consent",
        "apply_small_change": _text(payload, "applied_small_change"),
        "record_learning_only_if_approved": _text(payload, "learning_record_policy") or "record_only_if_approved",
    }
    return [
        {
            "index": str(index),
            "step": str(step),
            "detail": details.get(str(step), ""),
        }
        for index, step in enumerate(requested_steps, start=1)
    ]


def _blocked_reasons(payload: dict[str, Any], step_events: list[dict[str, str]]) -> list[str]:
    reasons: list[str] = []
    missing = [field for field in REQUIRED_PAYLOAD_FIELDS if not _text(payload, field)]
    if missing:
        reasons.append("missing required fields: " + ", ".join(missing))
    if [event.get("step") for event in step_events] != PREVIEW_RUN_STEPS:
        reasons.append("step_events must follow exact live preview order")
    if _text(payload, "consent_checkpoint") != "ask_consent":
        reasons.append("consent_checkpoint must be ask_consent")
    if _text(payload, "learning_record_policy") != "record_only_if_approved":
        reasons.append("learning_record_policy must be record_only_if_approved")
    runtime_actions = payload.get("runtime_actions", [])
    if runtime_actions != []:
        reasons.append("runtime_actions must stay empty")
    if payload.get("canonical_writes", 0) != 0:
        reasons.append("canonical_writes must be 0")
    return reasons


def _run_log_events(status: str) -> list[str]:
    events = [
        "observed_chat_signal",
        "drafted_reflection",
        "named_pattern",
        "suggested_small_adjustment",
        "consent_checkpoint_required",
        "drafted_review_card_only",
    ]
    if status == "valid_live_preview_run_record":
        events.append("awaiting_human_review_before_learning")
    else:
        events.append("blocked_before_learning_or_runtime_action")
    return events


def _text(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key, "")
    return value.strip() if isinstance(value, str) else ""


def _reject_forbidden_fields(value: Any, path: str = "payload") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_LIVE_PREVIEW_FIELDS:
                raise ValueError(f"forbidden private/runtime field at {path}.{key}")
            _reject_forbidden_fields(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_forbidden_fields(nested, f"{path}[{index}]")
