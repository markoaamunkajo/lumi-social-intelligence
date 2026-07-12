from lumi_social_intelligence.care_release import build_live_surface_autoresearch_readiness_plan


def test_v043_autoresearch_readiness_is_gateway_start_ready_without_first_use_warmup():
    plan = build_live_surface_autoresearch_readiness_plan(
        now="2026-07-12T09:00:00+07:00",
        source="telegram",
        context={"autoresearch_small_investigation_ready": True},
    )

    assert plan["schema"] == "lumi.v043.live_surface_autoresearch_readiness.v1"
    assert plan["version"] == "0.4.3"
    assert plan["status"] == "ready"
    readiness = plan["gateway_startup_readiness"]
    assert readiness["contract"] == "all_live_surface_tools_ready_after_gateway_start"
    assert readiness["startup_phase"] == "gateway_start"
    assert readiness["first_user_need_warmup_allowed"] is False
    assert readiness["autoresearch_small_investigation_ready"] is True


def test_v043_autoresearch_acknowledges_before_longer_tool_path_and_stays_review_gated():
    plan = build_live_surface_autoresearch_readiness_plan(
        now="2026-07-12T09:00:00+07:00",
        source="telegram",
    )

    ack = plan["pre_tool_acknowledgement"]
    assert ack["required_before_longer_tool_path"] is True
    assert "checking the small AutoResearch route" in ack["example"]
    assert "then I’ll give you" in ack["example"]
    assert ack["visible_latency_contract"] == "no_silent_long_wait"

    gate = plan["review_gate"]
    assert gate["readiness_is_not_permission"] is True
    assert gate["permission_expansion_allowed"] is False
    assert gate["durable_memory_write_allowed"] is False
    assert gate["runtime_promotion_allowed_by_public_repo"] is False
    assert plan["side_effects"] == {
        "telegram_messages_sent_by_public_repo": 0,
        "telegram_reactions_sent_by_public_repo": 0,
        "private_runtime_reads_by_public_repo": 0,
        "runtime_mutations_by_public_repo": 0,
    }


def test_v043_autoresearch_not_warmed_fails_closed():
    plan = build_live_surface_autoresearch_readiness_plan(
        now="2026-07-12T09:00:00+07:00",
        source="telegram",
        context={"autoresearch_small_investigation_ready": False},
    )

    assert plan["status"] == "blocked_not_warmed"
    assert plan["gateway_startup_readiness"]["autoresearch_small_investigation_ready"] is False
    assert plan["review_gate"]["runtime_promotion_allowed_by_public_repo"] is False
