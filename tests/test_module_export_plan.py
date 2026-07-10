import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'plan_module_export.py'


def _run_plan(tmp_path: Path, report: dict) -> subprocess.CompletedProcess[str]:
    report_path = tmp_path / 'audit-report.json'
    plan_path = tmp_path / 'copy-plan.json'
    report_path.write_text(json.dumps(report), encoding='utf-8')
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            '--audit-report',
            str(report_path),
            '--plan',
            str(plan_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_export_plan_maps_allowed_files_to_release_surface_without_copying(tmp_path):
    source = tmp_path / 'candidate'
    source.mkdir()
    (source / 'README.md').write_text('# Nuances\n', encoding='utf-8')
    report = {
        'module': 'Nuances',
        'package_name': 'lumi-nuances',
        'release_surface': 'core/nuances',
        'source': str(source),
        'status': 'pass',
        'would_copy': False,
        'allowed_files': ['README.md', 'src/lumi_nuances/__init__.py'],
        'blocked_files': [],
    }

    result = _run_plan(tmp_path, report)

    assert result.returncode == 0, result.stderr
    plan = json.loads((tmp_path / 'copy-plan.json').read_text(encoding='utf-8'))
    assert plan['status'] == 'ready_for_review'
    assert plan['would_copy'] is False
    assert plan['requires_human_review'] is True
    assert plan['copy_operations'] == [
        {
            'source': str(source / 'README.md'),
            'destination': str(ROOT / 'core/nuances/README.md'),
        },
        {
            'source': str(source / 'src/lumi_nuances/__init__.py'),
            'destination': str(ROOT / 'core/nuances/src/lumi_nuances/__init__.py'),
        },
    ]
    assert not (ROOT / 'core/nuances/src/lumi_nuances/__init__.py').exists()


def test_export_plan_refuses_path_escape_entries(tmp_path):
    source = tmp_path / 'candidate'
    source.mkdir()
    report = {
        'module': 'Presence',
        'package_name': 'lumi-presence',
        'release_surface': 'core/presence',
        'source': str(source),
        'status': 'pass',
        'would_copy': False,
        'allowed_files': ['README.md', '../private.txt', '/tmp/private.txt'],
        'blocked_files': [],
    }

    result = _run_plan(tmp_path, report)

    assert result.returncode == 1
    assert not (tmp_path / 'copy-plan.json').exists()
    assert 'unsafe relative path in audit report' in result.stderr


def test_export_plan_refuses_blocked_or_unreviewed_audit_report(tmp_path):
    report = {
        'module': 'Presence',
        'package_name': 'lumi-presence',
        'release_surface': 'core/presence',
        'source': str(tmp_path / 'candidate'),
        'status': 'blocked',
        'would_copy': False,
        'allowed_files': ['README.md'],
        'blocked_files': [{'path': 'runs/private.jsonl', 'reason': 'raw run artifact is forbidden'}],
    }

    result = _run_plan(tmp_path, report)

    assert result.returncode == 1
    assert not (tmp_path / 'copy-plan.json').exists()
    assert 'audit report is not pass-status' in result.stderr
