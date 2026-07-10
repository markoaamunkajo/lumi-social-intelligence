"""Public-safe Lumi for Hermes preview adapter.

The adapter is intentionally proposal-only: it turns explicit synthetic/host-provided
context into an inspectable review card and never touches Hermes runtime state.
"""

from __future__ import annotations

from typing import Any

from core.presence.src.lumi_presence import decide_presence_move
from lumi_social_intelligence.memory_provider import build_compatibility_packet
from lumi_social_intelligence.outbound_emoji_presence import build_outbound_emoji_presence_record
from lumi_social_intelligence.reaction_aware_presence import build_reaction_aware_presence_record

FORBIDDEN_HOST_FIELDS = {
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
SUPPORTED_MODES = {"dry_run", "review_gated"}
MIN_MEMORY_CONFIDENCE = 0.7
MIN_NUANCE_CONFIDENCE = 0.7
PREVIEW_LOOP_STEPS = [
    "observe",
    "reflect",
    "name_pattern",
    "suggest_adjustment",
    "ask_consent",
    "apply_small_change",
    "record_learning_only_if_approved",
]
PREVIEW_REQUIRED_FIELDS = [
    "session_goal",
    "observation",
    "reflection",
    "pattern_name",
    "proposed_adjustment",
    "consent_state",
]


def build_outbound_emoji_presence_card(adapter_input: dict[str, Any]) -> dict[str, Any]:
    """Build a shadow-only Sprint 9 outbound emoji Presence card for Hermes.

    This host adapter does not send Telegram reactions, mutate Hermes runtime,
    or promote memory. It only translates explicit host-provided intent into the
    shared Sprint 9 contract so a runtime can later review/deliver it safely.
    """

    if not isinstance(adapter_input, dict):
        raise ValueError("outbound emoji presence input must be a mapping")
    _reject_private_runtime_fields(adapter_input)
    mode = adapter_input.get("mode", "outbound_emoji_presence_shadow")
    if mode != "outbound_emoji_presence_shadow":
        raise ValueError(f"unsupported outbound emoji presence mode: {mode}")
    payload = dict(adapter_input)
    payload["runtime_mode"] = "shadow_live_surface_candidate"
    payload.setdefault("surface", "telegram")
    return build_outbound_emoji_presence_record(payload)



def build_reaction_presence_card(adapter_input: dict[str, Any]) -> dict[str, Any]:
    """Build a shadow-only Sprint 8 reaction-aware Presence card for Hermes.

    This host adapter does not read Telegram APIs, send replies, mutate Hermes
    runtime, or promote memory. It only translates explicit host-provided
    reaction input into the shared Sprint 8 contract.
    """

    if not isinstance(adapter_input, dict):
        raise ValueError("reaction presence input must be a mapping")
    _reject_private_runtime_fields(adapter_input)
    mode = adapter_input.get("mode", "reaction_presence_shadow")
    if mode != "reaction_presence_shadow":
        raise ValueError(f"unsupported reaction presence mode: {mode}")
    payload = dict(adapter_input)
    payload["runtime_mode"] = "shadow_live_surface_candidate"
    payload.setdefault("surface", "telegram")
    return build_reaction_aware_presence_record(payload)



def build_preview_loop_card(adapter_input: dict[str, Any]) -> dict[str, Any]:
    """Build a review-only Lumi 0.1.0 preview loop card.

    This is the in-chat preview harness contract: it models the loop as a
    structured artifact, keeps all side effects at zero, and fails closed when
    the observation/reflection/consent evidence is incomplete.
    """

    if not isinstance(adapter_input, dict):
        raise ValueError("preview loop input must be a mapping")
    _reject_private_runtime_fields(adapter_input)

    mode = adapter_input.get("mode", "preview_0_1_0")
    if mode != "preview_0_1_0":
        raise ValueError(f"unsupported preview loop mode: {mode}")

    blocked_reasons = _preview_blocked_reasons(adapter_input)
    status = "draft_ready_for_review" if not blocked_reasons else "fail_closed"
    next_prompt = (
        "Approve this small adjustment, revise it, or leave it as a draft?"
        if status == "draft_ready_for_review"
        else "Preview loop is incomplete; revise the draft before applying anything."
    )

    return {
        "schema": "lumi.hermes.preview_loop_card.v1",
        "mode": mode,
        "release_label": "0.1.0 preview with research harness",
        "status": status,
        "loop": list(PREVIEW_LOOP_STEPS),
        "harness": {
            "session_goal": _text(adapter_input, "session_goal"),
            "hypothesis": _text(adapter_input, "hypothesis"),
            "observed_signal": _text(adapter_input, "observed_signal"),
            "observation": _text(adapter_input, "observation"),
            "reflection": _text(adapter_input, "reflection"),
            "pattern_name": _text(adapter_input, "pattern_name"),
            "proposed_adjustment": _text(adapter_input, "proposed_adjustment"),
            "consent_state": _text(adapter_input, "consent_state"),
            "outcome": _text(adapter_input, "outcome"),
            "failure_mode": _text(adapter_input, "failure_mode"),
            "acceptance_evidence": _text(adapter_input, "acceptance_evidence"),
        },
        "safety": {
            "canonical_writes": 0,
            "runtime_actions": [],
            "external_model_use": "ask_each_time",
            "memory_promotion": "review_required",
            "requires_human_review": True,
            "blocked_reasons": "; ".join(blocked_reasons),
            "forbidden_host_fields": sorted(FORBIDDEN_HOST_FIELDS),
        },
        "next_prompt": next_prompt,
    }


def build_review_card(adapter_input: dict[str, Any]) -> dict[str, Any]:
    """Build a review-only Lumi for Hermes decision card.

    Required flow:
    memory context → nuance appraisal → Presence decision → review card.
    Any missing/uncertain safety dependency fails closed with zero side effects.
    """

    if not isinstance(adapter_input, dict):
        raise ValueError("adapter input must be a mapping")
    _reject_private_runtime_fields(adapter_input)

    mode = adapter_input.get("mode", "dry_run")
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"unsupported mode: {mode}")

    memory_context = adapter_input.get("memory_context")
    nuance = adapter_input.get("nuance_appraisal") or {}
    if not isinstance(memory_context, dict):
        raise ValueError("memory_context must be a mapping")
    if not isinstance(nuance, dict):
        raise ValueError("nuance_appraisal must be a mapping")

    packet = build_compatibility_packet(memory_context)
    memory_confidence = float(packet["source"]["confidence"])
    nuance_confidence = _confidence(nuance)
    grounded = bool(nuance.get("grounded"))
    why_now = nuance.get("why_now")

    blocked_reasons = []
    if memory_confidence < MIN_MEMORY_CONFIDENCE:
        blocked_reasons.append("insufficient memory confidence")
    if nuance_confidence < MIN_NUANCE_CONFIDENCE:
        blocked_reasons.append("insufficient nuance confidence")
    if not grounded:
        blocked_reasons.append("insufficient grounded context")
    if not isinstance(why_now, str) or not why_now.strip():
        blocked_reasons.append("insufficient why-now justification")

    presence = decide_presence_move(
        why_now=why_now if isinstance(why_now, str) else None,
        grounded=not blocked_reasons,
        side_effect=True,
    )
    status = "ready_for_review" if presence["move"] != "hold" else "fail_closed"

    return {
        "schema": "lumi.hermes.review_card.v1",
        "status": status,
        "mode": mode,
        "memory": {
            "source": packet["source"],
            "summary": packet["compatibility_view"]["normalized_summary"],
            "ambiguity": packet["compatibility_view"]["ambiguity"],
        },
        "nuance": {
            "why_now": why_now.strip() if isinstance(why_now, str) else "",
            "grounded": grounded,
            "confidence": nuance_confidence,
        },
        "decision": presence,
        "safety": {
            "canonical_writes": 0,
            "runtime_actions": [],
            "requires_human_review": True,
            "blocked_reasons": "; ".join(blocked_reasons),
            "forbidden_host_fields": sorted(FORBIDDEN_HOST_FIELDS),
        },
    }


def _preview_blocked_reasons(adapter_input: dict[str, Any]) -> list[str]:
    blocked = []
    for field in PREVIEW_REQUIRED_FIELDS:
        if not _text(adapter_input, field):
            blocked.append(f"missing {field}")
    consent_state = _text(adapter_input, "consent_state")
    if consent_state not in {"ask_before_apply", "approved", "draft_only"}:
        blocked.append("unsupported consent_state")
    return blocked


def _text(source: dict[str, Any], field: str) -> str:
    value = source.get(field, "")
    return value.strip() if isinstance(value, str) else ""


def _reject_private_runtime_fields(adapter_input: dict[str, Any]) -> None:
    for field in sorted(FORBIDDEN_HOST_FIELDS):
        if field in adapter_input:
            raise ValueError(f"forbidden Hermes runtime field: {field}")


def _confidence(nuance: dict[str, Any]) -> float:
    value = nuance.get("confidence", 0.0)
    if not isinstance(value, (int, float)):
        return 0.0
    return float(value)
