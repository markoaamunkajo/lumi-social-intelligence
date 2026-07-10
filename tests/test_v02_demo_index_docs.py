from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO_INDEX = ROOT / 'docs' / 'demos' / 'v0.2-demo-index.md'
README = ROOT / 'README.md'
ROADMAP = ROOT / 'docs' / 'roadmap.md'
DEMOS_README = ROOT / 'docs' / 'demos' / 'README.md'


REQUIRED_DEMO_ARTIFACTS = (
    'v0.2-demo-evidence.json',
    'v0.2-demo-side-by-side.json',
    'v0.2-demo-side-by-side.md',
)


def test_v02_demo_index_exists_and_links_all_current_artifacts():
    text = DEMO_INDEX.read_text(encoding='utf-8')

    assert '# v0.2 Demo Index' in text
    assert 'context → appraisal → presence decision → receipt' in text
    assert 'Observed in this repository' in text
    assert 'Shadow-only / not yet claimed live' in text
    for artifact in REQUIRED_DEMO_ARTIFACTS:
        assert f']({artifact})' in text


def test_v02_demo_index_keeps_live_claim_boundary_visible():
    text = DEMO_INDEX.read_text(encoding='utf-8')

    required_boundaries = [
        'Native outbound reaction delivery is **not claimed live**',
        'Canonical writes: `0`',
        'Telegram reactions sent: `0`',
        'synthetic/public-safe context',
    ]
    missing = [claim for claim in required_boundaries if claim not in text]
    assert not missing, missing


def test_public_navigation_points_to_v02_demo_index():
    expected_link = '[v0.2 Demo Index](docs/demos/v0.2-demo-index.md)'
    assert expected_link in README.read_text(encoding='utf-8')

    demos_text = DEMOS_README.read_text(encoding='utf-8')
    assert '[v0.2 Demo Index](v0.2-demo-index.md)' in demos_text

    roadmap_text = ROADMAP.read_text(encoding='utf-8')
    assert '[v0.2 Demo Index](demos/v0.2-demo-index.md)' in roadmap_text
