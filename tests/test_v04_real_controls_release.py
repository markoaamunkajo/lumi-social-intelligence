import json
import subprocess
import sys
from pathlib import Path

from lumi_social_intelligence.live_surface_controls import apply_review_gated_control

ROOT = Path(__file__).resolve().parents[1]


def test_review_gated_control_is_real_public_capability_not_shadow_only():
    card = apply_review_gated_control(
        "Keep the rain context warm for when I leave, but don't surface unless relevant",
        now="2026-07-11T18:00:00+07:00",
        source="public_review_gated_surface",
    )

    assert card["schema"] == "lumi.live_surface.review_gated_control.v1"
    assert card["mode"] == "review_gated"
    assert card["shadow_only"] is False
    assert card["claim_boundary"] == "review-gated public Live Surface control; no autonomous external automation"
    assert card["review_card"]["decision"] == "ready_for_review"
    assert card["review_card"]["applyable_by_public_api"] is True
    assert card["review_card"]["requires_private_runtime"] is False
    assert card["state"]["intent"] == "keep_fresh"
    assert card["state"]["refresh_policy"] == "safe_readiness_only"
    assert card["state"]["surfacing_policy"] == "presence_gated"
    assert card["state"]["side_effects"] == card["side_effects"]
    assert all(value == 0 for value in card["side_effects"].values())


def test_missing_calendar_surface_fails_closed_with_exact_add_surface_response():
    card = apply_review_gated_control(
        "check whether I am free tomorrow from my calendar",
        now="2026-07-11T18:00:00+07:00",
        source="public_review_gated_surface",
        available_surfaces=("conversation", "weather"),
    )

    assert card["mode"] == "review_gated"
    assert card["shadow_only"] is False
    assert card["state"]["status"] == "pending_review"
    assert "personal_data_read_blocked" in card["state"]["safety_flags"]
    assert card["ack"] == "Calendar doesn't yet exist on Live Surface, would you like to add it?"
    assert card["review_card"]["decision"] == "blocked_missing_surface"
    assert card["review_card"]["missing_surface"] == "calendar"
    assert card["side_effects"]["calendar_reads_without_surface"] == 0
    assert card["side_effects"]["personal_data_reads"] == 0


def test_v04_evidence_builder_writes_public_safe_real_controls_receipt(tmp_path):
    evidence = tmp_path / "v0.4.0-real-controls-evidence.json"
    markdown = tmp_path / "v0.4.0-real-controls-evidence.md"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_v04_real_controls_evidence.py",
            "--evidence",
            str(evidence),
            "--markdown",
            str(markdown),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    report = json.loads(result.stdout)
    receipt = json.loads(evidence.read_text(encoding="utf-8"))
    md = markdown.read_text(encoding="utf-8")

    assert report["status"] == "verified"
    assert receipt["schema"] == "lumi.v04.real_controls_evidence.v1"
    assert receipt["status"] == "verified"
    assert receipt["version"] == "0.4.0"
    assert receipt["mode"] == "review_gated"
    assert receipt["shadow_only"] is False
    assert receipt["canonical_writes"] == 0
    assert receipt["external_writes"] == 0
    assert receipt["private_runtime_reads"] == 0
    assert receipt["scheduler_mutations"] == 0
    assert receipt["claim_boundary"] == "real review-gated public capability; not autonomous private runtime automation"
    assert receipt["scenarios"]["safe_readiness"]["review_card"]["applyable_by_public_api"] is True
    assert receipt["scenarios"]["missing_calendar"]["ack"] == "Calendar doesn't yet exist on Live Surface, would you like to add it?"
    assert "shadow-only" not in md.lower()
    assert "review-gated public capability" in md
