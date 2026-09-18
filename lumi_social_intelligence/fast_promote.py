"""Fail-closed Fast Promote contracts for Live Surface metadata previews.

Fast Promote deliberately stops at a metadata-only catalogue candidate. A valid
preview is based on a reviewed, versioned manifest whose detached signature has
been verified by a host-owned trusted-key boundary. It never connects an
identity, grants a scope, calls a tool, reads context, or performs a durable or
external write.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any, Callable

MANIFEST_SCHEMA = "lumi.fast_promote.app_manifest.v1"
PREVIEW_SCHEMA = "lumi.live_surface.fast_promotion_preview.v1"
LIVE_SURFACE_CARD_SCHEMA = "lumi.live_surface.mcp_capability_card.v1"
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
LOGICAL_REFERENCE_RE = re.compile(
    r"^managed:[a-z][a-z0-9_-]*(?::[a-z][a-z0-9_-]*)*$", re.IGNORECASE
)
LOGICAL_REFERENCE_IN_TEXT_RE = re.compile(
    r"(?<![a-z0-9_-])managed:[a-z][a-z0-9_-]*(?::[a-z][a-z0-9_-]*)*(?![a-z0-9_-])",
    re.IGNORECASE,
)
SCOPE_LIKE_REFERENCE_IN_TEXT_RE = re.compile(
    r"(?<![a-z0-9_-])[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)*?\."
    r"(?:access|admin|create|delete|execute|list|manage|read|search|send|update|write)"
    r"(?![a-z0-9_.-])",
    re.IGNORECASE,
)
HOST_ALIAS_REFERENCE_SEGMENTS = {"localhost", "loopback"}
UNSAFE_PUBLIC_TEXT_RE = re.compile(
    r"(?:\b(?:api[_ -]?key|authorization|bearer|chat[_ -]?id|connection[_ -]?string|"
    r"cookie|credential|password|secret|token|user[_ -]?context|raw[_ -]?context)\b|"
    r"\b(?:localhost|loopback):\d{1,5}\b|[=@]|://)",
    re.IGNORECASE,
)

TOP_LEVEL_FIELDS = {
    "schema",
    "app",
    "publisher",
    "version",
    "signature",
    "purpose",
    "selected_capabilities",
    "transport",
    "consent",
    "retention_export",
    "memory",
    "trust",
    "rate_limits",
    "revocation",
    "effects",
}
APP_FIELDS = {"id", "name", "summary", "category", "example_prompts"}
PUBLISHER_FIELDS = {"owner", "provenance"}
SIGNATURE_FIELDS = {"algorithm", "key_id", "value"}
CAPABILITY_FIELDS = {
    "id",
    "label",
    "operation",
    "scopes",
    "input_classification",
    "output_classification",
}
TRANSPORT_FIELDS = {"kind", "provider_id", "endpoint_reference"}
CONSENT_FIELDS = {"connection", "purpose_acknowledged"}
RETENTION_EXPORT_FIELDS = {"input", "output", "export"}
MEMORY_FIELDS = {"authority", "durable_writes"}
TRUST_FIELDS = {"review_status", "provenance_verified"}
RATE_LIMIT_FIELDS = {"per_minute"}
REVOCATION_FIELDS = {"owner", "disable_path"}
EFFECT_FIELDS = {"external_writes", "durable_memory", "public_claims"}

FORBIDDEN_FIELD_NAMES = {
    "api_key",
    "authorization",
    "chat_id",
    "connection_string",
    "credential",
    "context",
    "cookie",
    "device_location",
    "location_history",
    "password",
    "raw_context",
    "secret",
    "token",
    "user_context",
}
ALLOWED_OPERATIONS = {"read", "write", "action"}
ALLOWED_INPUT_CLASSIFICATIONS = {
    "explicit_user_input",
    "identity_sensitive",
    "location_explicit_user_provided",
    "third_party_content",
}
ALLOWED_OUTPUT_CLASSIFICATIONS = {
    "minimized_ephemeral",
    "sensitive_labelled",
    "review_only",
}
ALLOWED_RETENTION_INPUT = {"none", "ephemeral"}
ALLOWED_RETENTION_OUTPUT = {"ephemeral", "expiry_labelled"}
ALLOWED_EXPORT = {"prohibited", "review_required"}
ALLOWED_MEMORY_AUTHORITY = {"none", "proposal_only"}
ALLOWED_MEMORY_WRITES = {"none", "review_required"}
ALLOWED_EFFECTS = {"none", "review_required", "reviewed_action_only"}
ALLOWED_SIGNATURE_ALGORITHMS = {"ed25519"}
# Expedited review is deliberately narrower than validation. Unknown or broader
# scopes may be represented in a reviewed manifest, but never inherit the
# low-risk route merely because they avoid a small denylist of words.
EXPEDITED_READONLY_SCOPES = {"thread.user_selected.read"}

SignatureVerifier = Callable[[bytes, Mapping[str, Any]], bool]


class _Validation:
    """Small internal accumulator to keep validation errors deterministic."""

    def __init__(self) -> None:
        self.errors: list[str] = []

    def error(self, message: str) -> None:
        if message not in self.errors:
            self.errors.append(message)


def validate_app_manifest(
    manifest: Mapping[str, Any] | Any,
    *,
    signature_verifier: SignatureVerifier | None = None,
) -> dict[str, Any]:
    """Validate a reviewed app manifest without dereferencing any transport.

    The return value is safe to log because it contains field paths and statuses,
    never arbitrary manifest values.
    """

    validation = _Validation()
    if not isinstance(manifest, Mapping):
        validation.error("manifest must be a mapping")
        return _validation_result(validation)

    _reject_forbidden_field_names(manifest, validation)
    _check_exact_fields(manifest, TOP_LEVEL_FIELDS, "manifest", validation)
    _require_text(manifest, "schema", "manifest", validation, expected=MANIFEST_SCHEMA)
    _validate_app(manifest.get("app"), validation)
    _validate_publisher(manifest.get("publisher"), validation)
    _require_text(manifest, "version", "manifest", validation, pattern=SEMVER_RE)
    _validate_signature(manifest.get("signature"), validation)
    _require_text(manifest, "purpose", "manifest", validation)
    _validate_capabilities(manifest.get("selected_capabilities"), validation)
    _validate_transport(manifest.get("transport"), validation)
    _validate_consent(manifest.get("consent"), validation)
    _validate_retention_export(manifest.get("retention_export"), validation)
    _validate_memory(manifest.get("memory"), validation)
    _validate_trust(manifest.get("trust"), validation)
    _validate_rate_limits(manifest.get("rate_limits"), validation)
    _validate_revocation(manifest.get("revocation"), validation)
    _validate_effects(manifest.get("effects"), validation)
    _validate_card_text_disclosures(manifest, validation)
    if not validation.errors:
        _verify_signature(manifest, signature_verifier, validation)
    return _validation_result(validation)


def build_fast_promotion_preview(
    manifest: Mapping[str, Any] | Any,
    *,
    signature_verifier: SignatureVerifier | None = None,
) -> dict[str, Any]:
    """Build a safe, review-routed Live Surface listing candidate.

    The function is intentionally pure. Its output has no user/context data and
    declares no activation, invocation, memory, write, or publication authority.
    """

    validation = validate_app_manifest(
        manifest, signature_verifier=signature_verifier
    )
    preview: dict[str, Any] = {
        "schema": PREVIEW_SCHEMA,
        "safety": _zero_side_effects(),
        "gates": _independent_gates(),
        "audit": {"manifest_fingerprint": _manifest_fingerprint(manifest)},
    }
    if validation["status"] != "pass":
        preview.update(
            {
                "status": "blocked_invalid_manifest",
                "validation": validation,
            }
        )
        return preview

    assert isinstance(manifest, Mapping)  # narrowed by validation
    risk = _classify_risk(manifest)
    listing_preview = _listing_preview(manifest)
    preview.update(
        {
            "status": (
                "ready_for_expedited_review"
                if risk["tier"] == "low"
                else "pending_stronger_review"
            ),
            "risk": risk,
            "validation": validation,
            "listing_preview": listing_preview,
            "live_surface_card": _live_surface_card(listing_preview, risk),
            "audit": {
                "manifest_fingerprint": _manifest_fingerprint(manifest),
                "manifest_version": manifest["version"],
                "review_status": manifest["trust"]["review_status"],
            },
        }
    )
    return preview


def _validation_result(validation: _Validation) -> dict[str, Any]:
    return {
        "status": "pass" if not validation.errors else "blocked",
        "errors": sorted(validation.errors),
    }


def _reject_forbidden_field_names(value: Any, validation: _Validation, path: str = "manifest") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            nested_path = f"{path}.{key_text}"
            if key_text in FORBIDDEN_FIELD_NAMES:
                validation.error(f"forbidden field {key_text}")
            _reject_forbidden_field_names(nested, validation, nested_path)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_forbidden_field_names(nested, validation, f"{path}[{index}]")


def _check_exact_fields(
    value: Any, allowed: set[str], path: str, validation: _Validation
) -> bool:
    if not isinstance(value, Mapping):
        validation.error(f"{path} must be a mapping")
        return False
    for key in value:
        if key not in allowed:
            validation.error(f"{path}.{key} is not allowed")
    for key in sorted(allowed):
        if key not in value:
            validation.error(f"missing {path}.{key}")
    return True


def _require_text(
    mapping: Mapping[str, Any],
    field: str,
    path: str,
    validation: _Validation,
    *,
    expected: str | None = None,
    pattern: re.Pattern[str] | None = None,
) -> None:
    value = mapping.get(field)
    qualified = f"{path}.{field}"
    if not isinstance(value, str) or not value.strip():
        validation.error(f"{qualified} must be non-empty text")
        return
    if expected is not None and value != expected:
        validation.error(f"{qualified} must be {expected}")
    if pattern is not None and not pattern.fullmatch(value):
        validation.error(f"{qualified} must be semantic version text")


def _validate_app(value: Any, validation: _Validation) -> None:
    if not _check_exact_fields(value, APP_FIELDS, "app", validation):
        return
    assert isinstance(value, Mapping)
    for field in sorted(APP_FIELDS - {"example_prompts"}):
        _require_text(value, field, "app", validation)
        _validate_public_listing_text(value.get(field), f"app.{field}", validation)
    prompts = value.get("example_prompts")
    if not isinstance(prompts, list) or not prompts or not all(
        isinstance(item, str) and item.strip() for item in prompts
    ):
        validation.error("app.example_prompts must be a non-empty text list")
        return
    for index, prompt in enumerate(prompts):
        _validate_public_listing_text(
            prompt, f"app.example_prompts[{index}]", validation
        )


def _validate_public_listing_text(
    value: Any, path: str, validation: _Validation
) -> None:
    """Reject obvious sensitive payloads from fields emitted in public previews."""

    if isinstance(value, str) and UNSAFE_PUBLIC_TEXT_RE.search(value):
        validation.error(f"{path} contains unsafe public listing text")


def _validate_card_text_disclosures(
    manifest: Mapping[str, Any], validation: _Validation
) -> None:
    """Keep structured MCP identifiers out of text copied to the review card.

    Reject before any listing/card construction rather than attempting lossy
    redaction after rendering. This prevents a signed manifest from laundering
    transport, scope, provider, app, or capability identifiers through prose.
    """

    identifiers = _card_disallowed_identifiers(manifest)
    for path, value in _card_emitted_text(manifest):
        if not isinstance(value, str):
            continue
        if (
            LOGICAL_REFERENCE_IN_TEXT_RE.search(value)
            or SCOPE_LIKE_REFERENCE_IN_TEXT_RE.search(value)
            or any(_contains_identifier(value, identifier) for identifier in identifiers)
        ):
            validation.error(f"{path} contains raw identifier forbidden from card text")


def _card_disallowed_identifiers(manifest: Mapping[str, Any]) -> set[str]:
    """Collect raw identifiers whose structured form must never be card prose."""

    identifiers: set[str] = set()
    app = manifest.get("app")
    if isinstance(app, Mapping):
        _add_text_identifier(identifiers, app.get("id"))
    transport = manifest.get("transport")
    if isinstance(transport, Mapping):
        for field in ("provider_id", "endpoint_reference"):
            _add_text_identifier(identifiers, transport.get(field))
    capabilities = manifest.get("selected_capabilities")
    if isinstance(capabilities, list):
        for capability in capabilities:
            if not isinstance(capability, Mapping):
                continue
            _add_text_identifier(identifiers, capability.get("id"))
            scopes = capability.get("scopes")
            if isinstance(scopes, list):
                for scope in scopes:
                    _add_text_identifier(identifiers, scope)
    return identifiers


def _card_emitted_text(manifest: Mapping[str, Any]) -> list[tuple[str, Any]]:
    """Return exactly the manifest text fields copied into a Live Surface card."""

    emitted: list[tuple[str, Any]] = []
    app = manifest.get("app")
    if isinstance(app, Mapping):
        for field in ("name", "summary", "category"):
            emitted.append((f"app.{field}", app.get(field)))
        prompts = app.get("example_prompts")
        if isinstance(prompts, list):
            emitted.extend(
                (f"app.example_prompts[{index}]", prompt)
                for index, prompt in enumerate(prompts)
            )
    capabilities = manifest.get("selected_capabilities")
    if isinstance(capabilities, list):
        for index, capability in enumerate(capabilities):
            if isinstance(capability, Mapping):
                emitted.append(
                    (f"selected_capabilities[{index}].label", capability.get("label"))
                )
    return emitted


def _add_text_identifier(identifiers: set[str], value: Any) -> None:
    if isinstance(value, str) and value.strip():
        identifiers.add(value)


def _contains_identifier(text: str, identifier: str) -> bool:
    return re.search(
        rf"(?<![a-z0-9_-]){re.escape(identifier)}(?![a-z0-9_-])",
        text,
        re.IGNORECASE,
    ) is not None


def _validate_publisher(value: Any, validation: _Validation) -> None:
    if not _check_exact_fields(value, PUBLISHER_FIELDS, "publisher", validation):
        return
    assert isinstance(value, Mapping)
    for field in sorted(PUBLISHER_FIELDS):
        _require_text(value, field, "publisher", validation)


def _validate_signature(value: Any, validation: _Validation) -> None:
    if not _check_exact_fields(value, SIGNATURE_FIELDS, "signature", validation):
        return
    assert isinstance(value, Mapping)
    if value.get("algorithm") not in ALLOWED_SIGNATURE_ALGORITHMS:
        validation.error("signature.algorithm is unsupported")
    for field in ("key_id", "value"):
        _require_text(value, field, "signature", validation)


def _verify_signature(
    manifest: Mapping[str, Any],
    signature_verifier: SignatureVerifier | None,
    validation: _Validation,
) -> None:
    """Delegate cryptographic trust to the host-owned trusted-key boundary."""

    if signature_verifier is None:
        validation.error("signature verifier is required")
        return
    try:
        verified = signature_verifier(
            _canonical_signed_payload(manifest), manifest["signature"]
        )
    except Exception:
        validation.error("signature verifier failed")
        return
    if verified is not True:
        validation.error("signature is not trusted")


def _validate_capabilities(value: Any, validation: _Validation) -> None:
    if not isinstance(value, list) or not value:
        validation.error("selected_capabilities must be a non-empty list")
        return
    for index, capability in enumerate(value):
        path = f"selected_capabilities[{index}]"
        if not _check_exact_fields(capability, CAPABILITY_FIELDS, path, validation):
            continue
        assert isinstance(capability, Mapping)
        for field in ("id", "label"):
            _require_text(capability, field, path, validation)
            _validate_public_listing_text(capability.get(field), f"{path}.{field}", validation)
        operation = capability.get("operation")
        if operation not in ALLOWED_OPERATIONS:
            validation.error(f"{path}.operation must be one of {sorted(ALLOWED_OPERATIONS)}")
        scopes = capability.get("scopes")
        if not isinstance(scopes, list) or not scopes or not all(
            isinstance(scope, str) and scope.strip() for scope in scopes
        ):
            validation.error(f"{path}.scopes must be a non-empty text list")
        input_classification = capability.get("input_classification")
        if input_classification not in ALLOWED_INPUT_CLASSIFICATIONS:
            validation.error(f"{path}.input_classification is unsupported")
        output_classification = capability.get("output_classification")
        if output_classification not in ALLOWED_OUTPUT_CLASSIFICATIONS:
            validation.error(f"{path}.output_classification is unsupported")


def _validate_transport(value: Any, validation: _Validation) -> None:
    if not _check_exact_fields(value, TRANSPORT_FIELDS, "transport", validation):
        return
    assert isinstance(value, Mapping)
    if value.get("kind") != "mcp":
        validation.error("transport.kind must be mcp")
    for field in ("provider_id", "endpoint_reference"):
        _require_text(value, field, "transport", validation)
    endpoint_reference = value.get("endpoint_reference")
    if (
        not isinstance(endpoint_reference, str)
        or not LOGICAL_REFERENCE_RE.fullmatch(endpoint_reference)
        or _has_host_alias_segment(endpoint_reference)
    ):
        validation.error("transport.endpoint_reference must be a logical reference, not a raw endpoint")


def _has_host_alias_segment(endpoint_reference: str) -> bool:
    """Keep managed references logical; hosts belong only in host-owned config."""

    return any(
        segment.casefold() in HOST_ALIAS_REFERENCE_SEGMENTS
        for segment in endpoint_reference.split(":")[1:]
    )


def _validate_consent(value: Any, validation: _Validation) -> None:
    if not _check_exact_fields(value, CONSENT_FIELDS, "consent", validation):
        return
    assert isinstance(value, Mapping)
    if value.get("connection") != "explicit_user_approval":
        validation.error("consent.connection must be explicit_user_approval")
    if value.get("purpose_acknowledged") is not True:
        validation.error("consent.purpose_acknowledged must be true")


def _validate_retention_export(value: Any, validation: _Validation) -> None:
    if not _check_exact_fields(value, RETENTION_EXPORT_FIELDS, "retention_export", validation):
        return
    assert isinstance(value, Mapping)
    if value.get("input") not in ALLOWED_RETENTION_INPUT:
        validation.error("retention_export.input is unsupported")
    if value.get("output") not in ALLOWED_RETENTION_OUTPUT:
        validation.error("retention_export.output is unsupported")
    if value.get("export") not in ALLOWED_EXPORT:
        validation.error("retention_export.export is unsupported")


def _validate_memory(value: Any, validation: _Validation) -> None:
    if not _check_exact_fields(value, MEMORY_FIELDS, "memory", validation):
        return
    assert isinstance(value, Mapping)
    if value.get("authority") not in ALLOWED_MEMORY_AUTHORITY:
        validation.error("memory.authority is unsupported")
    if value.get("durable_writes") not in ALLOWED_MEMORY_WRITES:
        validation.error("memory.durable_writes is unsupported")


def _validate_trust(value: Any, validation: _Validation) -> None:
    if not _check_exact_fields(value, TRUST_FIELDS, "trust", validation):
        return
    assert isinstance(value, Mapping)
    if value.get("review_status") != "approved":
        validation.error("trust.review_status must be approved")
    if value.get("provenance_verified") is not True:
        validation.error("trust.provenance_verified must be true")


def _validate_rate_limits(value: Any, validation: _Validation) -> None:
    if not _check_exact_fields(value, RATE_LIMIT_FIELDS, "rate_limits", validation):
        return
    assert isinstance(value, Mapping)
    per_minute = value.get("per_minute")
    if isinstance(per_minute, bool) or not isinstance(per_minute, int) or not 1 <= per_minute <= 100:
        validation.error("rate_limits.per_minute must be an integer from 1 to 100")


def _validate_revocation(value: Any, validation: _Validation) -> None:
    if not _check_exact_fields(value, REVOCATION_FIELDS, "revocation", validation):
        return
    assert isinstance(value, Mapping)
    for field in sorted(REVOCATION_FIELDS):
        _require_text(value, field, "revocation", validation)


def _validate_effects(value: Any, validation: _Validation) -> None:
    if not _check_exact_fields(value, EFFECT_FIELDS, "effects", validation):
        return
    assert isinstance(value, Mapping)
    for field in sorted(EFFECT_FIELDS):
        if value.get(field) not in ALLOWED_EFFECTS:
            validation.error(f"effects.{field} is unsupported")


def _classify_risk(manifest: Mapping[str, Any]) -> dict[str, str]:
    capabilities = manifest["selected_capabilities"]
    effects = manifest["effects"]
    memory = manifest["memory"]
    retention = manifest["retention_export"]

    has_high_effect = any(effects[name] != "none" for name in EFFECT_FIELDS)
    has_memory_effect = memory["authority"] != "none" or memory["durable_writes"] != "none"
    has_non_read_operation = any(item["operation"] != "read" for item in capabilities)
    if has_high_effect or has_memory_effect or has_non_read_operation:
        return {"tier": "high", "review_route": "stronger_review_required"}

    sensitive_inputs = {
        "identity_sensitive",
        "location_explicit_user_provided",
        "third_party_content",
    }
    has_sensitive_input = any(
        item["input_classification"] in sensitive_inputs for item in capabilities
    )
    has_broad_scope = any(
        scope not in EXPEDITED_READONLY_SCOPES
        for item in capabilities
        for scope in item["scopes"]
    )
    has_extended_data_handling = (
        retention["input"] != "none"
        or retention["output"] != "ephemeral"
        or retention["export"] != "prohibited"
        or any(item["output_classification"] != "minimized_ephemeral" for item in capabilities)
    )
    if has_sensitive_input or has_broad_scope or has_extended_data_handling:
        return {"tier": "sensitive", "review_route": "stronger_review_required"}
    return {"tier": "low", "review_route": "expedited_readonly_review"}


def _listing_preview(manifest: Mapping[str, Any]) -> dict[str, Any]:
    app = manifest["app"]
    return {
        "app_id": app["id"],
        "name": app["name"],
        "summary": app["summary"],
        "category": app["category"],
        "example_prompts": list(app["example_prompts"]),
        "capabilities": [
            {
                "id": item["id"],
                "label": item["label"],
                "operation": item["operation"],
            }
            for item in manifest["selected_capabilities"]
        ],
        "preview_mode": "metadata_only",
    }


def _live_surface_card(
    listing_preview: Mapping[str, Any], risk: Mapping[str, str]
) -> dict[str, Any]:
    """Build a zero-authority Live Surface card from public listing metadata.

    This remains a review affordance, never a connection or invocation control.
    Transport, scope, provider, and manifest identifiers are intentionally absent.
    """

    return {
        "schema": LIVE_SURFACE_CARD_SCHEMA,
        "mode": "metadata_review_only",
        "status": "ready_for_review",
        "headline": listing_preview["name"],
        "summary": listing_preview["summary"],
        "category": listing_preview["category"],
        "example_prompts": list(listing_preview["example_prompts"]),
        "capabilities": [
            {"label": item["label"], "operation": item["operation"]}
            for item in listing_preview["capabilities"]
        ],
        "next_step": "review_before_connection",
        "review": {
            "route": risk["review_route"],
            "requires_human_review": True,
        },
        "gates": {
            "connection": "explicit_approval_required_before_activation",
            "invocation": "not_enabled_by_listing_preview",
        },
        "safety": _zero_side_effects(),
    }


def _zero_side_effects() -> dict[str, Any]:
    return {
        "user_context_reads": 0,
        "tool_invocations": 0,
        "scopes_granted": [],
        "durable_writes": 0,
        "external_actions": 0,
        "publications": 0,
    }


def _independent_gates() -> dict[str, str]:
    return {
        "connection": "explicit_approval_required_before_activation",
        "invocation": "not_enabled_by_listing_preview",
        "external_writes": "independent_approval_required",
        "durable_memory": "independent_approval_required",
        "public_claims": "independent_approval_required",
        "revocation": "available_before_activation",
    }


def _canonical_signed_payload(manifest: Mapping[str, Any]) -> bytes:
    """Return the canonical bytes verified by the trusted signature boundary."""

    unsigned_manifest = {
        key: value for key, value in manifest.items() if key != "signature"
    }
    return json.dumps(
        unsigned_manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _manifest_fingerprint(manifest: Any) -> str:
    """Return a stable fingerprint without putting manifest contents in output."""

    try:
        canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError):
        canonical = "<unserializable-manifest>"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
