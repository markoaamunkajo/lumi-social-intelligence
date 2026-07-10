"""Sprint 2 preview loop protocol for Lumi Social Intelligence.

The protocol is a review-only run artifact. It defines the exact step order for
in-chat preview behavior without creating a hidden runtime, Telegram wiring,
Hermes scheduler changes, canonical memory writes, or silent durable learning.
"""

from __future__ import annotations

from typing import Any

HUMAN_SHAPE_STATEMENT = "We are making the self-improvement loop something that is human-shaped."
RELEASE_LABEL = "Lumi Social Intelligence 0.1.0 preview with research harness"
STAGE = "sprint_2_preview_loop_protocol"

PREVIEW_LOOP_STEPS = [
    "observe",
    "reflect",
    "name_pattern",
    "suggest_adjustment",
    "ask_consent",
    "apply_small_change",
    "record_learning_only_if_approved",
]

ALLOWED_CONSENT_STATES = {"not_required_yet", "asked", "approved", "draft_only"}
FORBIDDEN_PROTOCOL_FIELDS = {
    "chat_id",
    "job_id",
    "scheduler_queue",
    "runtime_state",
    "delivery_channel",
    "credential",
    "api_key",
    "token",
}

REQUIRED_PAYLOAD_FIELDS = [
    "session_goal",
    "current_state",
    "proposed_adjustment",
    "consent_checkpoint",
    "approval_state",
    "learning_record_policy",
]


def build_preview_loop_protocol_run(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a Sprint 2 protocol run with zero side effects."""

    if not isinstance(payload, dict):
        raise ValueError("preview loop protocol input must be a mapping")
    _reject_forbidden_fields(payload)

    step_events = _build_step_events(payload.get("steps", []))
    blocked_reasons = _blocked_reasons(payload, step_events)
    status = "valid_protocol_run" if not blocked_reasons else "fail_closed"

    return {
        "schema": "lumi.preview_loop_protocol.run.v1",
        "release_label": RELEASE_LABEL,
        "stage": STAGE,
        "status": status,
        "human_shape_statement": HUMAN_SHAPE_STATEMENT,
        "session_goal": _text(payload, "session_goal"),
        "protocol": {
            "steps": list(PREVIEW_LOOP_STEPS),
            "transition_rule": "strict_order_no_skips",
            "consent_checkpoint": _text(payload, "consent_checkpoint") or "ask_consent",
            "approval_state": _text(payload, "approval_state"),
            "learning_record_policy": _text(payload, "learning_record_policy") or "record_only_if_approved",
            "state_labels": {
                "mode": "Internal / Confidential",
                "data_location": "This chat / Hermes context",
                "external_model_use": "Ask each time",
                "export_status": "Draft / Review needed",
            },
        },
        "step_events": step_events,
        "run_log": {
            "format": "ordered_preview_protocol_events_v1",
            "events": _run_log_events(status, step_events),
        },
        "safety": {
            "canonical_writes": 0,
            "runtime_actions": [],
            "external_model_use": "ask_each_time",
            "memory_promotion": "review_required_explicit_approval_only",
            "no_silent_memory_promotion": True,
            "no_hidden_runtime": True,
            "no_telegram_wiring": True,
            "no_credentials_touched": True,
            "no_hermes_scheduler_config_memory_mutation": True,
            "requires_human_review": True,
            "blocked_reasons": "; ".join(blocked_reasons),
            "forbidden_fields": sorted(FORBIDDEN_PROTOCOL_FIELDS),
        },
    }


def validate_preview_loop_protocol_run(run: dict[str, Any]) -> list[str]:
    """Return contract errors for a Sprint 2 preview protocol run."""

    errors: list[str] = []
    if not isinstance(run, dict):
        return ["run must be a mapping"]
    if run.get("schema") != "lumi.preview_loop_protocol.run.v1":
        errors.append("schema must be lumi.preview_loop_protocol.run.v1")
    if run.get("release_label") != RELEASE_LABEL:
        errors.append("release_label mismatch")
    if run.get("stage") != STAGE:
        errors.append("stage mismatch")
    if run.get("human_shape_statement") != HUMAN_SHAPE_STATEMENT:
        errors.append("missing human-shaped product statement")

    protocol = run.get("protocol")
    if not isinstance(protocol, dict):
        errors.append("protocol must be a mapping")
        protocol = {}
    if protocol.get("steps") != PREVIEW_LOOP_STEPS:
        errors.append("protocol steps must follow exact preview loop order")
    if protocol.get("transition_rule") != "strict_order_no_skips":
        errors.append("transition_rule must be strict_order_no_skips")
    if protocol.get("consent_checkpoint") != "ask_consent":
        errors.append("consent checkpoint must be ask_consent")
    if protocol.get("learning_record_policy") != "record_only_if_approved":
        errors.append("learning policy must be record_only_if_approved")

    step_events = run.get("step_events")
    if not isinstance(step_events, list):
        errors.append("step_events must be a list")
        step_events = []
    if [event.get("step") for event in step_events if isinstance(event, dict)] != PREVIEW_LOOP_STEPS:
        errors.append("protocol steps must follow exact preview loop order")
    errors.extend(_consent_errors(step_events))

    safety = run.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety must be a mapping")
    else:
        if safety.get("canonical_writes") != 0:
            errors.append("canonical writes are not allowed")
        if safety.get("runtime_actions") != []:
            errors.append("runtime actions are not allowed")
        if safety.get("no_silent_memory_promotion") is not True:
            errors.append("silent memory promotion is not allowed")
        if safety.get("no_telegram_wiring") is not True:
            errors.append("telegram wiring is not allowed in sprint 2")
        if safety.get("no_hermes_scheduler_config_memory_mutation") is not True:
            errors.append("Hermes scheduler/config/memory mutation is not allowed")

    status = run.get("status")
    if errors and status != "fail_closed":
        errors.append("invalid protocol runs must fail closed")
    if not errors and status != "valid_protocol_run":
        errors.append("valid protocol runs must be marked valid_protocol_run")
    return _dedupe(errors)


def _build_step_events(raw_steps: Any) -> list[dict[str, str]]:
    if not isinstance(raw_steps, list):
        return []
    events = []
    for raw in raw_steps:
        if not isinstance(raw, dict):
            continue
        events.append(
            {
                "step": _text(raw, "step"),
                "input": _text(raw, "input"),
                "output": _text(raw, "output"),
                "consent_state": _text(raw, "consent_state"),
            }
        )
    return events


def _blocked_reasons(payload: dict[str, Any], step_events: list[dict[str, str]]) -> list[str]:
    blocked = []
    for field in REQUIRED_PAYLOAD_FIELDS:
        if not _text(payload, field):
            blocked.append(f"missing {field}")
    if [event["step"] for event in step_events] != PREVIEW_LOOP_STEPS:
        blocked.append("protocol steps must follow exact preview loop order")
    for event in step_events:
        if not event["input"]:
            blocked.append(f"missing {event['step']}.input")
        if not event["output"]:
            blocked.append(f"missing {event['step']}.output")
        if event["consent_state"] not in ALLOWED_CONSENT_STATES:
            blocked.append(f"unsupported {event['step']}.consent_state")
    blocked.extend(_consent_errors(step_events))
    if _text(payload, "consent_checkpoint") and _text(payload, "consent_checkpoint") != "ask_consent":
        blocked.append("consent checkpoint must be ask_consent")
    if _text(payload, "learning_record_policy") and _text(payload, "learning_record_policy") != "record_only_if_approved":
        blocked.append("learning policy must be record_only_if_approved")
    return _dedupe(blocked)


def _consent_errors(step_events: list[dict[str, str]]) -> list[str]:
    by_step = {event.get("step"): event for event in step_events if isinstance(event, dict)}
    errors = []
    ask = by_step.get("ask_consent", {})
    apply = by_step.get("apply_small_change", {})
    record = by_step.get("record_learning_only_if_approved", {})
    if ask and ask.get("consent_state") not in {"asked", "approved"}:
        errors.append("ask_consent must ask or capture approval")
    apply_has_approval = bool(apply and apply.get("consent_state") == "approved")
    if apply and not apply_has_approval:
        errors.append("apply_small_change requires approved consent")
    if record and (record.get("consent_state") != "approved" or not apply_has_approval):
        errors.append("record_learning_only_if_approved requires approved consent")
    return errors


def _run_log_events(status: str, step_events: list[dict[str, str]]) -> list[str]:
    events = [f"{event['step']}_completed" for event in step_events if event.get("step") in PREVIEW_LOOP_STEPS]
    if status == "valid_protocol_run":
        events.append("awaiting_human_review")
    else:
        events.append("blocked_before_application")
    return events


def _reject_forbidden_fields(payload: dict[str, Any]) -> None:
    for field in sorted(FORBIDDEN_PROTOCOL_FIELDS):
        if field in payload:
            raise ValueError(f"forbidden preview protocol field: {field}")


def _text(source: dict[str, Any], field: str) -> str:
    value = source.get(field, "")
    return value.strip() if isinstance(value, str) else ""


def _dedupe(items: list[str]) -> list[str]:
    deduped = []
    for item in items:
        if item not in deduped:
            deduped.append(item)
    return deduped
