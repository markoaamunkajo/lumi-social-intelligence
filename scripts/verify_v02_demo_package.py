#!/usr/bin/env python3
"""Verify the public-safe v0.2 demo package.

The verifier is deliberately conservative: it reads the tracked demo receipts and
Markdown, checks that the human-readable story matches the machine-readable
boundary, and fails closed if a live Telegram/native reaction claim appears
without observed evidence.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / 'docs' / 'demos'
REQUIRED_ARTIFACTS = (
    'v0.2-demo-evidence.json',
    'v0.2-demo-side-by-side.json',
    'v0.2-demo-side-by-side.md',
    'v0.2-demo-index.md',
    'v0.2-demo-script.md',
)
FORBIDDEN_LIVE_CLAIM_PATTERNS = (
    r'(?i)native outbound (emoji )?reaction delivery\s*[:\-]\s*(claimed|live|observed|verified)',
    r'(?i)telegram reactions sent\s*[:\-`]\s*(?!0\b)\d+',
    r'(?i)canonical writes\s*[:\-`]\s*(?!0\b)\d+',
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:  # pragma: no cover - exact exception text is enough for report
        raise ValueError(f'{path.relative_to(ROOT)} is not valid JSON: {exc}') from exc
    if not isinstance(data, dict):
        raise ValueError(f'{path.relative_to(ROOT)} must contain a JSON object')
    return data


def _contains_all(text: str, needles: list[str]) -> bool:
    lowered = text.lower()
    return all(needle.lower() in lowered for needle in needles)


def verify(demo_dir: Path = DEMO_DIR) -> dict[str, Any]:
    findings: list[str] = []
    required_paths = {name: demo_dir / name for name in REQUIRED_ARTIFACTS}
    missing = [name for name, path in required_paths.items() if not path.is_file()]
    if missing:
        findings.append(f'missing required demo artifacts: {missing}')

    evidence: dict[str, Any] = {}
    side_by_side: dict[str, Any] = {}
    markdown = ''
    index_text = ''
    script_text = ''

    if not missing:
        try:
            evidence = _read_json(required_paths['v0.2-demo-evidence.json'])
            side_by_side = _read_json(required_paths['v0.2-demo-side-by-side.json'])
            markdown = required_paths['v0.2-demo-side-by-side.md'].read_text(encoding='utf-8')
            index_text = required_paths['v0.2-demo-index.md'].read_text(encoding='utf-8')
            script_text = required_paths['v0.2-demo-script.md'].read_text(encoding='utf-8')
        except ValueError as exc:
            findings.append(str(exc))

    safety = evidence.get('safety', {}) if isinstance(evidence.get('safety'), dict) else {}
    live_claims = side_by_side.get('live_claims', {}) if isinstance(side_by_side.get('live_claims'), dict) else {}
    observed = evidence.get('evidence', {}).get('observed', []) if isinstance(evidence.get('evidence'), dict) else []
    shadow_only = evidence.get('evidence', {}).get('shadow_only', []) if isinstance(evidence.get('evidence'), dict) else []
    blocked_reasons = side_by_side.get('blocked_reasons', [])

    if evidence.get('schema') != 'lumi.v02.demo_receipt.v1':
        findings.append('v0.2 evidence schema mismatch')
    if evidence.get('status') != 'valid_v02_demo_receipt':
        findings.append('v0.2 evidence receipt is not valid')
    if side_by_side.get('schema') != 'lumi.v02.demo_side_by_side_report.v1':
        findings.append('v0.2 side-by-side schema mismatch')
    if side_by_side.get('status') != 'ready_for_demo':
        findings.append('v0.2 side-by-side report is not ready_for_demo')

    if safety.get('canonical_writes') != 0:
        findings.append('canonical_writes must be 0')
    if safety.get('telegram_reactions_sent') != 0:
        findings.append('telegram_reactions_sent must be 0')
    if safety.get('telegram_messages_sent') != 0:
        findings.append('telegram_messages_sent must be 0')
    if safety.get('runtime_actions') != []:
        findings.append('runtime_actions must be empty')
    if safety.get('requires_human_review_before_live_wiring') is not True:
        findings.append('requires_human_review_before_live_wiring must be true')

    live_boundary = live_claims.get('native_outbound_reaction_delivery')
    if live_boundary != 'not_claimed':
        findings.append('native outbound reaction delivery must remain not_claimed')

    if not isinstance(observed, list) or not observed:
        findings.append('observed evidence list must be present')
    if not isinstance(shadow_only, list) or not shadow_only:
        findings.append('shadow_only evidence list must be present')

    blocked_action_explanations_present = _contains_all(
        '\n'.join([markdown, index_text, script_text]),
        [
            'not claimed live',
            'canonical writes',
            'telegram reactions sent',
            'synthetic/public-safe context',
            'do not claim',
        ],
    )
    if not blocked_action_explanations_present:
        findings.append('blocked-action explanations are missing from demo docs')

    markdown_matches_json = _contains_all(
        markdown,
        [
            str(live_boundary),
            'canonical writes: `0`',
            'telegram reactions sent: `0`',
            'review card generated from synthetic context',
            'native outbound emoji reaction delivery',
        ],
    )
    if not markdown_matches_json:
        findings.append('side-by-side Markdown does not match JSON safety/live-claim boundary')

    forbidden_live_claims = []
    claim_scan_text = '\n'.join([markdown, index_text, script_text])
    for pattern in FORBIDDEN_LIVE_CLAIM_PATTERNS:
        if re.search(pattern, claim_scan_text):
            forbidden_live_claims.append(pattern)
    if forbidden_live_claims:
        findings.append(f'forbidden live claims detected: {forbidden_live_claims}')

    report = {
        'schema': 'lumi.v02.demo_package_verification.v1',
        'status': 'verified' if not findings else 'blocked',
        'required_artifacts': list(REQUIRED_ARTIFACTS),
        'required_artifacts_present': not missing,
        'demo_id': evidence.get('demo_id', ''),
        'observed': observed if isinstance(observed, list) else [],
        'shadow_only': shadow_only if isinstance(shadow_only, list) else [],
        'live_claim_boundary': {
            'native_outbound_reaction_delivery': live_boundary or 'unknown',
        },
        'safety': {
            'canonical_writes': safety.get('canonical_writes'),
            'runtime_actions': safety.get('runtime_actions'),
            'telegram_messages_sent': safety.get('telegram_messages_sent'),
            'telegram_reactions_sent': safety.get('telegram_reactions_sent'),
            'requires_human_review_before_live_wiring': safety.get('requires_human_review_before_live_wiring'),
        },
        'canonical_writes': safety.get('canonical_writes'),
        'blocked_action_explanations_present': blocked_action_explanations_present,
        'markdown_matches_json': markdown_matches_json,
        'forbidden_live_claims': forbidden_live_claims,
        'receipt_blocked_reasons': blocked_reasons if isinstance(blocked_reasons, list) else [],
        'findings': findings,
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Verify the Lumi v0.2 public-safe demo package.')
    parser.add_argument('--demo-dir', type=Path, default=DEMO_DIR)
    parser.add_argument('--report', type=Path, default=None)
    args = parser.parse_args(argv)

    report = verify(args.demo_dir)
    payload = json.dumps(report, indent=2, sort_keys=True)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload + '\n', encoding='utf-8')
    print(payload)
    return 0 if report['status'] == 'verified' else 1


if __name__ == '__main__':
    raise SystemExit(main())
