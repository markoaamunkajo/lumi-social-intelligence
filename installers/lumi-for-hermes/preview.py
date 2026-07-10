#!/usr/bin/env python3
"""Inspect the Lumi for Hermes preview installer plan.

This preview is intentionally dry-run only. It reports the reviewed artifacts that
would be considered by a future installer without writing files or touching Hermes
runtime state.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_preview(*, root: Path, dry_run: bool) -> dict[str, object]:
    if not dry_run:
        raise SystemExit('Lumi for Hermes preview currently supports --dry-run only')
    return {
        'schema': 'lumi.hermes.installer_preview.v1',
        'mode': 'dry_run',
        'install_root': str(root),
        'would_write': [],
        'canonical_writes': 0,
        'artifacts': [
            'adapters/hermes/lumi_for_hermes.py',
            'adapters/hermes/README.md',
        ],
        'safety': [
            'does not read Hermes private runtime state',
            'does not write config, memory, scheduler, queues, or chat metadata',
            'produces review-card output only',
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Inspect Lumi for Hermes preview installer plan')
    parser.add_argument('--dry-run', action='store_true', required=True)
    parser.add_argument('--root', type=Path, default=Path.home() / '.hermes')
    args = parser.parse_args()
    print(json.dumps(build_preview(root=args.root, dry_run=args.dry_run), indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
