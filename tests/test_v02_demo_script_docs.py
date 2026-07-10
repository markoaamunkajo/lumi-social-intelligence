from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'docs' / 'demos' / 'v0.2-demo-script.md'
DEMO_INDEX = ROOT / 'docs' / 'demos' / 'v0.2-demo-index.md'
DEMOS_README = ROOT / 'docs' / 'demos' / 'README.md'
ROADMAP = ROOT / 'docs' / 'roadmap.md'


def test_v02_demo_script_exists_as_short_human_review_script():
    text = SCRIPT.read_text(encoding='utf-8')

    assert '# v0.2 Demo Script' in text
    assert '## One-minute version' in text
    assert '## Show this' in text
    assert '## Say this' in text
    assert '## Do not claim' in text
    assert len(text.splitlines()) <= 90


def test_v02_demo_script_points_to_evidence_and_preserves_boundaries():
    text = SCRIPT.read_text(encoding='utf-8')

    required = [
        '[v0.2 Demo Index](v0.2-demo-index.md)',
        '[v0.2-demo-evidence.json](v0.2-demo-evidence.json)',
        '[v0.2-demo-side-by-side.json](v0.2-demo-side-by-side.json)',
        '[v0.2-demo-side-by-side.md](v0.2-demo-side-by-side.md)',
        'Native outbound reaction delivery is not claimed live',
        'Canonical writes: `0`',
        'Telegram reactions sent: `0`',
        'synthetic/public-safe context',
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_demo_navigation_links_to_script_and_roadmap_marks_it_done():
    assert '[v0.2 Demo Script](v0.2-demo-script.md)' in DEMO_INDEX.read_text(
        encoding='utf-8'
    )
    assert '[v0.2 Demo Script](v0.2-demo-script.md)' in DEMOS_README.read_text(
        encoding='utf-8'
    )

    roadmap = ROADMAP.read_text(encoding='utf-8')
    assert '- [x] Add a concise `docs/demos/v0.2-demo-script.md`' in roadmap
