from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER_README = ROOT / 'installers' / 'lumi-for-hermes' / 'README.md'
SYNTHETIC_PACK_README = ROOT / 'examples' / 'synthetic-memory-pack' / 'README.md'
RELEASE_NOTES = ROOT / 'docs' / 'releases' / 'v0.1.0.md'
ROADMAP = ROOT / 'docs' / 'roadmap.md'


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def test_public_installer_readme_uses_capability_language_not_sprint_labels():
    text = read(INSTALLER_README)

    assert 'dry-run installer preview' in text
    assert 'reviewable Hermes preview' in text
    assert 'Sprint 4' not in text


def test_synthetic_memory_pack_uses_capability_language_not_sprint_labels():
    text = read(SYNTHETIC_PACK_README)

    assert 'provider-neutral context boundary' in text
    assert 'Sprint 1' not in text


def test_release_notes_refer_to_capability_evidence_not_sprint_evidence():
    text = read(RELEASE_NOTES)

    assert 'capability evidence' in text
    assert 'Sprint 1–6 evidence' not in text
    assert 'Sprint 1-6 evidence' not in text


def test_roadmap_marks_capability_language_cleanup_done():
    text = read(ROADMAP)

    assert '- [x] Rename or reframe sprint-derived module names into durable capability names where useful.' in text
    assert '- [x] Keep tests and contract coverage, but remove process-first wording from public-facing docs.' in text
