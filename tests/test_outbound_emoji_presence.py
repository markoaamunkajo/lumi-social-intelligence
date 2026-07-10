import pytest

from lumi_social_intelligence.outbound_emoji_presence import (
    ALLOWED_OUTBOUND_REACTIONS,
    build_outbound_emoji_presence_record,
    validate_outbound_emoji_presence_record,
)


def _payload(**overrides):
    payload = {
        "surface": "telegram",
        "candidate_reaction": "❤️",
        "target_message_role": "user",
        "why_now": "user shared warm affect and a tiny presence signal fits better than text",
        "previous_outbound_reaction_turns_ago": 10,
        "platform_delivery_verified": False,
        "runtime_mode": "contract_only",
    }
    payload.update(overrides)
    return payload


def test_builds_shadow_only_outbound_emoji_presence_record():
    record = build_outbound_emoji_presence_record(_payload(candidate_reaction="❤️"))

    assert record["schema"] == "lumi.outbound_emoji_presence.record.v1"
    assert record["stage"] == "sprint_9_outbound_emoji_presence"
    assert record["status"] == "valid_outbound_emoji_presence_record"
    assert record["presence_intent"]["gesture"] == "add_emoji_reaction"
    assert record["emoji_choice"]["emoji"] == "❤️"
    assert record["emoji_choice"]["emoji"] in ALLOWED_OUTBOUND_REACTIONS
    assert record["emoji_choice"]["text_reply"] == ""
    assert record["emoji_choice"]["max_text_words"] == 0
    assert record["delivery_boundary"]["delivery_mode"] == "shadow_only"
    assert record["delivery_boundary"]["platform_delivery_verified"] is False
    assert record["delivery_boundary"]["safe_to_claim_live_delivery"] is False
    assert record["memory_boundary"]["durable_write"] is False
    assert record["safety"]["canonical_writes"] == 0
    assert record["safety"]["runtime_actions"] == []
    assert record["safety"]["telegram_messages_sent"] == 0
    assert record["safety"]["telegram_reactions_sent"] == 0
    assert validate_outbound_emoji_presence_record(record) == []


@pytest.mark.parametrize("emoji", ["❤️", "😄", "👍", "👀", "✨"])
def test_allows_only_tiny_approved_reaction_palette(emoji):
    record = build_outbound_emoji_presence_record(_payload(candidate_reaction=emoji))

    assert record["emoji_choice"]["emoji"] == emoji
    assert record["emoji_choice"]["allowed_palette"] == sorted(ALLOWED_OUTBOUND_REACTIONS)
    assert record["emoji_choice"]["text_reply"] == ""


@pytest.mark.parametrize("emoji", ["💍", "😈", "🤯", "this is not tiny"])
def test_unapproved_or_non_emoji_choice_fails_closed_to_silence(emoji):
    record = build_outbound_emoji_presence_record(_payload(candidate_reaction=emoji))

    assert record["presence_intent"]["gesture"] == "stay_silent"
    assert record["emoji_choice"]["emoji"] == ""
    assert record["status"] == "fail_closed"
    assert "candidate reaction is outside approved tiny palette" in record["safety"]["blocked_reasons"]


def test_throttles_repeated_outbound_reactions_to_silence():
    record = build_outbound_emoji_presence_record(
        _payload(candidate_reaction="😄", previous_outbound_reaction_turns_ago=1)
    )

    assert record["presence_intent"]["gesture"] == "stay_silent"
    assert record["emoji_choice"]["emoji"] == ""
    assert record["throttle"]["throttled"] is True
    assert record["safety"]["telegram_reactions_sent"] == 0


def test_blocks_outbound_reaction_to_assistant_or_unknown_target_message():
    record = build_outbound_emoji_presence_record(
        _payload(candidate_reaction="👀", target_message_role="assistant")
    )

    assert record["presence_intent"]["gesture"] == "stay_silent"
    assert record["emoji_choice"]["emoji"] == ""
    assert "target message must be user-authored" in record["safety"]["blocked_reasons"]


def test_rejects_private_runtime_fields_before_record_creation():
    payload = _payload(candidate_reaction="👍")
    payload["chat_id"] = "do-not-export"

    with pytest.raises(ValueError, match="forbidden private/runtime field"):
        build_outbound_emoji_presence_record(payload)


def test_validation_rejects_texty_or_live_claiming_records():
    record = build_outbound_emoji_presence_record(_payload(candidate_reaction="✨"))
    record["emoji_choice"]["text_reply"] = "this should never be paragraph cosplay"
    record["delivery_boundary"]["safe_to_claim_live_delivery"] = True
    record["safety"]["telegram_reactions_sent"] = 1
    record["status"] = "valid_outbound_emoji_presence_record"

    errors = validate_outbound_emoji_presence_record(record)

    assert "outbound emoji presence must not include a text reply" in errors
    assert "live delivery cannot be claimed by this contract" in errors
    assert "telegram_reactions_sent must be 0" in errors
    assert "valid record cannot contain contract errors" in errors
