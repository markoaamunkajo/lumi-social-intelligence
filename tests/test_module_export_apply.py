import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'apply_module_export.py'


def _run_apply(tmp_path: Path, plan: dict, *extra_args: str) -> subprocess.CompletedProcess[str]:
    plan_path = tmp_path / 'copy-plan.json'
    plan_path.write_text(json.dumps(plan), encoding='utf-8')
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            '--plan',
            str(plan_path),
            *extra_args,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_apply_export_requires_explicit_confirmation_flag(tmp_path):
    source = tmp_path / 'candidate'
    destination = tmp_path / 'exported' / 'README.md'
    source.mkdir()
    (source / 'README.md').write_text('# Presence\n', encoding='utf-8')
    plan = {
        'module': 'Presence',
        'package_name': 'lumi-presence',
        'release_surface': 'core/presence',
        'status': 'ready_for_review',
        'would_copy': False,
        'requires_human_review': True,
        'copy_operations': [
            {'source': str(source / 'README.md'), 'destination': str(destination)},
        ],
    }

    result = _run_apply(tmp_path, plan)

    assert result.returncode == 1
    assert 'requires --apply-reviewed-plan' in result.stderr
    assert not destination.exists()


def test_apply_export_copies_reviewed_plan_and_writes_manifest(tmp_path):
    source = tmp_path / 'candidate'
    destination_root = tmp_path / 'exported'
    source.mkdir()
    (source / 'README.md').write_text('# Layered Memory\n', encoding='utf-8')
    (source / 'pyproject.toml').write_text('[project]\nname = "lumi-layered-memory"\n', encoding='utf-8')
    plan = {
        'module': 'Lumi Layered Memory',
        'package_name': 'lumi-layered-memory',
        'release_surface': 'core/layered-memory',
        'status': 'ready_for_review',
        'would_copy': False,
        'requires_human_review': True,
        'copy_operations': [
            {'source': str(source / 'README.md'), 'destination': str(destination_root / 'README.md')},
            {'source': str(source / 'pyproject.toml'), 'destination': str(destination_root / 'pyproject.toml')},
        ],
    }

    result = _run_apply(tmp_path, plan, '--apply-reviewed-plan')

    assert result.returncode == 0, result.stderr
    assert (destination_root / 'README.md').read_text(encoding='utf-8') == '# Layered Memory\n'
    assert (destination_root / 'pyproject.toml').read_text(encoding='utf-8') == '[project]\nname = "lumi-layered-memory"\n'
    manifest = json.loads((destination_root / '.lumi-export-manifest.json').read_text(encoding='utf-8'))
    assert manifest['module'] == 'Lumi Layered Memory'
    assert manifest['package_name'] == 'lumi-layered-memory'
    assert manifest['status'] == 'applied_reviewed_plan'
    assert manifest['copied_files'] == ['README.md', 'pyproject.toml']


def test_apply_export_refuses_unsafe_destination_escape(tmp_path):
    source = tmp_path / 'candidate'
    safe_root = tmp_path / 'exported'
    unsafe_destination = safe_root / '..' / 'outside.txt'
    source.mkdir()
    (source / 'README.md').write_text('# Nuances\n', encoding='utf-8')
    plan = {
        'module': 'Nuances',
        'package_name': 'lumi-nuances',
        'release_surface': 'core/nuances',
        'status': 'ready_for_review',
        'would_copy': False,
        'requires_human_review': True,
        'copy_operations': [
            {'source': str(source / 'README.md'), 'destination': str(unsafe_destination)},
        ],
    }

    result = _run_apply(tmp_path, plan, '--apply-reviewed-plan')

    assert result.returncode == 1
    assert 'destination escapes release surface' in result.stderr
    assert not (tmp_path / 'outside.txt').exists()
