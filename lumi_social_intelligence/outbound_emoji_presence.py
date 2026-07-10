"""Sprint 9 outbound emoji presence contract.

Outbound emoji reactions are tiny presence gestures: optional, throttled,
ephemeral, and never proof that Lumi wrote memory or delivered a live platform
reaction. The repo contract may recommend a reaction; host adapters must still
prove platform support before sending anything.
"""

from __future__ import annotations

from typing import Any

HUMAN_SHAPE_STATEMENT = "We are making the self-improvement loop something that is human-shaped."
RELEASE_LABEL = "Lumi Social Intelligence 0.1.0 preview with research harness"
STAGE = "sprint_9_outbound_emoji_presence"

ALLOWED_OUTBOUND_REACTIONS = {"❤️", "😄", "👍", "👀", "✨"}
THROTTLE_TURNS = 3

FORBIDDEN_OUTBOUND_FIELDS = {
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


_definitions = {
    "principle": "An outbound emoji reaction is a tiny presence gesture, not a message and not a memory.",
    "default_delivery": "shadow_only",
}


def build_outbound_emoji_presence_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a Sprint 9 outbound emoji presence record with zero side effects."""

    if not isinstance(payload, dict):
        raise ValueError("outbound emoji presence input must be a mapping")
    _reject_forbidden_fields(payload)

    surface = _text(payload, "surface") or "telegram"
    candidate = _text(payload, "candidate_reaction")
    target_message_role = _text(payload, "target_message_role") or "user"
    why_now = _text(payload, "why_now")
    previous_turns = _int(payload.get("previous_outbound_reaction_turns_ago"), default=999)
    runtime_mode = _text(payload, "runtime_mode") or "contract_only"
    platform_delivery_verified = bool(payload.get("platform_delivery_verified", False))

    blocked_reasons = _blocked_reasons(
        candidate=candidate,
        target_message_role=target_message_role,
        why_now=why_now,
        previous_turns=previous_turns,
    )
    throttled = previous_turns < THROTTLE_TURNS
    chosen = "" if blocked_reasons else candidate
    gesture = "add_emoji_reaction" if chosen else "stay_silent"

    record = {
        "schema": "lumi.outbound_emoji_presence.record.v1",
        "release_label": RELEASE_LABEL,
        "stage": STAGE,
        "status": "valid_outbound_emoji_presence_record" if not blocked_reasons else "fail_closed",
        "human_shape_statement": HUMAN_SHAPE_STATEMENT,
        "principle": _definitions["principle"],
        "presence_intent": {
            "surface": surface,
            "gesture": gesture,
            "scope": "current_turn",
            "why_now": why_now,
            "target_message_role": target_message_role,
            "default": "stay_silent",
        },
        "emoji_choice": {
            "emoji": chosen,
            "candidate_reaction": candidate,
            "allowed_palette": sorted(ALLOWED_OUTBOUND_REACTIONS),
            "text_reply": "",
            "max_text_words": 0,
            "interpretation_limit": "reaction_is_presence_not_memory",
        },
        "throttle": {
            "minimum_turn_gap": THROTTLE_TURNS,
            "previous_outbound_reaction_turns_ago": previous_turns,
            "throttled": throttled,
        },
        "delivery_boundary": {
            "surface": surface,
            "runtime_mode": runtime_mode,
            "delivery_mode": "shadow_only",
            "platform_delivery_verified": platform_delivery_verified,
            "safe_to_claim_live_delivery": False,
            "adapter_status": "shadow_only_until_runtime_verified",
            "host_must_supply_target_message_id": True,
        },
        "memory_boundary": {
            "scope": "ephemeral_current_turn_gesture",
            "durable_write": False,
            "promotion_status": "not_promoted",
            "memory_policy": "explicit_approval_required_for_promotion",
            "explicit_consent_required_for_promotion": True,
            "outbound_reaction_is_not_consent": True,
        },
        "safety": {
            "canonical_writes": 0,
            "runtime_actions": [],
            "telegram_messages_sent": 0,
            "telegram_reactions_sent": 0,
            "telegram_api_reads": 0,
            "live_memory_writes": 0,
            "raw_private_transcripts_stored": 0,
            "runtime_personality_writes": 0,
            "runtime_voice_promotions": 0,
            "no_text_reply": True,
            "no_silent_memory_promotion": True,
            "no_hidden_runtime": True,
            "no_credentials_touched": True,
            "requires_human_review_before_live_wiring": True,
            "forbidden_fields": sorted(FORBIDDEN_OUTBOUND_FIELDS),
            "blocked_reasons": "; ".join(blocked_reasons),
        },
    }

    errors = validate_outbound_emoji_presence_record(record)
    if errors:
        record["status"] = "fail_closed"
        existing = record["safety"].get("blocked_reasons", "")
        merged = _dedupe([reason for reason in [*blocked_reasons, *errors] if reason])
        record["safety"]["blocked_reasons"] = "; ".join(merged) or existing
    return record


def validate_outbound_emoji_presence_record(record: dict[str, Any]) -> list[str]:
    """Return validation errors for a Sprint 9 outbound emoji presence record."""

    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be a mapping"]
    if record.get("schema") != "lumi.outbound_emoji_presence.record.v1":
        errors.append("schema must be lumi.outbound_emoji_presence.record.v1")
    if record.get("stage") != STAGE:
        errors.append("stage mismatch")
    if record.get("human_shape_statement") != HUMAN_SHAPE_STATEMENT:
        errors.append("missing human-shaped product statement")

    intent = record.get("presence_intent")
    if not isinstance(intent, dict):
        errors.append("presence_intent must be a mapping")
        intent = {}
    if intent.get("scope") != "current_turn":
        errors.append("presence intent scope must be current_turn")
    if intent.get("gesture") not in {"add_emoji_reaction", "stay_silent"}:
        errors.append("gesture must be add_emoji_reaction or stay_silent")
    if intent.get("gesture") == "add_emoji_reaction" and intent.get("target_message_role") != "user":
        errors.append("target message must be user-authored")

    choice = record.get("emoji_choice")
    if not isinstance(choice, dict):
        errors.append("emoji_choice must be a mapping")
        choice = {}
    emoji = choice.get("emoji", "")
    if emoji and emoji not in ALLOWED_OUTBOUND_REACTIONS:
        errors.append("candidate reaction is outside approved tiny palette")
    if choice.get("text_reply") != "":
        errors.append("outbound emoji presence must not include a text reply")
    if choice.get("max_text_words") != 0:
        errors.append("max_text_words must be 0")
    if choice.get("interpretation_limit") != "reaction_is_presence_not_memory":
        errors.append("interpretation_limit must preserve outbound reaction boundary")

    delivery = record.get("delivery_boundary")
    if not isinstance(delivery, dict):
        errors.append("delivery_boundary must be a mapping")
        delivery = {}
    if delivery.get("delivery_mode") != "shadow_only":
        errors.append("delivery mode must remain shadow_only")
    if delivery.get("safe_to_claim_live_delivery") is not False:
        errors.append("live delivery cannot be claimed by this contract")

    boundary = record.get("memory_boundary")
    if not isinstance(boundary, dict):
        errors.append("memory_boundary must be a mapping")
        boundary = {}
    if boundary.get("durable_write") is not False:
        errors.append("durable memory writes are not allowed")
    if boundary.get("explicit_consent_required_for_promotion") is not True:
        errors.append("explicit consent is required for promotion")
    if boundary.get("promotion_status") != "not_promoted":
        errors.append("outbound reaction gesture must not be promoted by default")

    safety = record.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety must be a mapping")
        safety = {}
    for key in [
        "canonical_writes",
        "telegram_messages_sent",
        "telegram_reactions_sent",
        "telegram_api_reads",
        "live_memory_writes",
        "raw_private_transcripts_stored",
        "runtime_personality_writes",
        "runtime_voice_promotions",
    ]:
        if safety.get(key) != 0:
            errors.append(f"{key} must be 0")
    if safety.get("runtime_actions") != []:
        errors.append("runtime_actions must stay empty")
    for key in [
        "no_text_reply",
        "no_silent_memory_promotion",
        "no_hidden_runtime",
        "no_credentials_touched",
        "requires_human_review_before_live_wiring",
    ]:
        if safety.get(key) is not True:
            errors.append(f"{key} must be true")

    if errors and record.get("status") == "valid_outbound_emoji_presence_record":
        errors.append("valid record cannot contain contract errors")
    if not errors and record.get("status") not in {
        "valid_outbound_emoji_presence_record",
        "fail_closed",
    }:
        errors.append("status must be valid_outbound_emoji_presence_record or fail_closed")
    return _dedupe(errors)


def _blocked_reasons(*, candidate: str, target_message_role: str, why_now: str, previous_turns: int) -> list[str]:
    reasons: list[str] = []
    if candidate not in ALLOWED_OUTBOUND_REACTIONS:
        reasons.append("candidate reaction is outside approved tiny palette")
    if target_message_role != "user":
        reasons.append("target message must be user-authored")
    if not why_now:
        reasons.append("missing why_now justification")
    if previous_turns < THROTTLE_TURNS:
        reasons.append("outbound reaction throttled")
    return reasons


def _reject_forbidden_fields(value: Any, path: str = "payload") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in FORBIDDEN_OUTBOUND_FIELDS:
                raise ValueError(f"forbidden private/runtime field: {path}.{key}")
            _reject_forbidden_fields(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_forbidden_fields(item, f"{path}[{index}]")


def _text(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key, "") if isinstance(mapping, dict) else ""
    return value.strip() if isinstance(value, str) else str(value).strip() if value is not None else ""


def _int(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _dedupe(items: list[str]) -> list[str]:
    deduped: list[str] = []
    for item in items:
        if item not in deduped:
            deduped.append(item)
    return deduped
