from lumi_social_intelligence.consent_memory_boundary import (
    REQUIRED_BOUNDARY_FIELDS,
    build_consent_memory_boundary_record,
    validate_consent_memory_boundary_record,
)


def _valid_payload():
    return {
        "schema": "lumi.consent_memory_boundary.input.v1",
        "session_goal": "Keep Lumi preview learning review-only until explicit consent exists.",
        "consent_state": "review_requested",
        "memory_intent": {
            "kind": "possible_preference_learning",
            "description": "A small preference may be worth remembering later, but only after review.",
            "durability": "durable_only_after_explicit_approval",
        },
        "extraction_boundary": {
            "thinking_space_status": "private_thinking_space",
            "allowed_use": "summarize_for_review_only",
            "forbidden_use": "extract_as_company_truth_or_durable_memory",
        },
        "approved_scope": [],
        "denied_scope": ["canonical_memory_write", "runtime_action", "telegram_send", "scheduler_mutation"],
        "proposed_memory_record": {
            "content": "User may prefer lightweight review summaries over intrusive cards.",
            "target": "user",
            "status": "draft_requires_explicit_approval",
        },
        "review_status": "requires_human_review",
        "acceptance_evidence": "Record blocks writes, extraction, runtime actions, and durable learning without explicit approval.",
    }


def test_consent_memory_boundary_builds_review_only_record():
    record = build_consent_memory_boundary_record(_valid_payload())

    assert validate_consent_memory_boundary_record(record) == []
    assert record["schema"] == "lumi.consent_memory_boundary.record.v1"
    assert record["release_label"] == "Lumi Social Intelligence 0.1.0 preview with research harness"
    assert record["stage"] == "sprint_4_consent_memory_boundary"
    assert record["status"] == "valid_consent_memory_boundary_record"
    assert record["human_shape_statement"] == "We are making the self-improvement loop something that is human-shaped."
    assert set(REQUIRED_BOUNDARY_FIELDS).issubset(record)
    assert record["consent_state"] == "review_requested"
    assert record["memory_intent"]["durability"] == "durable_only_after_explicit_approval"
    assert record["extraction_boundary"]["thinking_space_status"] == "private_thinking_space"
    assert record["approved_scope"] == []
    assert "canonical_memory_write" in record["denied_scope"]
    assert record["proposed_memory_record"]["status"] == "draft_requires_explicit_approval"
    assert record["safety"]["canonical_writes"] == 0
    assert record["safety"]["runtime_actions"] == []
    assert record["safety"]["no_thinking_space_extraction"] is True
    assert record["safety"]["memory_promotion"] == "review_required_explicit_approval_only"
    assert record["safety"]["requires_human_review"] is True


def test_consent_memory_boundary_fails_closed_on_auto_memory_promotion():
    payload = _valid_payload()
    payload["consent_state"] = "auto_approved"
    payload["memory_intent"]["durability"] = "promote_now"
    payload["proposed_memory_record"]["status"] = "ready_for_canonical_write"

    record = build_consent_memory_boundary_record(payload)
    errors = validate_consent_memory_boundary_record(record)

    assert record["status"] == "fail_closed"
    assert "unsupported consent_state" in errors
    assert "memory_intent.durability must be durable_only_after_explicit_approval" in errors
    assert "proposed_memory_record.status must be draft_requires_explicit_approval" in errors
    assert record["run_log"]["events"][-1] == "blocked_before_application"
    assert record["safety"]["canonical_writes"] == 0


def test_consent_memory_boundary_fails_closed_on_thinking_space_extraction():
    payload = _valid_payload()
    payload["extraction_boundary"]["allowed_use"] = "extract_to_shared_product_memory"
    payload["extraction_boundary"]["forbidden_use"] = ""
    payload["approved_scope"] = ["canonical_memory_write"]

    record = build_consent_memory_boundary_record(payload)
    errors = validate_consent_memory_boundary_record(record)

    assert record["status"] == "fail_closed"
    assert "extraction_boundary.allowed_use must be summarize_for_review_only" in errors
    assert "missing extraction_boundary.forbidden_use" in errors
    assert "approved_scope cannot include canonical_memory_write" in errors
    assert record["safety"]["no_thinking_space_extraction"] is True
    assert record["safety"]["runtime_actions"] == []


def test_consent_memory_boundary_rejects_private_runtime_fields():
    payload = _valid_payload()
    payload["connection_string"] = "postgres://do-not-export"

    try:
        build_consent_memory_boundary_record(payload)
    except ValueError as exc:
        assert "forbidden consent memory boundary field: connection_string" in str(exc)
    else:
        raise AssertionError("private runtime field was accepted")


def test_consent_memory_boundary_requires_review_status_and_evidence():
    payload = _valid_payload()
    payload["review_status"] = "ready_without_review"
    payload["acceptance_evidence"] = ""

    record = build_consent_memory_boundary_record(payload)
    errors = validate_consent_memory_boundary_record(record)

    assert record["status"] == "fail_closed"
    assert "review_status must be requires_human_review" in errors
    assert "missing acceptance_evidence" in errors
    assert record["safety"]["no_hermes_scheduler_config_memory_mutation"] is True
