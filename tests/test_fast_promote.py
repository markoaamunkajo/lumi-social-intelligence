from __future__ import annotations

import copy
import json
from typing import Any

import pytest

from lumi_social_intelligence.fast_promote import (
    build_fast_promotion_preview,
    validate_app_manifest,
)


def trusted_test_verifier(payload: bytes, signature: dict[str, Any]) -> bool:
    """Test stand-in for the catalogue's external trusted-key verifier."""

    signed_manifest = json.loads(payload)
    return (
        "signature" not in signed_manifest
        and signed_manifest["app"]["id"] == "user-selected-thread-summary"
        and signature
        == {
            "algorithm": "ed25519",
            "key_id": "lumi-review-2026-01",
            "value": "test-signature",
        }
    )


def low_risk_manifest() -> dict:
    return {
        "schema": "lumi.fast_promote.app_manifest.v1",
        "app": {
            "id": "user-selected-thread-summary",
            "name": "Selected Thread Summary",
            "summary": "Summarises a thread explicitly selected by the user.",
            "category": "project continuity",
            "example_prompts": ["Summarise the thread I selected."],
        },
        "publisher": {
            "owner": "lumi-catalogue",
            "provenance": "reviewed first-party manifest",
        },
        "version": "1.0.0",
        "signature": {
            "algorithm": "ed25519",
            "key_id": "lumi-review-2026-01",
            "value": "test-signature",
        },
        "purpose": "Provide a concise, user-requested summary of explicitly supplied text.",
        "selected_capabilities": [
            {
                "id": "summarize_user_selected_thread",
                "label": "Summarise selected thread",
                "operation": "read",
                "scopes": ["thread.user_selected.read"],
                "input_classification": "explicit_user_input",
                "output_classification": "minimized_ephemeral",
            }
        ],
        "transport": {
            "kind": "mcp",
            "provider_id": "thread-summary",
            "endpoint_reference": "managed:thread-summary:v1",
        },
        "consent": {
            "connection": "explicit_user_approval",
            "purpose_acknowledged": True,
        },
        "retention_export": {
            "input": "none",
            "output": "ephemeral",
            "export": "prohibited",
        },
        "memory": {"authority": "none", "durable_writes": "none"},
        "trust": {"review_status": "approved", "provenance_verified": True},
        "rate_limits": {"per_minute": 5},
        "revocation": {
            "owner": "lumi-catalogue",
            "disable_path": "catalogue:disable:user-selected-thread-summary",
        },
        "effects": {
            "external_writes": "none",
            "durable_memory": "none",
            "public_claims": "none",
        },
    }


def preview(manifest: dict) -> dict:
    return build_fast_promotion_preview(
        manifest, signature_verifier=trusted_test_verifier
    )


def test_valid_signed_read_only_manifest_builds_metadata_only_preview_for_expedited_review():
    result = preview(low_risk_manifest())

    assert result["schema"] == "lumi.live_surface.fast_promotion_preview.v1"
    assert result["status"] == "ready_for_expedited_review"
    assert result["risk"] == {
        "tier": "low",
        "review_route": "expedited_readonly_review",
    }
    assert result["listing_preview"] == {
        "app_id": "user-selected-thread-summary",
        "name": "Selected Thread Summary",
        "summary": "Summarises a thread explicitly selected by the user.",
        "category": "project continuity",
        "example_prompts": ["Summarise the thread I selected."],
        "capabilities": [
            {
                "id": "summarize_user_selected_thread",
                "label": "Summarise selected thread",
                "operation": "read",
            }
        ],
        "preview_mode": "metadata_only",
    }
    assert result["safety"] == {
        "user_context_reads": 0,
        "tool_invocations": 0,
        "scopes_granted": [],
        "durable_writes": 0,
        "external_actions": 0,
        "publications": 0,
    }
    assert result["gates"] == {
        "connection": "explicit_approval_required_before_activation",
        "invocation": "not_enabled_by_listing_preview",
        "external_writes": "independent_approval_required",
        "durable_memory": "independent_approval_required",
        "public_claims": "independent_approval_required",
        "revocation": "available_before_activation",
    }


def test_missing_signature_or_verifier_fails_closed_without_listing():
    unsigned_manifest = low_risk_manifest()
    unsigned_manifest.pop("signature")

    unsigned = build_fast_promotion_preview(unsigned_manifest)
    unverified = build_fast_promotion_preview(low_risk_manifest())

    assert unsigned["status"] == "blocked_invalid_manifest"
    assert unverified["status"] == "blocked_invalid_manifest"
    assert "listing_preview" not in unsigned
    assert "listing_preview" not in unverified
    assert any("signature" in error for error in unsigned["validation"]["errors"])
    assert "signature verifier is required" in unverified["validation"]["errors"]


def test_sensitive_effects_route_to_stronger_review_without_enabling_them():
    manifest = low_risk_manifest()
    manifest["selected_capabilities"][0]["operation"] = "write"
    manifest["effects"] = {
        "external_writes": "reviewed_action_only",
        "durable_memory": "review_required",
        "public_claims": "review_required",
    }

    result = preview(manifest)

    assert result["status"] == "pending_stronger_review"
    assert result["risk"] == {
        "tier": "high",
        "review_route": "stronger_review_required",
    }
    assert result["listing_preview"]["preview_mode"] == "metadata_only"
    assert result["safety"]["external_actions"] == 0
    assert result["safety"]["durable_writes"] == 0
    assert result["gates"]["external_writes"] == "independent_approval_required"
    assert result["gates"]["durable_memory"] == "independent_approval_required"
    assert result["gates"]["public_claims"] == "independent_approval_required"


def test_missing_review_or_forbidden_context_fails_closed_without_listing():
    manifest = low_risk_manifest()
    manifest["trust"]["review_status"] = "draft"
    manifest["user_context"] = {"raw": "never belongs in a manifest"}

    validation = validate_app_manifest(
        manifest, signature_verifier=trusted_test_verifier
    )
    result = preview(manifest)

    assert validation["status"] == "blocked"
    assert any("trust.review_status" in error for error in validation["errors"])
    assert any("forbidden field user_context" in error for error in validation["errors"])
    assert result["status"] == "blocked_invalid_manifest"
    assert "listing_preview" not in result
    assert result["safety"]["tool_invocations"] == 0


def test_preview_redacts_transport_and_never_echoes_raw_manifest_payloads():
    manifest = low_risk_manifest()
    manifest["transport"]["endpoint_reference"] = "managed:private-but-logical-reference"
    manifest["selected_capabilities"][0]["input_example"] = "private user supplied text"

    result = preview(manifest)
    encoded_preview = json.dumps(result, sort_keys=True)

    assert result["status"] == "blocked_invalid_manifest"
    assert "endpoint_reference" not in encoded_preview
    assert "private user supplied text" not in encoded_preview
    assert "managed:private-but-logical-reference" not in encoded_preview


def test_fingerprint_is_deterministic_and_changes_when_manifest_version_changes():
    manifest = low_risk_manifest()
    first = preview(manifest)
    same = preview(copy.deepcopy(manifest))
    changed_manifest = low_risk_manifest()
    changed_manifest["version"] = "1.0.1"
    changed = preview(changed_manifest)

    assert first["audit"]["manifest_fingerprint"] == same["audit"]["manifest_fingerprint"]
    assert first["audit"]["manifest_fingerprint"] != changed["audit"]["manifest_fingerprint"]


def test_non_allowlisted_data_scope_requires_stronger_review():
    manifest = low_risk_manifest()
    manifest["selected_capabilities"][0]["scopes"] = ["mail.all_messages.read"]

    result = preview(manifest)

    assert result["status"] == "pending_stronger_review"
    assert result["risk"] == {
        "tier": "sensitive",
        "review_route": "stronger_review_required",
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", "Support token=secret-live-value"),
        ("summary", "Support token=secret-live-value"),
        ("category", "Support token=secret-live-value"),
        ("example_prompts", ["Connect https://private.example.invalid/mcp"]),
    ],
)
def test_public_listing_text_with_sensitive_data_fails_closed_without_listing(
    field: str, value: object
):
    manifest = low_risk_manifest()
    manifest["app"][field] = value

    result = preview(manifest)

    assert result["status"] == "blocked_invalid_manifest"
    assert "listing_preview" not in result
    assert f"app.{field}" in result["validation"]["errors"][0]


def test_raw_host_port_transport_reference_fails_closed_without_listing():
    manifest = low_risk_manifest()
    manifest["transport"]["endpoint_reference"] = "localhost:3000/mcp"

    result = preview(manifest)

    assert result["status"] == "blocked_invalid_manifest"
    assert "listing_preview" not in result
    assert (
        "transport.endpoint_reference must be a logical reference, not a raw endpoint"
        in result["validation"]["errors"]
    )


def test_raw_host_alias_transport_reference_fails_closed_without_listing():
    manifest = low_risk_manifest()
    manifest["transport"]["endpoint_reference"] = "localhost:mcp"

    result = preview(manifest)

    assert result["status"] == "blocked_invalid_manifest"
    assert "listing_preview" not in result


@pytest.mark.parametrize(
    ("path", "value"),
    [
        ("app.summary", "Connect at localhost:3000"),
        ("selected_capabilities[0].id", "bearer=live-token"),
        ("selected_capabilities[0].label", "Use bearer=live-token"),
    ],
)
def test_all_public_preview_text_rejects_sensitive_or_transport_like_values(
    path: str, value: str
):
    manifest = low_risk_manifest()
    if path.startswith("app."):
        manifest["app"][path.removeprefix("app.")] = value
    else:
        manifest["selected_capabilities"][0][path.rsplit(".", 1)[1]] = value

    result = preview(manifest)

    assert result["status"] == "blocked_invalid_manifest"
    assert "listing_preview" not in result
    assert any(path in error for error in result["validation"]["errors"])


def test_managed_transport_reference_cannot_embed_host_alias():
    manifest = low_risk_manifest()
    manifest["transport"]["endpoint_reference"] = "managed:localhost:mcp"

    result = preview(manifest)

    assert result["status"] == "blocked_invalid_manifest"
    assert "listing_preview" not in result
    assert (
        "transport.endpoint_reference must be a logical reference, not a raw endpoint"
        in result["validation"]["errors"]
    )


def test_verified_manifest_emits_a_frictionless_review_only_live_surface_card():
    result = preview(low_risk_manifest())

    assert result["live_surface_card"] == {
        "schema": "lumi.live_surface.mcp_capability_card.v1",
        "mode": "metadata_review_only",
        "status": "ready_for_review",
        "headline": "Selected Thread Summary",
        "summary": "Summarises a thread explicitly selected by the user.",
        "category": "project continuity",
        "example_prompts": ["Summarise the thread I selected."],
        "capabilities": [
            {"label": "Summarise selected thread", "operation": "read"}
        ],
        "next_step": "review_before_connection",
        "review": {
            "route": "expedited_readonly_review",
            "requires_human_review": True,
        },
        "gates": {
            "connection": "explicit_approval_required_before_activation",
            "invocation": "not_enabled_by_listing_preview",
        },
        "safety": {
            "user_context_reads": 0,
            "tool_invocations": 0,
            "scopes_granted": [],
            "durable_writes": 0,
            "external_actions": 0,
            "publications": 0,
        },
    }
    rendered = json.dumps(result["live_surface_card"], sort_keys=True)
    for forbidden in (
        "endpoint_reference",
        "provider_id",
        "thread.user_selected.read",
        "managed:thread-summary:v1",
    ):
        assert forbidden not in rendered


def test_invalid_manifest_never_emits_live_surface_card():
    manifest = low_risk_manifest()
    manifest["signature"]["value"] = "untrusted"

    result = preview(manifest)

    assert result["status"] == "blocked_invalid_manifest"
    assert "live_surface_card" not in result


@pytest.mark.parametrize(
    "path",
    (
        "app.name",
        "app.summary",
        "app.category",
        "app.example_prompts",
        "selected_capabilities[0].label",
    ),
)
@pytest.mark.parametrize(
    "raw_identifier",
    (
        "managed:thread-summary:v1",
        "thread.user_selected.read",
        "thread-summary",
        "user-selected-thread-summary",
        "summarize_user_selected_thread",
    ),
)
def test_card_text_cannot_launder_raw_manifest_identifiers(
    path: str, raw_identifier: str
):
    manifest = low_risk_manifest()
    text = f"Useful capability: {raw_identifier}"
    if path == "app.example_prompts":
        manifest["app"]["example_prompts"] = [text]
    elif path.startswith("app."):
        manifest["app"][path.removeprefix("app.")] = text
    else:
        manifest["selected_capabilities"][0]["label"] = text

    result = preview(manifest)

    assert result["status"] == "blocked_invalid_manifest"
    assert "listing_preview" not in result
    assert "live_surface_card" not in result
    assert any(path in error and "raw identifier" in error for error in result["validation"]["errors"])


@pytest.mark.parametrize(
    "path",
    (
        "app.name",
        "app.summary",
        "app.category",
        "app.example_prompts",
        "selected_capabilities[0].label",
    ),
)
def test_card_text_rejects_unlisted_logical_references(path: str):
    manifest = low_risk_manifest()
    text = "Useful capability: managed:unlisted-reference:v1"
    if path == "app.example_prompts":
        manifest["app"]["example_prompts"] = [text]
    elif path.startswith("app."):
        manifest["app"][path.removeprefix("app.")] = text
    else:
        manifest["selected_capabilities"][0]["label"] = text

    result = preview(manifest)

    assert result["status"] == "blocked_invalid_manifest"
    assert "listing_preview" not in result
    assert "live_surface_card" not in result
    assert any(path in error and "raw identifier" in error for error in result["validation"]["errors"])


@pytest.mark.parametrize(
    "path",
    (
        "app.name",
        "app.summary",
        "app.category",
        "app.example_prompts",
        "selected_capabilities[0].label",
    ),
)
@pytest.mark.parametrize(
    "scope_like_reference",
    ("mail.read", "calendar.events.read"),
)
def test_card_text_rejects_unlisted_permission_shaped_references(
    path: str, scope_like_reference: str
):
    manifest = low_risk_manifest()
    text = f"Useful capability: {scope_like_reference}"
    if path == "app.example_prompts":
        manifest["app"]["example_prompts"] = [text]
    elif path.startswith("app."):
        manifest["app"][path.removeprefix("app.")] = text
    else:
        manifest["selected_capabilities"][0]["label"] = text

    result = preview(manifest)

    assert result["status"] == "blocked_invalid_manifest"
    assert "listing_preview" not in result
    assert "live_surface_card" not in result
    assert any(path in error and "raw identifier" in error for error in result["validation"]["errors"])


@pytest.mark.parametrize(
    "summary",
    (
        "Browse the docs.api.reference guide before reviewing.",
        "Consult docs.read.reference before reviewing.",
    ),
)
def test_card_text_permits_benign_dotted_prose(summary: str):
    manifest = low_risk_manifest()
    manifest["app"]["summary"] = summary

    result = preview(manifest)

    assert result["status"] == "ready_for_expedited_review"
    assert result["live_surface_card"]["summary"] == manifest["app"]["summary"]
