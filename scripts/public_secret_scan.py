#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {'.git', '.venv', '__pycache__', '.pytest_cache', 'dist', 'build'}
PATTERNS = [
    (re.compile(r'gho_[A-Za-z0-9_]{20,}'), 'GitHub token'),
    (re.compile(r'ghp_[A-Za-z0-9_]{20,}'), 'GitHub token'),
    (re.compile(r'AIza[0-9A-Za-z_\-]{20,}'), 'Google API key'),
    (re.compile(r'sk-[A-Za-z0-9]{20,}'), 'OpenAI-style API key'),
    (re.compile(r'(?i)api[_-]?key\s*[:=]\s*[^\s]+'), 'API key assignment'),
    (re.compile(r'(?i)password\s*[:=]\s*[^\s]+'), 'password assignment'),
    (re.compile(r'(?i)secret\s*[:=]\s*[^\s]+'), 'secret assignment'),
    (re.compile(r'(?i)chat[_-]?id\s*[:=]\s*[^\s]+'), 'chat id assignment'),
]
TEXT_SUFFIXES = {'.md', '.py', '.sh', '.txt', '.toml', '.yaml', '.yml', '.json', '.gitignore'}

failures: list[str] = []
for path in ROOT.rglob('*'):
    if any(part in SKIP_DIRS for part in path.parts):
        continue
    if path.is_dir():
        continue
    if path.suffix not in TEXT_SUFFIXES and path.name != '.gitignore':
        continue
    try:
        text = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        continue
    rel = path.relative_to(ROOT)
    for pattern, label in PATTERNS:
        for match in pattern.finditer(text):
            failures.append(f'{rel}: {label}: {match.group(0)[:80]}')

if failures:
    print('Public/secret scan failed:')
    for failure in failures:
        print(f' - {failure}')
    sys.exit(1)

print('Public/secret scan passed')
