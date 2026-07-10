"""Public-safe Lumi for Hermes preview adapter.

The adapter is intentionally proposal-only: it turns explicit synthetic/host-provided
context into an inspectable review card and never touches Hermes runtime state.
"""

from __future__ import annotations

from typing import Any

from core.presence.src.lumi_presence import decide_presence_move
from lumi_social_intelligence.memory_provider import build_compatibility_packet

FORBIDDEN_HOST_FIELDS = {"chat_id", "job_id", "scheduler_queue", "runtime_state"}
SUPPORTED_MODES = {"dry_run", "review_gated"}
MIN_MEMORY_CONFIDENCE = 0.7
MIN_NUANCE_CONFIDENCE = 0.7


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


def _reject_private_runtime_fields(adapter_input: dict[str, Any]) -> None:
    for field in sorted(FORBIDDEN_HOST_FIELDS):
        if field in adapter_input:
            raise ValueError(f"forbidden Hermes runtime field: {field}")


def _confidence(nuance: dict[str, Any]) -> float:
    value = nuance.get("confidence", 0.0)
    if not isinstance(value, (int, float)):
        return 0.0
    return float(value)
