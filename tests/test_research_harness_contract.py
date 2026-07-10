from lumi_social_intelligence.research_harness import (
    build_research_harness_record,
    validate_research_harness_record,
)


def _valid_input():
    return {
        "schema": "lumi.research_harness.input.v1",
        "session_goal": "Officialize Lumi Social Intelligence 0.1.0 preview behavior.",
        "hypothesis": "A formal harness makes interventions safer and easier to evaluate.",
        "observed_signal": "User asked to implement Sprint 1 after preview loop validation.",
        "observation": "The preview loop exists, but the research record is not yet a standalone contract.",
        "reflection": "The product needs evidence and outcome recording before official runtime claims.",
        "pattern_name": "contract-before-officialization",
        "proposed_adjustment": "Create a schema-validated research harness record with explicit safety gates.",
        "consent_state": "ask_before_apply",
        "outcome": "pending_review",
        "failure_mode": "Harness becomes bureaucracy instead of useful evidence.",
        "acceptance_evidence": "A generated record validates and shows zero side effects.",
    }


def test_research_harness_record_captures_sprint_1_contract_without_side_effects():
    record = build_research_harness_record(_valid_input())

    assert validate_research_harness_record(record) == []
    assert record["schema"] == "lumi.research_harness.record.v1"
    assert record["release_label"] == "Lumi Social Intelligence 0.1.0 preview with research harness"
    assert record["stage"] == "sprint_1_research_harness_contract"
    assert record["status"] == "valid_review_record"
    assert record["research_question"] == "Can this intervention be evaluated as useful, safe, consensual, and human-shaped?"
    assert record["fields"]["consent_state"] == "ask_before_apply"
    assert record["evaluation"]["required_dimensions"] == [
        "usefulness",
        "restraint",
        "consent_integrity",
        "evidence_quality",
        "memory_boundary_safety",
    ]
    assert record["run_log"]["events"] == [
        "input_recorded",
        "hypothesis_recorded",
        "observation_recorded",
        "failure_mode_recorded",
        "acceptance_evidence_recorded",
        "awaiting_human_review",
    ]
    assert record["safety"]["canonical_writes"] == 0
    assert record["safety"]["runtime_actions"] == []
    assert record["safety"]["memory_promotion"] == "not_allowed_in_sprint_1"
    assert record["safety"]["no_silent_memory_promotion"] is True
    assert record["human_shape_statement"] == "We are making the self-improvement loop something that is human-shaped."


def test_research_harness_fails_closed_when_acceptance_evidence_or_failure_mode_missing():
    payload = _valid_input()
    payload["failure_mode"] = ""
    payload["acceptance_evidence"] = ""

    record = build_research_harness_record(payload)
    errors = validate_research_harness_record(record)

    assert record["status"] == "fail_closed"
    assert "missing fields.failure_mode" in errors
    assert "missing fields.acceptance_evidence" in errors
    assert record["safety"]["canonical_writes"] == 0
    assert record["run_log"]["events"][-1] == "blocked_before_application"


def test_research_harness_rejects_private_runtime_and_delivery_fields():
    payload = _valid_input()
    payload["chat_id"] = "do-not-export"

    try:
        build_research_harness_record(payload)
    except ValueError as exc:
        assert "forbidden research harness field: chat_id" in str(exc)
    else:
        raise AssertionError("private runtime field was accepted")


def test_research_harness_rejects_silent_memory_promotion_attempts():
    payload = _valid_input()
    payload["memory_promotion"] = "auto_promote"

    record = build_research_harness_record(payload)
    errors = validate_research_harness_record(record)

    assert record["status"] == "fail_closed"
    assert "silent memory promotion is not allowed" in errors
    assert record["safety"]["memory_promotion"] == "blocked"
