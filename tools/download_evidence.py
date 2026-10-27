"""Download the fixed evidence assets into a new directory and verify SHA-256.

Python 3.11+ standard library only. The gh transport uses the user's existing
GitHub CLI authentication; no access token is read or stored by this script.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.request

REPOSITORY = 'Lshiqi67/proper-hat-guessing-c5-reproducibility'
TAG = 'c5-arxiv-v1-evidence-20261027'
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_NAMES = {
    'c5-reviewed-evidence-20261027-v2-code.zip',
    'p001-two-stage-review-20261027.zip',
    *(f'c5-evidence-20261026-v1-weight{weight}.zip' for weight in range(17, 26)),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_manifest(path):
    manifest = json.loads(path.read_text(encoding='utf-8-sig'))
    require(manifest.get('schema_version') == 1, 'unsupported manifest schema')
    require(manifest.get('repository') == REPOSITORY, 'repository mismatch')
    require(manifest.get('tag') == TAG, 'release tag mismatch')
    assets = manifest.get('assets')
    require(isinstance(assets, list) and len(assets) == 11, 'expected eleven assets')
    names = [row['name'] for row in assets]
    require(len(set(names)) == len(names), 'duplicate asset name')
    require(set(names) == EXPECTED_NAMES, 'unexpected or missing asset')
    for row in assets:
        name = row['name']
        require(re.fullmatch(r'[A-Za-z0-9_.-]+', name), 'unsafe asset name')
        require(type(row['bytes']) is int and row['bytes'] > 0, 'invalid asset size')
        require(re.fullmatch(r'[0-9a-f]{64}', row['sha256']), 'invalid SHA-256')
        expected_url = f'https://github.com/{REPOSITORY}/releases/download/{TAG}/{name}'
        require(row['download_url'] == expected_url, 'unexpected download URL')
    require(sum(x['bytes'] for x in assets) == 1910553676, 'wrong total asset size')
    return manifest


def hash_file(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def verify_file(path, row):
    require(path.is_file() and not path.is_symlink(), 'download missing or symlink')
    require(path.stat().st_size == row['bytes'], f'wrong byte count: {row["name"]}')
    actual = hash_file(path)
    require(actual == row['sha256'], f'SHA-256 mismatch: {row["name"]}')
    return actual


def safe_output(raw):
    lexical = Path(raw).absolute()
    require(not lexical.exists(), 'output already exists; choose a fresh directory')
    require(lexical.parent.is_dir(), 'output parent must already exist')
    out = lexical.resolve()
    require(not out.is_relative_to(ROOT) and not ROOT.is_relative_to(out),
            'output must be outside the repository and not contain it')
    require(not any(part in {'.git', '.codex', '.agents'} for part in out.parts),
            'output cannot use a control directory')
    return out


def fetch_https(row, target):
    # Only the fixed, validated GitHub asset URL is used. No authentication
    # header is attached, so redirects cannot forward a script-supplied token.
    request = urllib.request.Request(row['download_url'], headers={
        'User-Agent': 'c5-evidence-reproduction/1',
        'Accept': 'application/octet-stream',
    })
    temporary = target.with_name(target.name + '.part')
    received = 0
    with urllib.request.urlopen(request, timeout=120) as response:
        with temporary.open('xb') as handle:
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                received += len(block)
                require(received <= row['bytes'], 'download exceeds manifest size')
                handle.write(block)
    verify_file(temporary, row)
    os.rename(temporary, target)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT / 'metadata/evidence-manifest.json')
    parser.add_argument('--out', required=True)
    parser.add_argument('--asset', action='append', help='exact asset name; repeat for a subset')
    parser.add_argument('--transport', choices=('gh', 'https'), default='gh')
    parser.add_argument('--from-directory', type=Path,
                        help='offline copy from existing archives, still verifies every selected file')
    args = parser.parse_args(argv)
    manifest = read_manifest(args.manifest.resolve())
    selected_names = args.asset or sorted(EXPECTED_NAMES)
    require(len(selected_names) == len(set(selected_names)), 'duplicate requested asset')
    require(set(selected_names) <= EXPECTED_NAMES, 'unknown requested asset')
    selected = [row for row in manifest['assets'] if row['name'] in selected_names]
    out = safe_output(args.out)
    source = args.from_directory.resolve() if args.from_directory else None
    if source:
        require(source.is_dir(), 'offline source is not a directory')
        require(not out.is_relative_to(source) and not source.is_relative_to(out),
                'offline input and output cannot contain one another')
        for row in selected:
            candidate = source / row['name']
            require(candidate.is_file() and not candidate.is_symlink(), 'offline input missing or symlink')
    elif args.transport == 'gh':
        require(shutil.which('gh') is not None, 'GitHub CLI not found')

    out.mkdir(exist_ok=False)
    receipt = {
        'status': 'STARTED',
        'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'repository': REPOSITORY,
        'tag': TAG,
        'manifest_sha256': hash_file(args.manifest),
        'transport': 'offline-copy' if source else args.transport,
        'scope': 'all-eleven-archives' if len(selected) == 11 else 'selected-assets-only',
        'requested_assets': selected_names,
        'verified_assets': [],
        'mathematical_replay_performed': False,
    }
    exit_code = 0
    try:
        for row in selected:
            target = out / row['name']
            if source:
                # Exclusive output creation avoids overwriting even if another
                # process unexpectedly writes into the new output directory.
                with (source / row['name']).open('rb') as inp, target.open('xb') as dest:
                    shutil.copyfileobj(inp, dest, length=1024 * 1024)
            elif args.transport == 'gh':
                command = ['gh', 'release', 'download', TAG, '--repo', REPOSITORY,
                           '--pattern', row['name'], '--dir', str(out)]
                result = subprocess.run(command, capture_output=True, text=True, errors='replace')
                # gh errors may contain temporary signed URLs. Never copy its
                # raw output into the public-facing verification receipt.
                require(result.returncode == 0, 'GitHub CLI download failed; inspect connectivity and access')
            else:
                fetch_https(row, target)
            actual = verify_file(target, row)
            receipt['verified_assets'].append({'name': row['name'], 'bytes': row['bytes'], 'sha256': actual})
            print(f'VERIFIED {row["name"]}')
        receipt['status'] = 'ALL_REQUESTED_FILES_VERIFIED'
    except Exception as error:
        receipt['status'] = 'FAILED_PARTIAL_OUTPUT_RETAINED'
        receipt['error_type'] = type(error).__name__
        # Only our own fixed validation messages are printed; HTTP errors can
        # contain signed redirect URLs and therefore are deliberately redacted.
        receipt['message'] = str(error) if isinstance(error, ValueError) else 'Download failed; raw network details omitted.'
        print(receipt['message'], file=sys.stderr)
        exit_code = 1
    finally:
        receipt['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        (out / 'download-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    return exit_code


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        print(f'Cannot start: {type(error).__name__}: {error}', file=sys.stderr)
        raise SystemExit(2)
