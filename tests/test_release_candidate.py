import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'prepare_release_candidate.py'
NOTES = ROOT / 'docs' / 'releases' / 'v0.1.0.md'
VALID_NOTES = '''
We are making the self-improvement loop something that is human-shaped.
governed reflection layer
not an auto-personality-rewriter
confidence scoring
contradiction handling
user approval
skill evaluation
Lumi for Hermes
canonical_writes: 0
'''


def load_module():
    spec = importlib.util.spec_from_file_location('prepare_release_candidate', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_release_notes_define_human_shaped_governed_scope():
    text = NOTES.read_text(encoding='utf-8')
    assert '# Lumi Social Intelligence v0.1.0' in text
    assert 'We are making the self-improvement loop something that is human-shaped.' in text
    assert 'governed reflection layer' in text
    assert 'not an auto-personality-rewriter' in text
    assert 'confidence scoring' in text
    assert 'contradiction handling' in text
    assert 'user approval' in text
    assert 'skill evaluation' in text
    assert 'Lumi for Hermes' in text
    assert 'canonical_writes: 0' in text
    assert 'OpenClaw' in text and 'deferred' in text


def test_release_candidate_plan_is_non_mutating_by_default(monkeypatch, tmp_path):
    module = load_module()
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    (tmp_path / 'docs' / 'releases').mkdir(parents=True)
    (tmp_path / 'docs' / 'releases' / 'v0.1.0.md').write_text(VALID_NOTES, encoding='utf-8')

    def fake_run(command):
        if command[:2] == ['git', 'status']:
            return '## main...origin/main\n'
        if command[:2] == ['git', 'tag']:
            return ''
        if command[:3] == ['git', 'rev-parse', 'HEAD']:
            return 'abc123\n'
        if command[:3] == ['git', 'rev-parse', '--abbrev-ref']:
            return 'main\n'
        raise AssertionError(command)

    monkeypatch.setattr(module, '_run', fake_run)
    plan = module.build_plan(tag='v0.1.0', notes_path='docs/releases/v0.1.0.md')
    assert plan['schema'] == 'lumi.release_candidate_plan.v1'
    assert plan['tag'] == 'v0.1.0'
    assert plan['canonical_writes'] == 0
    assert plan['pushes'] == []
    assert plan['status'] == 'ready'
    assert plan['release_notes'] == 'docs/releases/v0.1.0.md'


def test_release_candidate_blocks_dirty_tree(monkeypatch, tmp_path):
    module = load_module()
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    (tmp_path / 'docs' / 'releases').mkdir(parents=True)
    (tmp_path / 'docs' / 'releases' / 'v0.1.0.md').write_text(VALID_NOTES, encoding='utf-8')

    def fake_run(command):
        if command[:2] == ['git', 'status']:
            return '## main...origin/main\n M README.md\n'
        if command[:2] == ['git', 'tag']:
            return ''
        if command[:3] == ['git', 'rev-parse', 'HEAD']:
            return 'abc123\n'
        if command[:3] == ['git', 'rev-parse', '--abbrev-ref']:
            return 'main\n'
        raise AssertionError(command)

    monkeypatch.setattr(module, '_run', fake_run)
    plan = module.build_plan(tag='v0.1.0', notes_path='docs/releases/v0.1.0.md')
    assert plan['status'] == 'blocked'
    assert any('working tree is not clean' in item for item in plan['blockers'])


def test_release_candidate_blocks_existing_tag(monkeypatch, tmp_path):
    module = load_module()
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    (tmp_path / 'docs' / 'releases').mkdir(parents=True)
    (tmp_path / 'docs' / 'releases' / 'v0.1.0.md').write_text(VALID_NOTES, encoding='utf-8')

    def fake_run(command):
        if command[:2] == ['git', 'status']:
            return '## main...origin/main\n'
        if command[:2] == ['git', 'tag']:
            return 'v0.1.0\n'
        if command[:3] == ['git', 'rev-parse', 'HEAD']:
            return 'abc123\n'
        if command[:3] == ['git', 'rev-parse', '--abbrev-ref']:
            return 'main\n'
        raise AssertionError(command)

    monkeypatch.setattr(module, '_run', fake_run)
    plan = module.build_plan(tag='v0.1.0', notes_path='docs/releases/v0.1.0.md')
    assert plan['status'] == 'blocked'
    assert any('tag already exists' in item for item in plan['blockers'])


def test_cli_writes_plan_without_creating_tag(tmp_path):
    module = load_module()
    output = tmp_path / 'plan.json'
    plan = module.main(['--tag', 'v0.1.0-test', '--report', str(output)])
    assert output.exists()
    written = json.loads(output.read_text(encoding='utf-8'))
    assert written['schema'] == 'lumi.release_candidate_plan.v1'
    assert written['tag'] == 'v0.1.0-test'
    assert written['canonical_writes'] == 0
    assert written['pushes'] == []
    assert plan == written
