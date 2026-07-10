#!/usr/bin/env python3
"""Build deterministic Lumi Social Intelligence release artifacts.

Sprint 5 keeps release building local and inspectable: the script packages only
tracked public doorway files, writes artifacts to the requested output directory,
scans the archive member list for private/runtime material, and emits checksums.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.1.0-rc.1'
ARCHIVE_NAME = f'lumi-social-intelligence-{VERSION}.zip'
FORBIDDEN_MEMBER_PATTERNS = (
    '.git/*',
    '.hermes/*',
    'runs/*',
    'logs/*',
    'cron/*',
    'state/*',
    'secrets/*',
    'private/*',
    '*__pycache__*',
    '*.pyc',
    '.pytest_cache/*',
    'dist/*',
    'build/*',
    '*.egg-info/*',
)
REQUIRED_RELEASE_MEMBERS = (
    'README.md',
    'LICENSE',
    'LICENSE-DOCS.md',
    'NOTICE.md',
    'docs/releases/v0.1.0.md',
    'scripts/release_check.sh',
    'scripts/public_secret_scan.py',
    'scripts/public_readiness_audit.py',
    'scripts/prepare_release_candidate.py',
    'scripts/build_release_artifacts.py',
    'adapters/hermes/lumi_for_hermes.py',
    'adapters/hermes/README.md',
    'installers/lumi-for-hermes/preview.py',
    'installers/lumi-for-hermes/README.md',
    'core/presence/pyproject.toml',
)


def _run_git_ls_files() -> list[str]:
    result = subprocess.run(
        ['git', 'ls-files'],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return sorted(line for line in result.stdout.splitlines() if line)


def _is_forbidden(member: str) -> bool:
    return any(fnmatch.fnmatch(member, pattern) for pattern in FORBIDDEN_MEMBER_PATTERNS)


def _private_material_findings(members: Iterable[str]) -> list[dict[str, str]]:
    findings = []
    for member in members:
        if _is_forbidden(member):
            findings.append({'path': member, 'reason': 'forbidden release archive member'})
    return findings


def _write_zip(archive_path: Path, members: list[str]) -> None:
    with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for member in members:
            source = ROOT / member
            if not source.is_file():
                continue
            info = zipfile.ZipInfo(member)
            info.date_time = (2026, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if os.access(source, os.X_OK) else 0o644) << 16
            zf.writestr(info, source.read_bytes())


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _write_checksums(output_dir: Path, artifact_paths: list[Path]) -> Path:
    checksum_path = output_dir / 'SHA256SUMS'
    lines = [f'{_sha256(path)}  {path.name}' for path in sorted(artifact_paths, key=lambda p: p.name)]
    checksum_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return checksum_path


def _package_artifacts(members: list[str]) -> list[dict[str, str]]:
    packages = []
    for product, package_name, surface in (
        ('Lumi Layered Memory', 'lumi-layered-memory', 'core/layered-memory'),
        ('Nuances', 'lumi-nuances', 'core/nuances'),
        ('Presence', 'lumi-presence', 'core/presence'),
    ):
        has_pyproject = f'{surface}/pyproject.toml' in members
        packages.append({
            'product_name': product,
            'package_name': package_name,
            'release_surface': surface,
            'artifact_status': 'source_included' if has_pyproject else 'blocked_until_promoted',
        })
    return packages


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    tracked_members = _run_git_ls_files()
    findings = _private_material_findings(tracked_members)
    if findings:
        raise SystemExit(f'private material findings: {findings}')

    members = tracked_members
    missing_required = [member for member in REQUIRED_RELEASE_MEMBERS if member not in members]
    if missing_required:
        raise SystemExit(f'missing required release members: {missing_required}')

    archive_path = output_dir / ARCHIVE_NAME
    _write_zip(archive_path, members)

    manifest = {
        'schema': 'lumi.release_manifest.v1',
        'version': VERSION,
        'archive': ARCHIVE_NAME,
        'archive_members': members,
        'package_artifacts': _package_artifacts(members),
        'lumi_for_hermes_preview': {
            'adapter': 'adapters/hermes/lumi_for_hermes.py',
            'installer_preview': 'installers/lumi-for-hermes/preview.py',
            'mode': 'dry_run_review_card_only',
        },
        'private_material_findings': findings,
        'canonical_writes': 0,
    }
    manifest_path = output_dir / 'release-manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    checksums_path = _write_checksums(output_dir, [archive_path, manifest_path])

    return {
        'schema': 'lumi.release_artifacts.v1',
        'status': 'built',
        'version': VERSION,
        'output_dir': str(output_dir),
        'artifacts': [archive_path.name, manifest_path.name, checksums_path.name],
        'private_material_findings': findings,
        'canonical_writes': 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Build Lumi Social Intelligence release artifacts.')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'dist' / VERSION)
    args = parser.parse_args(argv)
    report = build(args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
