from lumi_social_intelligence.signal_reflection_schema import (
    REQUIRED_SIGNAL_FIELDS,
    REQUIRED_REFLECTION_FIELDS,
    build_signal_reflection_record,
    validate_signal_reflection_record,
)


def _valid_payload():
    return {
        "schema": "lumi.signal_reflection.input.v1",
        "session_goal": "Make the Lumi preview loop evaluable without hidden learning.",
        "observed_signal": {
            "source": "current_chat",
            "type": "consent_signal",
            "description": "User explicitly asked to continue to the next sprint.",
            "evidence": "Let's go next sprint",
            "strength": "strong",
            "uncertainty": "low",
        },
        "reflection": {
            "interpretation": "The user wants Sprint 3 implementation, not more planning prose.",
            "confidence": "high",
            "contradictions": [],
            "risk": "low",
            "boundary": "review_only_not_runtime",
        },
        "proposed_adjustment": {
            "name": "signal-reflection-before-learning",
            "description": "Separate observed signal from reflection before any future learning record.",
            "scope": "preview_review_artifact_only",
        },
        "consent": {
            "state": "draft_only",
            "checkpoint": "ask_before_apply",
            "required_before": "apply_small_change",
        },
        "acceptance_evidence": "The record validates signal, reflection, contradiction, confidence, consent, and no-side-effect boundaries.",
    }


def test_signal_reflection_schema_builds_review_only_record():
    record = build_signal_reflection_record(_valid_payload())

    assert validate_signal_reflection_record(record) == []
    assert record["schema"] == "lumi.signal_reflection.record.v1"
    assert record["release_label"] == "Lumi Social Intelligence 0.1.0 preview with research harness"
    assert record["stage"] == "sprint_3_signal_reflection_schema"
    assert record["status"] == "valid_signal_reflection_record"
    assert record["human_shape_statement"] == "We are making the self-improvement loop something that is human-shaped."
    assert set(REQUIRED_SIGNAL_FIELDS).issubset(record["observed_signal"])
    assert set(REQUIRED_REFLECTION_FIELDS).issubset(record["reflection"])
    assert record["observed_signal"]["type"] == "consent_signal"
    assert record["reflection"]["confidence"] == "high"
    assert record["reflection"]["contradictions"] == []
    assert record["proposed_adjustment"]["scope"] == "preview_review_artifact_only"
    assert record["consent"]["checkpoint"] == "ask_before_apply"
    assert record["safety"]["canonical_writes"] == 0
    assert record["safety"]["runtime_actions"] == []
    assert record["safety"]["memory_promotion"] == "review_required_explicit_approval_only"
    assert record["safety"]["no_silent_memory_promotion"] is True


def test_signal_reflection_schema_fails_closed_without_evidence_or_confidence():
    payload = _valid_payload()
    payload["observed_signal"]["evidence"] = ""
    payload["reflection"]["confidence"] = ""

    record = build_signal_reflection_record(payload)
    errors = validate_signal_reflection_record(record)

    assert record["status"] == "fail_closed"
    assert "missing observed_signal.evidence" in errors
    assert "missing reflection.confidence" in errors
    assert record["run_log"]["events"][-1] == "blocked_before_application"
    assert record["safety"]["canonical_writes"] == 0


def test_signal_reflection_schema_rejects_unsupported_confidence_and_consent():
    payload = _valid_payload()
    payload["reflection"]["confidence"] = "certain_forever"
    payload["consent"]["state"] = "silently_apply"

    record = build_signal_reflection_record(payload)
    errors = validate_signal_reflection_record(record)

    assert record["status"] == "fail_closed"
    assert "unsupported reflection.confidence" in errors
    assert "unsupported consent.state" in errors
    assert record["safety"]["runtime_actions"] == []


def test_signal_reflection_schema_rejects_private_runtime_fields():
    payload = _valid_payload()
    payload["chat_id"] = "do-not-export"

    try:
        build_signal_reflection_record(payload)
    except ValueError as exc:
        assert "forbidden signal reflection field: chat_id" in str(exc)
    else:
        raise AssertionError("private runtime field was accepted")


def test_signal_reflection_schema_blocks_silent_memory_promotion():
    payload = _valid_payload()
    payload["memory_promotion"] = "promote_to_durable_memory"

    record = build_signal_reflection_record(payload)
    errors = validate_signal_reflection_record(record)

    assert record["status"] == "fail_closed"
    assert "silent memory promotion is not allowed" in errors
    assert record["safety"]["memory_promotion"] == "blocked"
    assert record["safety"]["no_silent_memory_promotion"] is True
