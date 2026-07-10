from lumi_social_intelligence.preview_loop_protocol import (
    PREVIEW_LOOP_STEPS,
    build_preview_loop_protocol_run,
    validate_preview_loop_protocol_run,
)


VALID_STEP_PAYLOADS = [
    {
        "step": "observe",
        "input": "User confirms Sprint 2 should begin.",
        "output": "The conversation is moving from research harness contract to loop protocol.",
        "consent_state": "not_required_yet",
    },
    {
        "step": "reflect",
        "input": "The loop needs to be useful without becoming card bureaucracy.",
        "output": "The protocol should make state and consent visible while staying lightweight.",
        "consent_state": "not_required_yet",
    },
    {
        "step": "name_pattern",
        "input": "Preview loops can over-speak if every observation becomes a card.",
        "output": "quiet-protocol-before-runtime",
        "consent_state": "not_required_yet",
    },
    {
        "step": "suggest_adjustment",
        "input": "Define a minimal protocol record and transition gates.",
        "output": "Only ask for approval when a small change would affect the current chat behavior.",
        "consent_state": "not_required_yet",
    },
    {
        "step": "ask_consent",
        "input": "Approve this small adjustment, revise it, or leave it as a draft?",
        "output": "User approval is required before applying the suggested adjustment.",
        "consent_state": "asked",
    },
    {
        "step": "apply_small_change",
        "input": "Use the lightweight protocol only for meaningful Lumi interventions.",
        "output": "The adjustment is applied to this preview artifact only.",
        "consent_state": "approved",
    },
    {
        "step": "record_learning_only_if_approved",
        "input": "The protocol should remain review-only unless explicitly approved.",
        "output": "Learning is recorded as review evidence, not durable memory.",
        "consent_state": "approved",
    },
]


def _valid_payload():
    return {
        "schema": "lumi.preview_loop_protocol.input.v1",
        "session_goal": "Officialize the Lumi 0.1.0 preview loop protocol.",
        "steps": [dict(step) for step in VALID_STEP_PAYLOADS],
        "current_state": "record_learning_only_if_approved",
        "proposed_adjustment": "Use a visible step protocol for meaningful preview interventions only.",
        "consent_checkpoint": "ask_consent",
        "approval_state": "approved",
        "learning_record_policy": "record_only_if_approved",
    }


def test_preview_loop_protocol_defines_exact_order_and_review_only_safety():
    run = build_preview_loop_protocol_run(_valid_payload())

    assert validate_preview_loop_protocol_run(run) == []
    assert run["schema"] == "lumi.preview_loop_protocol.run.v1"
    assert run["release_label"] == "Lumi Social Intelligence 0.1.0 preview with research harness"
    assert run["stage"] == "sprint_2_preview_loop_protocol"
    assert run["status"] == "valid_protocol_run"
    assert run["human_shape_statement"] == "We are making the self-improvement loop something that is human-shaped."
    assert run["protocol"]["steps"] == PREVIEW_LOOP_STEPS
    assert [event["step"] for event in run["step_events"]] == PREVIEW_LOOP_STEPS
    assert run["protocol"]["transition_rule"] == "strict_order_no_skips"
    assert run["protocol"]["consent_checkpoint"] == "ask_consent"
    assert run["protocol"]["learning_record_policy"] == "record_only_if_approved"
    assert run["safety"]["canonical_writes"] == 0
    assert run["safety"]["runtime_actions"] == []
    assert run["safety"]["memory_promotion"] == "review_required_explicit_approval_only"
    assert run["safety"]["no_telegram_wiring"] is True
    assert run["safety"]["no_hermes_scheduler_config_memory_mutation"] is True


def test_preview_loop_protocol_fails_closed_when_steps_are_out_of_order():
    payload = _valid_payload()
    payload["steps"][4], payload["steps"][5] = payload["steps"][5], payload["steps"][4]

    run = build_preview_loop_protocol_run(payload)
    errors = validate_preview_loop_protocol_run(run)

    assert run["status"] == "fail_closed"
    assert "protocol steps must follow exact preview loop order" in errors
    assert run["safety"]["canonical_writes"] == 0
    assert run["run_log"]["events"][-1] == "blocked_before_application"


def test_preview_loop_protocol_blocks_apply_before_consent():
    payload = _valid_payload()
    payload["steps"][5]["consent_state"] = "asked"
    payload["approval_state"] = "asked"

    run = build_preview_loop_protocol_run(payload)
    errors = validate_preview_loop_protocol_run(run)

    assert run["status"] == "fail_closed"
    assert "apply_small_change requires approved consent" in errors
    assert "record_learning_only_if_approved requires approved consent" in errors
    assert run["safety"]["runtime_actions"] == []


def test_preview_loop_protocol_rejects_private_runtime_fields():
    payload = _valid_payload()
    payload["scheduler_queue"] = "do-not-export"

    try:
        build_preview_loop_protocol_run(payload)
    except ValueError as exc:
        assert "forbidden preview protocol field: scheduler_queue" in str(exc)
    else:
        raise AssertionError("private runtime field was accepted")
