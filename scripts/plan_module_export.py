#!/usr/bin/env python3
"""Create a reviewed copy plan from a passed Lumi module export audit.

This command is intentionally non-mutating: it consumes the JSON report produced
by audit_module_export.py, refuses blocked audits, and writes the copy operations
that a human can review before any later export command exists.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class ModuleExportPlanError(Exception):
    """Raised when an audit report cannot be turned into a reviewable plan."""


def _load_audit_report(path: Path) -> dict[str, Any]:
    try:
        report = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError as exc:
        raise ModuleExportPlanError(f'audit report does not exist: {path}') from exc
    except json.JSONDecodeError as exc:
        raise ModuleExportPlanError(f'{path}: invalid JSON: {exc}') from exc
    if not isinstance(report, dict):
        raise ModuleExportPlanError('audit report must be a JSON object')
    return report


def _require_string(report: dict[str, Any], key: str) -> str:
    value = report.get(key)
    if not isinstance(value, str) or not value:
        raise ModuleExportPlanError(f'audit report missing required string field: {key}')
    return value


def _require_string_list(report: dict[str, Any], key: str) -> list[str]:
    value = report.get(key)
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ModuleExportPlanError(f'audit report field must be a list of strings: {key}')
    return value


def _validate_passed_audit(report: dict[str, Any]) -> None:
    if report.get('status') != 'pass':
        raise ModuleExportPlanError('audit report is not pass-status')
    if report.get('would_copy') is not False:
        raise ModuleExportPlanError('audit report must come from a read-only audit')
    blocked_files = report.get('blocked_files')
    if blocked_files != []:
        raise ModuleExportPlanError('audit report still contains blocked files')


def _validate_relative_path(path: str) -> None:
    posix = PurePosixPath(path)
    if posix.is_absolute() or '..' in posix.parts:
        raise ModuleExportPlanError(f'unsafe relative path in audit report: {path}')


def build_copy_plan(report: dict[str, Any]) -> dict[str, Any]:
    _validate_passed_audit(report)
    module = _require_string(report, 'module')
    package_name = _require_string(report, 'package_name')
    release_surface = _require_string(report, 'release_surface')
    source = Path(_require_string(report, 'source'))
    allowed_files = _require_string_list(report, 'allowed_files')

    destination_root = ROOT / release_surface
    copy_operations = []
    for relative in allowed_files:
        _validate_relative_path(relative)
        copy_operations.append(
            {
                'source': str(source / relative),
                'destination': str(destination_root / relative),
            }
        )

    return {
        'module': module,
        'package_name': package_name,
        'release_surface': release_surface,
        'status': 'ready_for_review',
        'would_copy': False,
        'requires_human_review': True,
        'copy_operations': copy_operations,
    }


def _write_plan(plan: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Plan a Lumi module export without copying files.')
    parser.add_argument('--audit-report', required=True, type=Path, help='Passed JSON report from audit_module_export.py')
    parser.add_argument('--plan', required=True, type=Path, help='JSON copy-plan path to write')
    args = parser.parse_args(argv)

    try:
        report = _load_audit_report(args.audit_report)
        plan = build_copy_plan(report)
        _write_plan(plan, args.plan)
    except ModuleExportPlanError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"module export copy plan written to {args.plan}; no files copied")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
