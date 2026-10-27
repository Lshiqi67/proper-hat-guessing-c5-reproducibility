"""Offline, explicit-path verification entry point for the v2 local deposit.

Original audit sources remain byte-for-byte unchanged. This adapter only selects
paths, protects old records, builds the checker, and checks complete coverage.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import sys
import time
import traceback
import zipfile

VERSION = 'c5-reviewed-evidence-20261027-v2'
CSC = r'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe'
FRESH_HASH = 'fa991db895021be9f4fc50ca010fb221d05d850f398c38c1c2c3615f8c58dd63'
INPUT_HASH = 'af9524fbc6a4507a025db436678f774d1555af0a35988bc46fbebcc3ab1598df'


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def lines(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8-sig').splitlines() if x.strip()]


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def safe_path(root, name):
    pp = PurePosixPath(name)
    require(not pp.is_absolute() and pp.parts and all(x not in ('.', '..') for x in pp.parts), 'unsafe relative path')
    require('\\' not in name and ':' not in name, 'unsafe portable path')
    target = root.joinpath(*pp.parts)
    require(target.resolve().is_relative_to(root), 'path escapes root')
    return target


def verify_file(path, row, size_key='bytes', hash_key='sha256'):
    require(path.is_file(), f'missing file: {path}')
    require(path.stat().st_size == row[size_key], f'wrong size: {path}')
    actual = digest(path)
    require(actual == row[hash_key], f'wrong SHA-256: {path}')
    return actual


def code_integrity(root):
    manifest = read(root / 'MANIFEST.json')
    require(manifest['version'] == VERSION, 'wrong code manifest version')
    names = [r['path'] for r in manifest['files']]
    require(len(names) == len(set(names)), 'duplicate code manifest path')
    for row in manifest['files']:
        verify_file(safe_path(root, row['path']), row)
    require(digest(root/'fresh-audit/FreshRup.cs') == FRESH_HASH, 'frozen RUP source mismatch')
    require(digest(root/'fresh-audit/audit_inputs.py') == INPUT_HASH, 'frozen input source mismatch')
    return len(names)


def complete_inventory(root):
    selected = lines(root/'fresh-audit/selected-leaves.jsonl')
    catalog = lines(root/'research/review/catalog/terminal-certificates.jsonl')
    branches = read(root/'research/review/catalog/branches.json')['branches']
    evidence = lines(root/'evidence/files.jsonl')
    identity = lambda r: (r['weight'], r['profile'], r['case'])
    ids = [identity(r) for r in selected]
    require(len(ids) == len(set(ids)), 'duplicate selected terminal identity')
    cid = [identity(r) for r in catalog]
    require(len(cid) == len(set(cid)) and set(cid) == set(ids), 'catalog is not the exact selected terminal set')
    cm = {identity(r):r for r in catalog}
    branch_ids = [(b['weight'], b['profile']) for b in branches]
    require(len(branch_ids) == len(set(branch_ids)) == 1413, 'invalid parent identity set')
    require(set(b['weight'] for b in branches) == set(range(17,26)), 'missing parent weight')
    bm = {(b['weight'], b['profile']): b for b in branches}
    patterns = []
    for p in itertools.product(range(1,5), repeat=5):
        rename = {}
        norm = tuple(rename.setdefault(x, len(rename)+1) for x in p)
        if p == norm:
            patterns.append(''.join(map(str,p)))
    require(len(patterns) == 51, 'diagonal orbit count')
    wanted = set()
    for b in branches:
        require(b['mode'] in ('direct','diagonal-split'), 'unknown branch mode')
        cases = [None] if b['mode'] == 'direct' else patterns
        require(b['leaf_count'] == len(cases), 'incorrect branch leaf count')
        wanted.update((b['weight'], b['profile'], c) for c in cases)
    require(set(ids) == wanted and len(wanted) == 8613, 'terminal set lacks exact branch/case coverage')
    em = {r['path']:r for r in evidence}
    require(len(em) == len(evidence), 'duplicate evidence manifest path')
    terminal_paths = set()
    leaf_ids = set()
    for row in selected:
        b = bm[row['weight'],row['profile']]
        suffix = 'direct' if row['case'] is None else row['case']
        lid = f"{row['weight']}/{row['profile']:03d}/{suffix}"
        require(row['leaf_id'] == lid and lid not in leaf_ids, 'invalid or duplicate leaf_id')
        leaf_ids.add(lid)
        require(row['mode'] == b['mode'], 'leaf mode differs from parent')
        folder = b['path']
        if row['case'] is not None:
            folder += '/diagonal-split/case-' + row['case']
        for kind, filename in [('cnf','instance.cnf'), ('proof','proof.drup')]:
            require(row[kind] == folder+'/'+filename, 'terminal path differs from branch')
            for key in [kind, kind+'_bytes', kind+'_sha256']:
                require(row[key] == cm[identity(row)][key], 'catalog/fresh-selection disagreement')
            path = 'research/'+row[kind]
            require(path not in terminal_paths and path in em, 'missing or duplicate terminal file')
            terminal_paths.add(path)
            require(em[path]['bytes'] == row[kind+'_bytes'] and em[path]['sha256'] == row[kind+'_sha256'], 'old ZIP manifest/fresh selection disagreement')
    require(terminal_paths == {r['path'] for r in evidence if r['role'] in ('terminal-cnf','terminal-proof')}, 'evidence terminal role coverage mismatch')
    return selected, evidence


def restore(args, root, out, evidence):
    archive_root = Path(args.archives).resolve()
    require(archive_root.is_dir(), 'archive directory missing')
    weights = set(range(17,26)) if args.full else {args.weight}
    assets = read(root/'evidence/assets.json')['assets']
    chosen = [a for a in assets if a['weight'] in weights]
    require({a['weight'] for a in chosen} == weights, 'archive weight missing')
    expected = [r for r in evidence if r['weight'] in weights]
    for row in expected:
        target = safe_path(root,row['path'])
        require(not target.exists(), f'restore refuses existing evidence file: {target}')
        require(os.name != 'nt' or len(str(target)) <= 235, 'choose a shorter extraction root (235-character limit)')
    actual_rows = []
    for a in chosen:
        archive = safe_path(archive_root,a['name'])
        verify_file(archive,a)
        expected_archive = {r['path']:r for r in expected if r['archive'] == a['name']}
        with zipfile.ZipFile(archive) as z:
            names = [i.filename for i in z.infolist()]
            require(len(names) == len(set(names)) and set(names) == set(expected_archive), 'ZIP member inventory mismatch')
            for info in z.infolist():
                require(not info.is_dir() and ((info.external_attr >> 16) & 0o170000) != 0o120000, 'directories/symlinks are not expected')
                row = expected_archive[info.filename]
                require(info.file_size == row['bytes'], 'ZIP member size mismatch')
                target = safe_path(root,info.filename)
                target.parent.mkdir(parents=True,exist_ok=True)
                h = hashlib.sha256()
                count = 0
                with z.open(info) as source, target.open('xb') as dest:
                    while chunk := source.read(1024*1024):
                        h.update(chunk)
                        count += len(chunk)
                        dest.write(chunk)
                require(count == row['bytes'] and h.hexdigest() == row['sha256'], f'ZIP member content mismatch: {info.filename}')
                actual_rows.append({'path':info.filename,'archive':a['name'],'bytes':count,'sha256':h.hexdigest()})
        print(f"Restored and checked weight {a['weight']}: {len(expected_archive)} files.",flush=True)
    (out/'member-readback.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in actual_rows),encoding='utf-8')
    return {'weights':sorted(weights),'restored_files':len(actual_rows),'restored_bytes':sum(r['bytes'] for r in actual_rows),'archive_sha256_checked':True,'exact_member_inventory_checked':True,'every_member_sha256_and_crc_checked':True,'terminal_hashes_cross_checked_to_20261027_selection':True}


def inputs(root, out):
    source = root/'fresh-audit/audit_inputs.py'
    require(digest(source) == INPUT_HASH, 'wrong input auditor')
    spec = importlib.util.spec_from_file_location('frozen_c5_input_auditor',source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root/'research'
    module.OUTPUTS = module.ROOT/'attempts/A001-v4-extension/checks/outputs'
    module.HERE = out
    module.START = time.perf_counter()
    module.main()
    require(digest(source) == INPUT_HASH, 'input source changed')
    result = read(out/'report.json')
    require(result['status'] == 'PASSED_FOR_RECORDED_SCOPE', 'input audit incomplete')
    return {'source_sha256':INPUT_HASH,'adapter_changes':['ROOT','OUTPUTS','HERE','START timer only'],'audit_report':'report.json','parent_inputs':result['parent_inputs'],'child_inputs':result['child_inputs'],'valid_auxiliary_inputs':result['valid_auxiliary_inputs'],'proof_inferences_replayed':False}


def replay(args, root, out, selected):
    if args.full:
        require(args.weight is None and args.profile is None and args.limit is None, '--full cannot be narrowed')
        chosen = selected
    else:
        require(args.weight is not None, 'partial replay requires --weight')
        chosen = [r for r in selected if r['weight'] == args.weight and (args.profile is None or r['profile'] == args.profile)]
        if args.limit is not None:
            require(args.limit > 0, 'limit must be positive')
            chosen = chosen[:args.limit]
    require(chosen, 'no selected leaves')
    ids = [r['leaf_id'] for r in chosen]
    require(len(ids) == len(set(ids)), 'duplicate replay identity')
    for row in chosen:
        for kind in ('cnf','proof'):
            verify_file(safe_path(root/'research',row[kind]),row,kind+'_bytes',kind+'_sha256')
    (out/'selected-leaves.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in chosen),encoding='utf-8')
    compiler = Path(args.csc).resolve()
    require(compiler.is_file(), 'C# compiler missing; pass --csc')
    exe = out/'FreshRup.exe'
    cmd = [str(compiler),'/nologo','/optimize+','/out:'+str(exe),str(root/'fresh-audit/FreshRup.cs')]
    compile_result = subprocess.run(cmd,capture_output=True,text=True,errors='replace')
    (out/'compiler.stdout.txt').write_text(compile_result.stdout,encoding='utf-8')
    (out/'compiler.stderr.txt').write_text(compile_result.stderr,encoding='utf-8')
    require(compile_result.returncode == 0 and exe.is_file(), 'checker compilation failed')
    batch = out/'batch.tsv'
    batch.write_text(''.join(f"{r['leaf_id']}\t{root/'research'/r['cnf']}\t{root/'research'/r['proof']}\n" for r in chosen),encoding='utf-8')
    invocation = [str(exe),'--batch',str(batch),str(out/'replay.tsv')]
    with (out/'checker.stdout.txt').open('w',encoding='utf-8') as stdout, (out/'checker.stderr.txt').open('w',encoding='utf-8') as stderr:
        completed = subprocess.run(invocation,stdout=stdout,stderr=stderr)
    require(completed.returncode == 0, 'proof replay failed; inspect checker.stderr.txt')
    records = [line.split('\t') for line in (out/'replay.tsv').read_text(encoding='utf-8').splitlines()]
    require(all(len(r) == 5 for r in records), 'malformed checker result')
    got = [r[0] for r in records]
    require(len(got) == len(set(got)) and set(got) == set(ids), 'missing, extra or duplicated checker result identity')
    require(got == ids, 'checker result order differs from the submitted batch')
    require(all(r[2] == 'true' for r in records), 'unchecked empty clause')
    expected_by_id = {r['leaf_id']:r for r in chosen}
    require(all(int(r[1]) == expected_by_id[r[0]]['verified_additions_recorded'] for r in records), 'per-leaf addition count differs from archive record')
    additions = sum(int(r[1]) for r in records)
    require(additions == sum(r['verified_additions_recorded'] for r in chosen), 'actual addition totals differ from archive records')
    if args.full:
        require(set(got) == {r['leaf_id'] for r in selected} and len(got) == 8613 and additions == 66403934, 'full replay coverage/totals mismatch')
    return {'scope':'FULL_EXACT_TERMINAL_SET' if args.full else 'EXPLICIT_PARTIAL_SET','leaves':len(got),'additions':additions,'checked_empty_clauses':len(got),'deletion_records_parsed_and_ignored':sum(int(r[4]) for r in records),'checker_source_sha256':digest(root/'fresh-audit/FreshRup.cs'),'compiled_executable_sha256':digest(exe),'compiler_command':cmd,'replay_command':invocation,'exact_unique_identity_coverage_checked':True,'old_success_cache_used':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['integrity','restore','inputs','replay'])
    parser.add_argument('--root',required=True,help='extracted v2 package root (explicit input root)')
    parser.add_argument('--out',required=True,help='new output directory outside the package')
    parser.add_argument('--archives',help='local evidence ZIP directory; restore only')
    parser.add_argument('--full',action='store_true')
    parser.add_argument('--weight',type=int,choices=range(17,26))
    parser.add_argument('--profile',type=int)
    parser.add_argument('--limit',type=int)
    parser.add_argument('--csc',default=CSC)
    args = parser.parse_args()
    require(sys.version_info >= (3,11), 'Python 3.11+ required')
    require(not sys.flags.optimize, 'do not run Python with -O')
    root = Path(args.root).resolve()
    out = Path(args.out).resolve()
    require(read(root/'VERSION.json')['version'] == VERSION, 'not a v2 package root')
    require(not out.exists(), 'output directory must not exist')
    require(not out.is_relative_to(root) and not root.is_relative_to(out), 'output directory must be outside and not contain the input package')
    require(all(c not in str(root)+str(out) for c in '\t\r\n'), 'paths must not contain tabs or newlines')
    out.mkdir(parents=True,exist_ok=False)
    started = time.perf_counter()
    report = {'status':'FAILED_OR_INCOMPLETE','command':sys.argv,'version':VERSION,'started_at':datetime.datetime.now().astimezone().isoformat(),'root':str(root),'out':str(out),'python':sys.version,'platform':platform.platform(),'network_access_required':False}
    try:
        report['code_files_checked'] = code_integrity(root)
        selected,evidence = complete_inventory(root)
        report['catalog_terminal_count'] = len(selected)
        report['exact_unique_full_inventory_checked'] = True
        if args.command == 'restore':
            require(args.archives and (args.full != (args.weight is not None)), 'restore needs --archives and exactly one of --full / --weight')
            report['result'] = restore(args,root,out,evidence)
        elif args.command == 'inputs':
            report['result'] = inputs(root,out)
        elif args.command == 'replay':
            report['result'] = replay(args,root,out,selected)
        else:
            if args.full:
                for row in evidence:
                    verify_file(safe_path(root,row['path']),row)
            report['result'] = {'code_integrity_passed':True,'evidence_files_hashed':len(evidence) if args.full else 0,'proof_inferences_replayed':False}
        report['status'] = 'PASSED_FOR_RECORDED_SCOPE'
    except Exception:
        report['error'] = traceback.format_exc()
        raise
    finally:
        report['elapsed_seconds'] = time.perf_counter()-started
        report['finished_at'] = datetime.datetime.now().astimezone().isoformat()
        write(out/'wrapper-report.json',report)
    print(json.dumps(report['result'],ensure_ascii=False),flush=True)


if __name__ == '__main__':
    main()
