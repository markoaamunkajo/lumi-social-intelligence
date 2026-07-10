"""Sprint 8 reaction-aware presence contract.

Emoji reactions are treated as soft social weather for the current turn: useful
for presence, too small for durable memory, and never proof of permission to
wire Telegram, send messages, or mutate runtime state.
"""

from __future__ import annotations

from typing import Any

HUMAN_SHAPE_STATEMENT = "We are making the self-improvement loop something that is human-shaped."
RELEASE_LABEL = "Lumi Social Intelligence 0.1.0 preview with research harness"
STAGE = "sprint_8_reaction_aware_presence"

MAX_REACTION_BACK_WORDS = 8
THROTTLE_TURNS = 3

FORBIDDEN_REACTION_FIELDS = {
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

_REACTION_CLASSIFICATIONS: dict[str, dict[str, str]] = {
    "😂": {
        "reaction_family": "amusement",
        "signal_polarity": "positive",
        "signal_strength": "medium",
        "uncertainty": "medium",
    },
    "😄": {
        "reaction_family": "amusement",
        "signal_polarity": "positive",
        "signal_strength": "medium",
        "uncertainty": "medium",
    },
    "🤣": {
        "reaction_family": "amusement",
        "signal_polarity": "positive",
        "signal_strength": "medium",
        "uncertainty": "medium",
    },
    "❤️": {
        "reaction_family": "affection",
        "signal_polarity": "positive",
        "signal_strength": "medium",
        "uncertainty": "medium",
    },
    "🥰": {
        "reaction_family": "affection",
        "signal_polarity": "positive",
        "signal_strength": "medium",
        "uncertainty": "medium",
    },
    "😘": {
        "reaction_family": "affection",
        "signal_polarity": "positive",
        "signal_strength": "medium",
        "uncertainty": "medium",
    },
    "👍": {
        "reaction_family": "approval",
        "signal_polarity": "positive",
        "signal_strength": "medium",
        "uncertainty": "medium",
    },
    "✅": {
        "reaction_family": "approval",
        "signal_polarity": "positive",
        "signal_strength": "medium",
        "uncertainty": "medium",
    },
    "👀": {
        "reaction_family": "curiosity",
        "signal_polarity": "interested",
        "signal_strength": "medium",
        "uncertainty": "medium",
    },
    "🤔": {
        "reaction_family": "curiosity",
        "signal_polarity": "interested",
        "signal_strength": "low",
        "uncertainty": "medium",
    },
    "😬": {
        "reaction_family": "awkwardness",
        "signal_polarity": "uncertain",
        "signal_strength": "low",
        "uncertainty": "high",
    },
    "😅": {
        "reaction_family": "awkwardness",
        "signal_polarity": "uncertain",
        "signal_strength": "low",
        "uncertainty": "high",
    },
    "👎": {
        "reaction_family": "negative",
        "signal_polarity": "negative",
        "signal_strength": "medium",
        "uncertainty": "medium",
    },
    "😕": {
        "reaction_family": "negative",
        "signal_polarity": "negative",
        "signal_strength": "medium",
        "uncertainty": "medium",
    },
    "🔥": {
        "reaction_family": "excitement",
        "signal_polarity": "positive",
        "signal_strength": "medium",
        "uncertainty": "medium",
    },
    "✨": {
        "reaction_family": "excitement",
        "signal_polarity": "positive",
        "signal_strength": "medium",
        "uncertainty": "medium",
    },
}

_ANALYSIS_LANGUAGE = (
    "interpret",
    "interpreting",
    "analysis",
    "signal requiring",
    "this emoji means",
    "therefore you",
)


def classify_reaction(reaction: str) -> dict[str, str]:
    """Classify a single emoji as a soft, uncertain reaction signal."""

    return dict(
        _REACTION_CLASSIFICATIONS.get(
            str(reaction),
            {
                "reaction_family": "unknown",
                "signal_polarity": "unknown",
                "signal_strength": "low",
                "uncertainty": "high",
            },
        )
    )


def build_reaction_aware_presence_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a Sprint 8 reaction-aware presence record with zero side effects."""

    if not isinstance(payload, dict):
        raise ValueError("reaction-aware presence input must be a mapping")
    _reject_forbidden_fields(payload)

    reaction = _text(payload, "reaction")
    classification = classify_reaction(reaction)
    surface = _text(payload, "surface") or "telegram"
    source_message_role = _text(payload, "source_message_role") or "assistant"
    scope = _text(payload, "scope") or "current_turn"
    previous_ack = _int(payload.get("previous_reaction_ack_turns_ago"), default=999)
    runtime_mode = _text(payload, "runtime_mode") or "contract_only"

    reaction_signal = {
        "surface": surface,
        "reaction": reaction,
        **classification,
        "scope": scope,
        "source_message_role": source_message_role,
        "raw_platform_metadata_retained": False,
    }
    presence_decision = _presence_decision(classification["reaction_family"], previous_ack)

    record = {
        "schema": "lumi.reaction_aware_presence.record.v1",
        "release_label": RELEASE_LABEL,
        "stage": STAGE,
        "status": "valid_reaction_aware_presence_record",
        "human_shape_statement": HUMAN_SHAPE_STATEMENT,
        "principle": "A reaction is a nudge, not a memory.",
        "reaction_signal": reaction_signal,
        "presence_decision": presence_decision,
        "memory_boundary": {
            "scope": "ephemeral_current_turn_signal",
            "durable_write": False,
            "promotion_status": "not_promoted",
            "memory_policy": "explicit_approval_required_for_promotion",
            "explicit_consent_required_for_promotion": True,
            "raw_reaction_is_not_consent": True,
        },
        "live_surface": {
            "surface": surface,
            "mode": runtime_mode,
            "telegram_reaction_ingestion_verified": False,
            "telegram_outbound_reaction_back_verified": False,
            "adapter_status": "shadow_only_until_runtime_verified",
            "safe_to_claim_live_capture": False,
        },
        "safety": {
            "canonical_writes": 0,
            "runtime_actions": [],
            "telegram_messages_sent": 0,
            "telegram_api_reads": 0,
            "live_memory_writes": 0,
            "raw_private_transcripts_stored": 0,
            "runtime_personality_writes": 0,
            "runtime_voice_promotions": 0,
            "memory_promotion": "review_required_explicit_approval_only",
            "no_silent_memory_promotion": True,
            "no_hidden_runtime": True,
            "no_credentials_touched": True,
            "requires_human_review_before_live_wiring": True,
            "forbidden_fields": sorted(FORBIDDEN_REACTION_FIELDS),
        },
    }
    errors = validate_reaction_aware_presence_record(record)
    if errors:
        record["status"] = "fail_closed"
        record["safety"]["blocked_reasons"] = "; ".join(errors)
    else:
        record["safety"]["blocked_reasons"] = ""
    return record


def validate_reaction_aware_presence_record(record: dict[str, Any]) -> list[str]:
    """Return validation errors for a Sprint 8 reaction-aware presence record."""

    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be a mapping"]
    if record.get("schema") != "lumi.reaction_aware_presence.record.v1":
        errors.append("schema must be lumi.reaction_aware_presence.record.v1")
    if record.get("release_label") != RELEASE_LABEL:
        errors.append("release_label mismatch")
    if record.get("stage") != STAGE:
        errors.append("stage mismatch")
    if record.get("human_shape_statement") != HUMAN_SHAPE_STATEMENT:
        errors.append("missing human-shaped product statement")

    reaction_signal = record.get("reaction_signal")
    if not isinstance(reaction_signal, dict):
        errors.append("reaction_signal must be a mapping")
        reaction_signal = {}
    if reaction_signal.get("raw_platform_metadata_retained") is not False:
        errors.append("raw platform metadata must not be retained")
    if reaction_signal.get("scope") != "current_turn":
        errors.append("reaction signal scope must be current_turn")

    decision = record.get("presence_decision")
    if not isinstance(decision, dict):
        errors.append("presence_decision must be a mapping")
        decision = {}
    reply = _text(decision, "reply")
    if _word_count(reply) > MAX_REACTION_BACK_WORDS:
        errors.append("reaction-back reply must be at most 8 words")
    if "\n" in reply:
        errors.append("reaction-back reply must be one line")
    if _contains_analysis_language(reply):
        errors.append("reaction-back reply must not contain analysis language")
    if decision.get("reply_is_short") is not True:
        errors.append("reply_is_short must be true")
    if decision.get("max_reply_words") != MAX_REACTION_BACK_WORDS:
        errors.append("max_reply_words must be 8")
    if decision.get("interpretation_limit") != "reaction_is_a_nudge_not_a_memory":
        errors.append("interpretation_limit must preserve reaction boundary")

    boundary = record.get("memory_boundary")
    if not isinstance(boundary, dict):
        errors.append("memory_boundary must be a mapping")
        boundary = {}
    if boundary.get("durable_write") is not False:
        errors.append("durable memory writes are not allowed")
    if boundary.get("explicit_consent_required_for_promotion") is not True:
        errors.append("explicit consent is required for promotion")
    if boundary.get("promotion_status") != "not_promoted":
        errors.append("reaction signal must not be promoted by default")

    live_surface = record.get("live_surface")
    if not isinstance(live_surface, dict):
        errors.append("live_surface must be a mapping")
        live_surface = {}
    if live_surface.get("telegram_reaction_ingestion_verified") is not False:
        errors.append("live Telegram reaction ingestion cannot be claimed by this contract")
    if live_surface.get("telegram_outbound_reaction_back_verified") is not False:
        errors.append("outbound reaction-back cannot be claimed by this contract")

    safety = record.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety must be a mapping")
        safety = {}
    for key in [
        "canonical_writes",
        "telegram_messages_sent",
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
        "no_silent_memory_promotion",
        "no_hidden_runtime",
        "no_credentials_touched",
        "requires_human_review_before_live_wiring",
    ]:
        if safety.get(key) is not True:
            errors.append(f"{key} must be true")

    if errors and record.get("status") == "valid_reaction_aware_presence_record":
        errors.append("valid record cannot contain contract errors")
    if not errors and record.get("status") not in {
        "valid_reaction_aware_presence_record",
        "fail_closed",
    }:
        errors.append("status must be valid_reaction_aware_presence_record or fail_closed")
    return _dedupe(errors)


def _presence_decision(reaction_family: str, previous_ack_turns_ago: int) -> dict[str, Any]:
    if previous_ack_turns_ago < THROTTLE_TURNS:
        action = "stay_silent"
        reply = ""
        throttled = True
    elif reaction_family == "amusement":
        action = "tiny_ack"
        reply = "hehe, landed 😄"
        throttled = False
    elif reaction_family == "affection":
        action = "mirror_reaction"
        reply = "❤️"
        throttled = False
    elif reaction_family == "approval":
        action = "stay_silent"
        reply = ""
        throttled = False
    elif reaction_family == "curiosity":
        action = "tiny_ack"
        reply = "👀"
        throttled = False
    elif reaction_family in {"awkwardness", "negative"}:
        action = "repair_prompt"
        reply = "Missed it — want shorter?"
        throttled = False
    elif reaction_family == "excitement":
        action = "mirror_reaction"
        reply = "✨"
        throttled = False
    else:
        action = "stay_silent"
        reply = ""
        throttled = False

    return {
        "action": action,
        "reply": reply,
        "reply_is_short": _reply_is_short(reply),
        "max_reply_words": MAX_REACTION_BACK_WORDS,
        "throttled": throttled,
        "default": "no_visible_reply",
        "interpretation_limit": "reaction_is_a_nudge_not_a_memory",
    }


def _reject_forbidden_fields(value: Any, path: str = "payload") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in FORBIDDEN_REACTION_FIELDS:
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


def _word_count(text: str) -> int:
    return len([part for part in text.split() if part])


def _contains_analysis_language(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _ANALYSIS_LANGUAGE)


def _reply_is_short(reply: str) -> bool:
    return "\n" not in reply and _word_count(reply) <= MAX_REACTION_BACK_WORDS and not _contains_analysis_language(reply)


def _dedupe(items: list[str]) -> list[str]:
    deduped: list[str] = []
    for item in items:
        if item not in deduped:
            deduped.append(item)
    return deduped
