#!/usr/bin/env python3
"""Apply a reviewed Lumi module export copy plan.

This is the first mutating step in the module promotion chain. It deliberately
requires an explicit confirmation flag and only accepts plans produced for human
review by plan_module_export.py.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path, PurePosixPath
from typing import Any


class ModuleExportApplyError(Exception):
    """Raised when a reviewed copy plan cannot be safely applied."""


def _load_plan(path: Path) -> dict[str, Any]:
    try:
        plan = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError as exc:
        raise ModuleExportApplyError(f'copy plan does not exist: {path}') from exc
    except json.JSONDecodeError as exc:
        raise ModuleExportApplyError(f'{path}: invalid JSON: {exc}') from exc
    if not isinstance(plan, dict):
        raise ModuleExportApplyError('copy plan must be a JSON object')
    return plan


def _require_string(plan: dict[str, Any], key: str) -> str:
    value = plan.get(key)
    if not isinstance(value, str) or not value:
        raise ModuleExportApplyError(f'copy plan missing required string field: {key}')
    return value


def _validate_plan_header(plan: dict[str, Any]) -> None:
    if plan.get('status') != 'ready_for_review':
        raise ModuleExportApplyError('copy plan is not ready_for_review')
    if plan.get('would_copy') is not False:
        raise ModuleExportApplyError('copy plan must be non-mutating before apply')
    if plan.get('requires_human_review') is not True:
        raise ModuleExportApplyError('copy plan must require human review')
    _require_string(plan, 'module')
    _require_string(plan, 'package_name')
    _require_string(plan, 'release_surface')


def _require_operation_path(raw: dict[str, Any], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value:
        raise ModuleExportApplyError(f'copy operation missing {key}')
    posix = PurePosixPath(value)
    if '..' in posix.parts:
        raise ModuleExportApplyError(f'{key} escapes release surface: {value}')
    return value


def _copy_operations(plan: dict[str, Any]) -> list[dict[str, Path]]:
    raw_operations = plan.get('copy_operations')
    if not isinstance(raw_operations, list) or not raw_operations:
        raise ModuleExportApplyError('copy plan must include copy_operations')

    operations: list[dict[str, Path]] = []
    for index, raw in enumerate(raw_operations):
        if not isinstance(raw, dict):
            raise ModuleExportApplyError(f'copy operation #{index} must be an object')
        source = _require_operation_path(raw, 'source')
        destination = _require_operation_path(raw, 'destination')
        source_path = Path(source)
        destination_path = Path(destination)
        if not source_path.is_file():
            raise ModuleExportApplyError(f'source file does not exist: {source_path}')
        operations.append({'source': source_path, 'destination': destination_path})
    return operations


def _relative_destination(destination: Path, destinations_root: Path) -> str:
    try:
        return destination.resolve().relative_to(destinations_root.resolve()).as_posix()
    except ValueError:
        return destination.name


def _destination_root(operations: list[dict[str, Path]]) -> Path:
    destination_parents = [str(operation['destination'].parent) for operation in operations]
    return Path(os.path.commonpath(destination_parents))


def apply_copy_plan(plan: dict[str, Any]) -> dict[str, Any]:
    _validate_plan_header(plan)
    operations = _copy_operations(plan)
    destinations_root = _destination_root(operations)

    copied_files: list[str] = []
    for operation in operations:
        destination = operation['destination']
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(operation['source'], destination)
        copied_files.append(_relative_destination(destination, destinations_root))

    manifest = {
        'module': plan['module'],
        'package_name': plan['package_name'],
        'release_surface': plan['release_surface'],
        'status': 'applied_reviewed_plan',
        'copied_files': copied_files,
    }
    manifest_path = destinations_root / '.lumi-export-manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Apply a reviewed Lumi module export copy plan.')
    parser.add_argument('--plan', required=True, type=Path, help='Reviewed JSON copy plan from plan_module_export.py')
    parser.add_argument(
        '--apply-reviewed-plan',
        action='store_true',
        help='Required acknowledgement that the copy plan has been reviewed by a human',
    )
    args = parser.parse_args(argv)

    if not args.apply_reviewed_plan:
        print('applying a module export requires --apply-reviewed-plan', file=sys.stderr)
        return 1

    try:
        plan = _load_plan(args.plan)
        manifest = apply_copy_plan(plan)
    except ModuleExportApplyError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"applied reviewed module export for {manifest['module']}; copied {len(manifest['copied_files'])} files")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
