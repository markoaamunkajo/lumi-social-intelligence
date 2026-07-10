import json
import subprocess
import sys
from pathlib import Path

import pytest

from adapters.hermes.lumi_for_hermes import build_review_card

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
