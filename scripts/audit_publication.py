"""Audit staged/tracked publication files without printing possible secret values.

This is a deterministic allowlist/integrity and high-confidence pattern check,
not a comprehensive credential detector or a substitute for human review.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_FILES = {
    '.gitignore', 'README.md', 'THIRD_PARTY_NOTICES.md', 'pytest.ini', 'requirements-dev.txt',
    'docs/architecture.md', 'docs/photo-storage.md', 'docs/publication-license-review.json',
    'docs/source-manifest.json', 'docs/validation.md',
    'docs/media/01-welcome.png', 'docs/media/02-settings.png', 'docs/media/03-photo.png',
    'docs/media/04-result.png', 'docs/media/05-history.png', 'docs/media/06-detail.png',
    'docs/media/capture-report.json', 'docs/media/walkthrough.gif', 'docs/media/walkthrough.webm',
    'scripts/audit_publication.py', 'scripts/capture_portfolio.py', 'scripts/run_checks.py',
    'scripts/run_local.py', 'tests/test_publication_audit.py',
}
PATTERNS = {
    'private-key': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'github-token': re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}'),
    'google-api-key': re.compile(rb'AIza[0-9A-Za-z_-]{35}'),
    'aws-access-key': re.compile(rb'(?:AKIA|ASIA)[A-Z0-9]{16}'),
    'provider-key': re.compile(rb'sk-(?:proj-|ant-)?[A-Za-z0-9_-]{40,}'),
    'retired-private-host': re.compile(rb'tailf' + rb'74832'),
}


def main():
    entries = subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=ROOT).decode().split('\0')
    index = {}
    modes = {}
    for entry in filter(None, entries):
        metadata, name = entry.split('\t', 1)
        mode, object_id, stage = metadata.split()
        if stage != '0' or mode not in {'100644', '100755'}:
            raise SystemExit('Unsupported index entry: ' + name)
        index[name] = subprocess.check_output(['git', 'cat-file', 'blob', object_id], cwd=ROOT)
        modes[name] = mode
    paths = list(index)
    assert paths, 'Stage the reviewed files before auditing'
    manifest = json.loads(index['docs/source-manifest.json'])
    allowed = {item['path'] for item in manifest['files']} | PUBLICATION_FILES
    adjusted = {item['path']: item['published_sha256'] for item in manifest['publication_adjustments']}
    errors = []
    for item in manifest['files']:
        expected = adjusted.get(item['path'], item['sha256'])
        if item['path'] not in index or hashlib.sha256(index[item['path']]).hexdigest() != expected:
            errors.append('source-integrity: ' + item['path'])
        if item.get('mode') and modes.get(item['path']) != item['mode']:
            errors.append('source-mode: ' + item['path'])
    for name in paths:
        path = Path(name)
        parts = path.parts
        if name not in allowed:
            errors.append('outside-publication-allowlist: ' + name)
        if any(part in {'.beads', '.config', '.local', '.cache', 'node_modules', 'python_modules', 'raw'} for part in parts):
            errors.append('forbidden-path: ' + name)
            continue
        if path.name.startswith('.env') or path.name == 'settings.json' or path.suffix in {'.db', '.sqlite', '.sqlite3', '.log'}:
            errors.append('local-state: ' + name)
        raw = index[name]
        for kind, pattern in PATTERNS.items():
            if pattern.search(raw):
                errors.append(kind + ': ' + name)
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(paths)} publication files; {len(manifest["files"])} imported files accounted for; no forbidden local state or detected credential patterns')


if __name__ == '__main__':
    main()
