import json
import subprocess
import sys
from pathlib import Path

import pytest

from adapters.hermes.lumi_for_hermes import (
    build_preview_loop_card,
    build_reaction_presence_card,
    build_review_card,
)

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / 'installers' / 'lumi-for-hermes' / 'preview.py'


def test_review_card_connects_memory_nuance_presence_without_side_effects():
    card = build_review_card({
        'schema': 'lumi.hermes.adapter_input.v1',
        'mode': 'dry_run',
        'memory_context': {
            'provider': 'hermes-memory',
            'source_id': 'synthetic://memory/context/1',
            'text': 'Marko prefers short factual recovery notes after continuity scares.',
            'confidence': 0.91,
        },
        'nuance_appraisal': {
            'why_now': 'continuity concern needs calm acknowledgement',
            'grounded': True,
            'confidence': 0.84,
        },
        'requested_effect': 'review_card',
    })

    assert card['schema'] == 'lumi.hermes.review_card.v1'
    assert card['mode'] == 'dry_run'
    assert card['decision']['move'] == 'speak'
    assert card['decision']['side_effect_allowed'] is False
    assert card['safety']['canonical_writes'] == 0
    assert card['safety']['runtime_actions'] == []
    assert card['safety']['requires_human_review'] is True
    assert card['memory']['source']['source_id'] == 'synthetic://memory/context/1'
    assert card['nuance']['why_now'] == 'continuity concern needs calm acknowledgement'


def test_adapter_fails_closed_when_grounding_or_confidence_is_missing():
    card = build_review_card({
        'schema': 'lumi.hermes.adapter_input.v1',
        'mode': 'review_gated',
        'memory_context': {
            'provider': 'hermes-memory',
            'source_id': 'synthetic://memory/context/low-confidence',
            'text': 'Maybe maybe maybe.',
            'confidence': 0.4,
        },
        'nuance_appraisal': {
            'why_now': '',
            'grounded': False,
            'confidence': 0.2,
        },
    })

    assert card['decision']['move'] == 'hold'
    assert card['status'] == 'fail_closed'
    assert card['safety']['canonical_writes'] == 0
    assert 'insufficient' in card['safety']['blocked_reasons']


@pytest.mark.parametrize('forbidden', ['chat_id', 'job_id', 'scheduler_queue', 'runtime_state'])
def test_adapter_rejects_private_hermes_runtime_fields(forbidden):
    with pytest.raises(ValueError, match=forbidden):
        build_review_card({
            'schema': 'lumi.hermes.adapter_input.v1',
            'mode': 'dry_run',
            forbidden: 'do-not-export',
            'memory_context': {
                'provider': 'hermes-memory',
                'source_id': 'synthetic://memory/context/1',
                'text': 'Safe text.',
                'confidence': 0.9,
            },
            'nuance_appraisal': {
                'why_now': 'safe fixture',
                'grounded': True,
                'confidence': 0.9,
            },
        })


def test_preview_loop_card_runs_01_preview_harness_without_side_effects():
    card = build_preview_loop_card({
        'schema': 'lumi.hermes.preview_loop_input.v1',
        'mode': 'preview_0_1_0',
        'session_goal': 'Shape actual Lumi 0.1.0 with research harness in chat.',
        'observation': 'User wants the 0.1.0 preview loop implemented before officialization sprints.',
        'reflection': 'This needs a bounded in-chat loop, not a hidden runtime or silent memory promotion.',
        'pattern_name': 'officialization-before-automation',
        'proposed_adjustment': 'Run preview as observe-reflect-suggest-consent-apply-record with zero automatic writes.',
        'consent_state': 'ask_before_apply',
        'hypothesis': 'A visible preview harness makes Lumi useful without pretending it is an autonomous service.',
        'observed_signal': 'explicit user request to implement the preview loop here',
    })

    assert card['schema'] == 'lumi.hermes.preview_loop_card.v1'
    assert card['mode'] == 'preview_0_1_0'
    assert card['release_label'] == '0.1.0 preview with research harness'
    assert card['loop'] == [
        'observe',
        'reflect',
        'name_pattern',
        'suggest_adjustment',
        'ask_consent',
        'apply_small_change',
        'record_learning_only_if_approved',
    ]
    assert card['harness']['session_goal'].startswith('Shape actual Lumi')
    assert card['harness']['consent_state'] == 'ask_before_apply'
    assert card['safety']['canonical_writes'] == 0
    assert card['safety']['runtime_actions'] == []
    assert card['safety']['external_model_use'] == 'ask_each_time'
    assert card['safety']['memory_promotion'] == 'review_required'
    assert card['next_prompt'] == 'Approve this small adjustment, revise it, or leave it as a draft?'


def test_preview_loop_fails_closed_without_required_harness_fields():
    card = build_preview_loop_card({
        'schema': 'lumi.hermes.preview_loop_input.v1',
        'mode': 'preview_0_1_0',
        'session_goal': 'Incomplete preview.',
        'observation': '',
        'reflection': 'Missing observation should block applying the loop.',
        'pattern_name': 'incomplete',
        'proposed_adjustment': 'Do nothing.',
        'consent_state': 'approved',
    })

    assert card['status'] == 'fail_closed'
    assert card['safety']['canonical_writes'] == 0
    assert 'missing observation' in card['safety']['blocked_reasons']
    assert card['next_prompt'] == 'Preview loop is incomplete; revise the draft before applying anything.'


@pytest.mark.parametrize('forbidden', ['chat_id', 'job_id', 'scheduler_queue', 'runtime_state'])
def test_preview_loop_rejects_private_hermes_runtime_fields(forbidden):
    with pytest.raises(ValueError, match=forbidden):
        build_preview_loop_card({
            'schema': 'lumi.hermes.preview_loop_input.v1',
            'mode': 'preview_0_1_0',
            forbidden: 'do-not-export',
            'session_goal': 'Safe fixture.',
            'observation': 'Safe fixture.',
            'reflection': 'Safe fixture.',
            'pattern_name': 'safe-fixture',
            'proposed_adjustment': 'Ask before applying.',
            'consent_state': 'ask_before_apply',
        })


def test_reaction_presence_card_is_shadow_only_and_tiny():
    card = build_reaction_presence_card({
        'schema': 'lumi.hermes.reaction_presence_input.v1',
        'mode': 'reaction_presence_shadow',
        'surface': 'telegram',
        'reaction': '❤️',
        'source_message_role': 'assistant',
        'scope': 'current_turn',
        'previous_reaction_ack_turns_ago': 10,
    })

    assert card['schema'] == 'lumi.reaction_aware_presence.record.v1'
    assert card['stage'] == 'sprint_8_reaction_aware_presence'
    assert card['reaction_signal']['reaction_family'] == 'affection'
    assert card['presence_decision']['reply'] == '❤️'
    assert card['presence_decision']['reply_is_short'] is True
    assert card['live_surface']['mode'] == 'shadow_live_surface_candidate'
    assert card['live_surface']['telegram_reaction_ingestion_verified'] is False
    assert card['safety']['canonical_writes'] == 0
    assert card['safety']['runtime_actions'] == []
    assert card['safety']['telegram_messages_sent'] == 0


@pytest.mark.parametrize('forbidden', ['chat_id', 'token', 'api_key', 'scheduler_queue', 'runtime_state'])
def test_reaction_presence_card_rejects_private_runtime_fields(forbidden):
    with pytest.raises(ValueError, match=forbidden):
        build_reaction_presence_card({
            'schema': 'lumi.hermes.reaction_presence_input.v1',
            'mode': 'reaction_presence_shadow',
            'reaction': '👍',
            forbidden: 'do-not-export',
        })


def test_preview_installer_outputs_inspectable_json_without_writes(tmp_path):
    result = subprocess.run(
        [sys.executable, str(PREVIEW), '--dry-run', '--root', str(tmp_path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload['mode'] == 'dry_run'
    assert payload['would_write'] == []
    assert payload['canonical_writes'] == 0
    assert payload['install_root'] == str(tmp_path)
    assert list(tmp_path.iterdir()) == []
