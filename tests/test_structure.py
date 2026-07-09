from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_playground_structure_exists():
    required = [
        'core/layered-memory',
        'core/nuances',
        'core/presence',
        'adapters/hermes',
        'installers/lumi-for-hermes',
        'docs/architecture.md',
        'docs/host-compatibility.md',
        'docs/release-boundary.md',
        'docs/product-brief.md',
        'scripts/release_check.sh',
        'scripts/public_secret_scan.py',
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    assert not missing, missing


def test_openclaw_adapter_is_not_added_before_compatibility_research():
    assert not (ROOT / 'adapters/openclaw').exists()
    assert not (ROOT / 'installers/lumi-for-openclaw').exists()
