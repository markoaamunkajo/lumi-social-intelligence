from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALIGNMENT_DOC = ROOT / 'docs' / 'live-surface-workbench-alignment.md'
README = ROOT / 'README.md'
RELEASE_BOUNDARY = ROOT / 'docs' / 'release-boundary.md'
ROADMAP = ROOT / 'docs' / 'roadmap.md'


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def test_workbench_alignment_defines_public_surface_modes():
    text = read(ALIGNMENT_DOC)

    assert 'Draft · Research · Review · Export · Help' in text
    for mode in ('**Draft**', '**Research**', '**Review**', '**Export**', '**Help**'):
        assert mode in text


def test_workbench_alignment_hides_engine_room_terms_from_normal_ux():
    text = read(ALIGNMENT_DOC)

    assert 'Engine-room terms stay out of normal UX' in text
    assert 'models, queues, jobs, agents, packs, memory, source graph, scheduler IDs, chat IDs' in text
    assert 'Public examples, docs, and adapters should translate those concepts into the five surface modes above.' in text


def test_workbench_alignment_preserves_public_private_boundary():
    text = read(ALIGNMENT_DOC)

    assert 'confidential internal workbench workflows' in text
    assert 'raw research runs or scrape dumps' in text
    assert 'local pack manifests or pack internals from private workspaces' in text
    assert 'Evidence ≠ insight' in text
    assert 'Insight ≠ company truth' in text
    assert 'Company truth ≠ public claim' in text
    assert 'Do not extract value from people’s thinking space automatically.' in text


def test_readme_links_public_workbench_alignment_without_private_claims():
    text = read(README)

    assert '[Live Surface workbench alignment](docs/live-surface-workbench-alignment.md)' in text
    assert 'Draft · Research · Review · Export · Help' in text
    assert 'Public Lumi documents the surface contract; private workbenches keep their source material, pack internals, and raw evidence behind their own review gates.' in text


def test_release_boundary_mentions_workbench_alignment_contract():
    text = read(RELEASE_BOUNDARY)

    assert 'Public Live Surface workbench alignment' in text
    assert 'Draft · Research · Review · Export · Help' in text
    assert 'No confidential workbench workflows, local pack internals, private source ledgers, or raw evidence should be promoted here.' in text


def test_roadmap_tracks_public_workbench_alignment_done():
    text = read(ROADMAP)

    assert '- [x] Add public Live Surface workbench alignment for `Draft · Research · Review · Export · Help`.' in text
    assert '- [x] Keep private/internal workbench assumptions out of the public release doorway.' in text
