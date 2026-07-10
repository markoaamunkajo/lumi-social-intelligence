from lumi_social_intelligence.official_packaging_release_notes import (
    REQUIRED_PACKAGING_FIELDS,
    REQUIRED_RELEASE_NOTE_SECTIONS,
    build_official_packaging_record,
    validate_official_packaging_record,
)


def _valid_payload():
    return {
        "schema": "lumi.official_packaging.input.v1",
        "session_goal": "Reconcile the existing technical v0.1.0 release with official product-readiness packaging.",
        "technical_release": {
            "tag": "v0.1.0",
            "status": "existing_public_technical_release",
            "url": "https://github.com/markoaamunkajo/lumi-social-intelligence/releases/tag/v0.1.0",
        },
        "product_release": {
            "version": "0.1.0",
            "status": "official_packaging_candidate",
            "positioning": "preview_with_research_harness_and_review_only_governance",
        },
        "officialization_evidence": [
            "sprint_1_research_harness_contract_passed",
            "sprint_2_preview_loop_protocol_passed",
            "sprint_3_signal_reflection_schema_passed",
            "sprint_4_consent_memory_boundary_passed",
            "sprint_5_evaluation_acceptance_criteria_passed",
            "release_check_passed",
        ],
        "release_note_sections": [
            "technical_release_exists",
            "product_readiness_delta",
            "officialization_sprints",
            "safety_boundaries",
            "verification_evidence",
            "not_included",
            "human_review_next_step",
        ],
        "packaging_decision": {
            "status": "ready_for_human_release_note_review",
            "allowed_action": "draft_official_0_1_0_release_notes",
            "blocked_action": "publish_without_human_review",
        },
        "review_status": "requires_human_review",
        "acceptance_evidence": "Packaging separates existing technical release from official product-readiness notes and keeps publication review-gated.",
    }


def test_official_packaging_builds_review_only_record():
    record = build_official_packaging_record(_valid_payload())

    assert validate_official_packaging_record(record) == []
    assert record["schema"] == "lumi.official_packaging.record.v1"
    assert record["release_label"] == "Lumi Social Intelligence 0.1.0 preview with research harness"
    assert record["stage"] == "sprint_6_official_packaging_release_notes"
    assert record["status"] == "valid_official_packaging_record"
    assert record["human_shape_statement"] == "We are making the self-improvement loop something that is human-shaped."
    assert set(REQUIRED_PACKAGING_FIELDS).issubset(record)
    assert set(REQUIRED_RELEASE_NOTE_SECTIONS).issubset(record["release_note_sections"])
    assert record["technical_release"]["status"] == "existing_public_technical_release"
    assert record["product_release"]["status"] == "official_packaging_candidate"
    assert record["packaging_decision"]["allowed_action"] == "draft_official_0_1_0_release_notes"
    assert record["safety"]["canonical_writes"] == 0
    assert record["safety"]["runtime_actions"] == []
    assert record["safety"]["no_publish_without_human_review"] is True


def test_official_packaging_fails_closed_if_technical_and_product_release_are_blurred():
    payload = _valid_payload()
    payload["technical_release"]["status"] = "official_product_release"
    payload["product_release"]["status"] = "already_published"

    record = build_official_packaging_record(payload)
    errors = validate_official_packaging_record(record)

    assert record["status"] == "fail_closed"
    assert "technical_release.status must be existing_public_technical_release" in errors
    assert "product_release.status must be official_packaging_candidate" in errors
    assert record["run_log"]["events"][-1] == "blocked_before_publication"


def test_official_packaging_requires_all_prior_sprint_evidence_and_release_check():
    payload = _valid_payload()
    payload["officialization_evidence"] = payload["officialization_evidence"][:-2]

    record = build_official_packaging_record(payload)
    errors = validate_official_packaging_record(record)

    assert record["status"] == "fail_closed"
    assert "officialization_evidence must include sprint_5_evaluation_acceptance_criteria_passed" in errors
    assert "officialization_evidence must include release_check_passed" in errors


def test_official_packaging_requires_release_note_sections_and_review_gate():
    payload = _valid_payload()
    payload["release_note_sections"].remove("not_included")
    payload["packaging_decision"]["allowed_action"] = "publish_release_now"
    payload["review_status"] = "approved_without_review"

    record = build_official_packaging_record(payload)
    errors = validate_official_packaging_record(record)

    assert record["status"] == "fail_closed"
    assert "release_note_sections must include not_included" in errors
    assert "packaging_decision.allowed_action must be draft_official_0_1_0_release_notes" in errors
    assert "review_status must be requires_human_review" in errors
    assert record["safety"]["requires_human_review"] is True


def test_official_packaging_rejects_private_runtime_fields():
    payload = _valid_payload()
    payload["chat_id"] = "do-not-export"

    try:
        build_official_packaging_record(payload)
    except ValueError as exc:
        assert "forbidden official packaging field: chat_id" in str(exc)
    else:
        raise AssertionError("private runtime field was accepted")
