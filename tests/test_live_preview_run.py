from lumi_social_intelligence.live_preview_run import (
    PREVIEW_RUN_STEPS,
    build_live_preview_run_record,
    validate_live_preview_run_record,
)


def _valid_payload():
    return {
        "session_goal": "Run a review-only Lumi preview loop against this chat interaction.",
        "conversation_context": "Marko is ready to exercise the preview loop after Sprint 6 packaging.",
        "observed_signal": "User offers a gentle go-ahead without asking for live automation.",
        "reflection": "The appropriate next move is a small, explicit, review-only run record.",
        "named_pattern": "soft_consent_to_begin_sprint_7_preview",
        "suggested_adjustment": "Use the preview loop in chat and keep any durable learning gated.",
        "consent_checkpoint": "ask_consent",
        "approval_state": "draft_only",
        "applied_small_change": "Prepared a review card and no runtime side effects.",
        "learning_record_policy": "record_only_if_approved",
        "human_review_summary": "Review the signal/reflection/adjustment before any memory or product learning.",
    }


def test_builds_review_only_live_preview_record_for_this_chat():
    record = build_live_preview_run_record(_valid_payload())

    assert record["schema"] == "lumi.live_preview_run.record.v1"
    assert record["stage"] == "sprint_7_live_preview_run"
    assert record["status"] == "valid_live_preview_run_record"
    assert record["preview_run"]["surface"] == "this_chat_review_only"
    assert [event["step"] for event in record["step_events"]] == PREVIEW_RUN_STEPS
    assert record["review_card"]["requires_human_review"] is True
    assert record["review_card"]["durable_learning_allowed"] is False
    assert record["safety"]["canonical_writes"] == 0
    assert record["safety"]["runtime_actions"] == []
    assert record["safety"]["no_telegram_wiring"] is True
    assert record["safety"]["no_hermes_scheduler_config_memory_mutation"] is True
    assert validate_live_preview_run_record(record) == []


def test_requires_exact_preview_step_order_and_human_review():
    payload = _valid_payload()
    payload["steps"] = ["observe", "reflect", "ask_consent"]

    record = build_live_preview_run_record(payload)

    assert record["status"] == "fail_closed"
    errors = validate_live_preview_run_record(record)
    assert "step_events must follow exact live preview order" in errors
    assert "blocked_before_learning_or_runtime_action" in record["run_log"]["events"]


def test_blocks_silent_memory_or_runtime_claims():
    payload = _valid_payload()
    payload["approval_state"] = "approved"
    payload["learning_record_policy"] = "record_automatically"
    payload["runtime_actions"] = ["send_telegram_message"]

    record = build_live_preview_run_record(payload)

    assert record["status"] == "fail_closed"
    errors = validate_live_preview_run_record(record)
    assert "learning_record_policy must be record_only_if_approved" in errors
    assert "runtime_actions must stay empty" in errors
    assert record["review_card"]["durable_learning_allowed"] is False


def test_rejects_private_runtime_fields_before_record_creation():
    payload = _valid_payload()
    payload["chat_id"] = "12345"

    try:
        build_live_preview_run_record(payload)
    except ValueError as exc:
        assert "forbidden private/runtime field" in str(exc)
    else:
        raise AssertionError("expected forbidden chat_id to be rejected")


def test_review_card_names_observation_reflection_adjustment_and_consent():
    record = build_live_preview_run_record(_valid_payload())
    card = record["review_card"]

    assert card["observed_signal"] == _valid_payload()["observed_signal"]
    assert card["reflection"] == _valid_payload()["reflection"]
    assert card["named_pattern"] == "soft_consent_to_begin_sprint_7_preview"
    assert card["suggested_adjustment"] == _valid_payload()["suggested_adjustment"]
    assert card["consent_checkpoint"] == "ask_consent"
    assert card["approval_state"] == "draft_only"
    assert card["apply_small_change_status"] == "drafted_review_card_only"
