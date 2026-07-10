"""v0.2 demo evidence receipt contract.

This module turns a public-safe synthetic demo fixture into an inspectable receipt
for the v0.2 live-proof path. It deliberately separates observed behavior from
shadow-only behavior and never performs host/runtime side effects.
"""

from __future__ import annotations

from typing import Any

from adapters.hermes.lumi_for_hermes import (
    build_outbound_emoji_presence_card,
    build_reaction_presence_card,
    build_review_card,
)

FORBIDDEN_DEMO_FIELDS = {
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

OBSERVED_STATUSES = {"observed"}
SHADOW_STATUSES = {"shadow_only", "not_observed", "blocked", "limited"}


def build_v02_demo_receipt(fixture: dict[str, Any]) -> dict[str, Any]:
    """Build a v0.2 demo receipt with zero runtime side effects."""

    if not isinstance(fixture, dict):
        raise ValueError("v0.2 demo fixture input must be a mapping")
    _reject_private_runtime_fields(fixture)

    memory_context = _mapping(fixture, "memory_context")
    nuance_appraisal = _mapping(fixture, "nuance_appraisal")
    reaction_input = dict(_mapping(fixture, "reaction_input"))
    outbound_input = dict(_mapping(fixture, "outbound_emoji_input"))

    review_card = build_review_card({
        "schema": "lumi.hermes.adapter_input.v1",
        "mode": "review_gated",
        "memory_context": memory_context,
        "nuance_appraisal": nuance_appraisal,
        "requested_effect": "v02_demo_receipt",
    })

    reaction_input.setdefault("schema", "lumi.hermes.reaction_presence_input.v1")
    reaction_input.setdefault("mode", "reaction_presence_shadow")
    reaction_input.setdefault("surface", "telegram")
    reaction_card = build_reaction_presence_card(reaction_input)

    outbound_input.setdefault("schema", "lumi.hermes.outbound_emoji_presence_input.v1")
    outbound_input.setdefault("mode", "outbound_emoji_presence_shadow")
    outbound_input.setdefault("surface", "telegram")
    outbound_card = build_outbound_emoji_presence_card(outbound_input)

    observations = _observations(fixture.get("live_observations", []))
    observed = [item["behavior"] for item in observations if item["status"] in OBSERVED_STATUSES]
    shadow_only = [item["behavior"] for item in observations if item["status"] in SHADOW_STATUSES]

    platform_delivery_verified = bool(
        outbound_card.get("delivery_boundary", {}).get("platform_delivery_verified")
    )
    live_native_reaction_observed = any(
        item["status"] == "observed" and "native" in item["behavior"] and "reaction" in item["behavior"]
        for item in observations
    )
    safe_to_claim_live_delivery = platform_delivery_verified and live_native_reaction_observed

    receipt = {
        "schema": "lumi.v02.demo_receipt.v1",
        "demo_id": _text(fixture, "demo_id") or "synthetic-v02-demo",
        "observed_at": _text(fixture, "observed_at"),
        "status": "valid_v02_demo_receipt",
        "flow": {
            "memory": review_card["memory"],
            "nuance": review_card["nuance"],
            "presence_decision": review_card["decision"],
            "review_card_status": review_card["status"],
        },
        "reaction_aware_presence": reaction_card,
        "outbound_emoji_presence": outbound_card,
        "evidence": {
            "observed": observed,
            "shadow_only": shadow_only,
            "receipts": [
                "review_card",
                "reaction_aware_presence_record",
                "outbound_emoji_presence_record",
            ],
            "notes": [item["evidence"] for item in observations if item.get("evidence")],
        },
        "claims": {
            "context_to_appraisal_to_presence_receipt": review_card["status"] == "ready_for_review",
            "safe_to_claim_live_native_reaction_delivery": safe_to_claim_live_delivery,
            "observed_behavior_is_separated_from_shadow_behavior": bool(observed or shadow_only),
        },
        "safety": {
            "canonical_writes": 0,
            "runtime_actions": [],
            "telegram_messages_sent": 0,
            "telegram_reactions_sent": 0,
            "telegram_api_reads": 0,
            "live_memory_writes": 0,
            "raw_private_transcripts_stored": 0,
            "private_runtime_fields_retained": False,
            "requires_human_review_before_live_wiring": True,
            "blocked_reasons": "",
            "forbidden_fields": sorted(FORBIDDEN_DEMO_FIELDS),
        },
    }

    errors = validate_v02_demo_receipt(receipt)
    if errors:
        receipt["status"] = "fail_closed"
        receipt["safety"]["blocked_reasons"] = "; ".join(errors)
        receipt["claims"]["safe_to_claim_live_native_reaction_delivery"] = False
    return receipt


def validate_v02_demo_receipt(receipt: dict[str, Any]) -> list[str]:
    """Return contract errors for a v0.2 demo receipt."""

    errors: list[str] = []
    if not isinstance(receipt, dict):
        return ["receipt must be a mapping"]
    if receipt.get("schema") != "lumi.v02.demo_receipt.v1":
        errors.append("schema must be lumi.v02.demo_receipt.v1")

    flow = receipt.get("flow")
    if not isinstance(flow, dict):
        errors.append("flow must be a mapping")
        flow = {}
    if flow.get("review_card_status") != "ready_for_review":
        errors.append("review card must be ready for review")
    presence = flow.get("presence_decision")
    if not isinstance(presence, dict):
        errors.append("presence_decision must be a mapping")
    elif presence.get("side_effect_allowed") is not False:
        errors.append("presence decision must not allow side effects")

    evidence = receipt.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("evidence must be a mapping")
        evidence = {}
    observed = evidence.get("observed", [])
    shadow_only = evidence.get("shadow_only", [])
    if not isinstance(observed, list) or not isinstance(shadow_only, list):
        errors.append("observed and shadow_only evidence must be lists")
    if not observed and not shadow_only:
        errors.append("demo evidence must distinguish observed or shadow behavior")

    claims = receipt.get("claims")
    if not isinstance(claims, dict):
        errors.append("claims must be a mapping")
        claims = {}
    observed_labels = observed if isinstance(observed, list) else []
    shadow_labels = shadow_only if isinstance(shadow_only, list) else []
    has_native_observation = any(
        isinstance(label, str) and "native" in label and "reaction" in label
        for label in observed_labels
    )
    has_native_shadow_claim = any(
        isinstance(label, str) and "native" in label and "reaction" in label
        for label in shadow_labels
    )
    if claims.get("safe_to_claim_live_native_reaction_delivery") is True and not has_native_observation:
        errors.append("cannot claim live native reaction delivery without observed evidence")
    if not has_native_observation and not has_native_shadow_claim:
        outbound = receipt.get("outbound_emoji_presence")
        delivery = outbound.get("delivery_boundary", {}) if isinstance(outbound, dict) else {}
        if delivery.get("platform_delivery_verified") is True:
            errors.append("cannot claim live native reaction delivery without observed evidence")
    if claims.get("observed_behavior_is_separated_from_shadow_behavior") is not True:
        errors.append("observed and shadow behavior must be explicitly separated")

    safety = receipt.get("safety")
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
    ]:
        if safety.get(key) != 0:
            errors.append(f"{key} must be 0")
    if safety.get("runtime_actions") != []:
        errors.append("runtime_actions must stay empty")
    if safety.get("private_runtime_fields_retained") is not False:
        errors.append("private runtime fields must not be retained")
    if safety.get("requires_human_review_before_live_wiring") is not True:
        errors.append("human review is required before live wiring")

    return _dedupe(errors)


def _mapping(source: dict[str, Any], key: str) -> dict[str, Any]:
    value = source.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a mapping")
    return value


def _observations(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError("live_observations must be a list")
    observations: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"live_observations[{index}] must be a mapping")
        behavior = _text(item, "behavior")
        status = _text(item, "status")
        if not behavior:
            raise ValueError(f"live_observations[{index}].behavior is required")
        if status not in OBSERVED_STATUSES | SHADOW_STATUSES:
            raise ValueError(f"unsupported live observation status: {status}")
        observations.append({
            "surface": _text(item, "surface") or "unknown",
            "behavior": behavior,
            "status": status,
            "evidence": _text(item, "evidence"),
        })
    return observations


def _reject_private_runtime_fields(value: Any, path: str = "fixture") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in FORBIDDEN_DEMO_FIELDS:
                raise ValueError(f"forbidden private/runtime field: {path}.{key}")
            _reject_private_runtime_fields(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_private_runtime_fields(item, f"{path}[{index}]")


def _text(source: dict[str, Any], key: str) -> str:
    value = source.get(key, "") if isinstance(source, dict) else ""
    return value.strip() if isinstance(value, str) else ""


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result
