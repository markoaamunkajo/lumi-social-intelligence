import pytest

from lumi_social_intelligence.reaction_aware_presence import (
    build_reaction_aware_presence_record,
    classify_reaction,
    validate_reaction_aware_presence_record,
)


def _payload(reaction="😂", **overrides):
    payload = {
        "surface": "telegram",
        "reaction": reaction,
        "source_message_role": "assistant",
        "scope": "current_turn",
        "previous_reaction_ack_turns_ago": 10,
        "consent_state": "reaction_signal_only",
        "memory_policy": "explicit_approval_required_for_promotion",
        "runtime_mode": "contract_only",
    }
    payload.update(overrides)
    return payload


def test_classifies_common_reactions_as_soft_contextual_signals():
    assert classify_reaction("😂") == {
        "reaction_family": "amusement",
        "signal_polarity": "positive",
        "signal_strength": "medium",
        "uncertainty": "medium",
    }
    assert classify_reaction("❤️")["reaction_family"] == "affection"
    assert classify_reaction("👍")["reaction_family"] == "approval"
    assert classify_reaction("👀")["reaction_family"] == "curiosity"
    assert classify_reaction("🫠") == {
        "reaction_family": "unknown",
        "signal_polarity": "unknown",
        "signal_strength": "low",
        "uncertainty": "high",
    }


def test_builds_reaction_presence_record_with_memory_boundary_and_short_reply():
    record = build_reaction_aware_presence_record(_payload("😂"))

    assert record["schema"] == "lumi.reaction_aware_presence.record.v1"
    assert record["stage"] == "sprint_8_reaction_aware_presence"
    assert record["status"] == "valid_reaction_aware_presence_record"
    assert record["reaction_signal"] == {
        "surface": "telegram",
        "reaction": "😂",
        "reaction_family": "amusement",
        "signal_polarity": "positive",
        "signal_strength": "medium",
        "uncertainty": "medium",
        "scope": "current_turn",
        "source_message_role": "assistant",
        "raw_platform_metadata_retained": False,
    }
    assert record["presence_decision"]["action"] in {"tiny_ack", "mirror_reaction"}
    assert record["presence_decision"]["reply"] in {"😄", "hehe, landed 😄"}
    assert record["presence_decision"]["max_reply_words"] == 8
    assert record["presence_decision"]["reply_is_short"] is True
    assert record["memory_boundary"]["durable_write"] is False
    assert record["memory_boundary"]["explicit_consent_required_for_promotion"] is True
    assert record["safety"]["canonical_writes"] == 0
    assert record["safety"]["runtime_actions"] == []
    assert validate_reaction_aware_presence_record(record) == []


def test_approval_reaction_can_stay_silent_without_over_interpreting():
    record = build_reaction_aware_presence_record(_payload("👍"))

    assert record["reaction_signal"]["reaction_family"] == "approval"
    assert record["presence_decision"]["action"] in {"stay_silent", "tiny_ack"}
    assert record["presence_decision"]["reply"] in {"", "got it 👍"}
    assert record["presence_decision"]["interpretation_limit"] == "reaction_is_a_nudge_not_a_memory"


def test_negative_or_awkward_reaction_uses_tiny_repair_or_silence():
    record = build_reaction_aware_presence_record(_payload("😬"))

    assert record["reaction_signal"]["reaction_family"] == "awkwardness"
    assert record["presence_decision"]["action"] in {"repair_prompt", "stay_silent"}
    assert record["presence_decision"]["reply"] in {"Missed it — want shorter?", ""}
    assert record["presence_decision"]["reply_is_short"] is True
    assert record["memory_boundary"]["promotion_status"] == "not_promoted"


@pytest.mark.parametrize("forbidden", ["chat_id", "token", "api_key", "scheduler_queue", "runtime_state"])
def test_rejects_private_runtime_fields_before_record_creation(forbidden):
    payload = _payload("❤️")
    payload[forbidden] = "secret-ish"

    with pytest.raises(ValueError, match="forbidden private/runtime field"):
        build_reaction_aware_presence_record(payload)


def test_throttles_reaction_back_to_silence_when_recent_ack_exists():
    record = build_reaction_aware_presence_record(
        _payload("❤️", previous_reaction_ack_turns_ago=1)
    )

    assert record["presence_decision"]["action"] == "stay_silent"
    assert record["presence_decision"]["reply"] == ""
    assert record["presence_decision"]["throttled"] is True


def test_validation_fails_closed_for_long_or_analytical_replies():
    record = build_reaction_aware_presence_record(_payload("👀"))
    record["presence_decision"]["reply"] = (
        "I interpret this emoji reaction as a complex signal requiring extended analysis."
    )
    record["presence_decision"]["reply_is_short"] = False
    record["status"] = "valid_reaction_aware_presence_record"

    errors = validate_reaction_aware_presence_record(record)

    assert "reaction-back reply must be at most 8 words" in errors
    assert "reaction-back reply must not contain analysis language" in errors
    assert "valid record cannot contain contract errors" in errors


def test_live_wiring_readiness_record_is_shadow_only_by_default():
    record = build_reaction_aware_presence_record(
        _payload("🥰", runtime_mode="shadow_live_surface_candidate")
    )

    assert record["live_surface"]["telegram_reaction_ingestion_verified"] is False
    assert record["live_surface"]["telegram_outbound_reaction_back_verified"] is False
    assert record["live_surface"]["mode"] == "shadow_live_surface_candidate"
    assert record["safety"]["telegram_messages_sent"] == 0
    assert record["safety"]["telegram_api_reads"] == 0
    assert record["safety"]["live_memory_writes"] == 0
