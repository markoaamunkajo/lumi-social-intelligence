from lumi_social_intelligence.evaluation_acceptance_criteria import (
    REQUIRED_ACCEPTANCE_FIELDS,
    REQUIRED_EVALUATION_DIMENSIONS,
    build_evaluation_acceptance_record,
    validate_evaluation_acceptance_record,
)


def _valid_payload():
    return {
        "schema": "lumi.evaluation_acceptance.input.v1",
        "session_goal": "Define what good enough for official 0.1.0 means before packaging.",
        "candidate_version": "0.1.0-product-candidate",
        "evaluation_dimensions": [
            {
                "name": "research_harness_contract",
                "required_status": "pass",
                "evidence": "Research harness records fail closed and require review evidence.",
            },
            {
                "name": "preview_loop_protocol",
                "required_status": "pass",
                "evidence": "Preview loop steps are ordered and consent-gated.",
            },
            {
                "name": "signal_reflection_schema",
                "required_status": "pass",
                "evidence": "Observed signals remain separate from reflection and confidence.",
            },
            {
                "name": "consent_memory_boundary",
                "required_status": "pass",
                "evidence": "Possible memory remains draft-only until explicit approval.",
            },
            {
                "name": "public_release_safety",
                "required_status": "pass",
                "evidence": "Release gate and public/secret scan must pass.",
            },
        ],
        "acceptance_checks": [
            "focused_tests_pass",
            "combined_officialization_tests_pass",
            "release_check_passes",
            "public_secret_scan_passes",
            "clean_checkout_smoke_passes",
        ],
        "minimum_evidence": {
            "focused_tests": "pytest tests/test_evaluation_acceptance_criteria.py -q",
            "combined_tests": "pytest tests/test_evaluation_acceptance_criteria.py tests/test_consent_memory_boundary.py tests/test_signal_reflection_schema.py tests/test_preview_loop_protocol.py tests/test_research_harness_contract.py tests/test_lumi_for_hermes_adapter.py -q",
            "release_gate": "./scripts/release_check.sh",
        },
        "decision": {
            "status": "candidate_under_review",
            "allowed_next_step": "official_0_1_0_packaging_review",
            "blocked_until": "all_acceptance_checks_pass_with_evidence",
        },
        "review_status": "requires_human_review",
        "acceptance_evidence": "Defines measurable gates before official 0.1.0 packaging without runtime writes.",
    }


def test_evaluation_acceptance_builds_review_only_record():
    record = build_evaluation_acceptance_record(_valid_payload())

    assert validate_evaluation_acceptance_record(record) == []
    assert record["schema"] == "lumi.evaluation_acceptance.record.v1"
    assert record["release_label"] == "Lumi Social Intelligence 0.1.0 preview with research harness"
    assert record["stage"] == "sprint_5_evaluation_acceptance_criteria"
    assert record["status"] == "valid_evaluation_acceptance_record"
    assert record["human_shape_statement"] == "We are making the self-improvement loop something that is human-shaped."
    assert set(REQUIRED_ACCEPTANCE_FIELDS).issubset(record)
    assert {dimension["name"] for dimension in record["evaluation_dimensions"]} == set(
        REQUIRED_EVALUATION_DIMENSIONS
    )
    assert record["decision"]["status"] == "candidate_under_review"
    assert record["decision"]["allowed_next_step"] == "official_0_1_0_packaging_review"
    assert record["safety"]["canonical_writes"] == 0
    assert record["safety"]["runtime_actions"] == []
    assert record["safety"]["requires_human_review"] is True


def test_evaluation_acceptance_fails_closed_on_missing_required_dimension():
    payload = _valid_payload()
    payload["evaluation_dimensions"] = payload["evaluation_dimensions"][:-1]

    record = build_evaluation_acceptance_record(payload)
    errors = validate_evaluation_acceptance_record(record)

    assert record["status"] == "fail_closed"
    assert "missing evaluation dimension: public_release_safety" in errors
    assert record["run_log"]["events"][-1] == "blocked_before_official_packaging"


def test_evaluation_acceptance_fails_closed_on_unmeasured_or_failed_dimension():
    payload = _valid_payload()
    payload["evaluation_dimensions"][0]["required_status"] = "warn"
    payload["evaluation_dimensions"][1]["evidence"] = ""

    record = build_evaluation_acceptance_record(payload)
    errors = validate_evaluation_acceptance_record(record)

    assert record["status"] == "fail_closed"
    assert "evaluation dimension research_harness_contract must require pass" in errors
    assert "evaluation dimension preview_loop_protocol missing evidence" in errors


def test_evaluation_acceptance_fails_closed_until_release_gates_are_explicit():
    payload = _valid_payload()
    payload["acceptance_checks"].remove("release_check_passes")
    payload["minimum_evidence"]["release_gate"] = ""
    payload["decision"]["allowed_next_step"] = "ship_now"

    record = build_evaluation_acceptance_record(payload)
    errors = validate_evaluation_acceptance_record(record)

    assert record["status"] == "fail_closed"
    assert "acceptance_checks must include release_check_passes" in errors
    assert "missing minimum_evidence.release_gate" in errors
    assert "decision.allowed_next_step must be official_0_1_0_packaging_review" in errors
    assert record["safety"]["no_official_release_without_evidence"] is True


def test_evaluation_acceptance_rejects_private_runtime_fields():
    payload = _valid_payload()
    payload["token"] = "do-not-export"

    try:
        build_evaluation_acceptance_record(payload)
    except ValueError as exc:
        assert "forbidden evaluation acceptance field: token" in str(exc)
    else:
        raise AssertionError("private runtime field was accepted")
