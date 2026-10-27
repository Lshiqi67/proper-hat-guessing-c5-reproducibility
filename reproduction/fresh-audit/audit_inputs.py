"""Fresh read-only audit of P001 classification and actual input CNFs.

Uses Python standard library only. This file imports no historical generator,
auditor, solver, or checking code. All outputs are written beside this file.
"""
from __future__ import annotations

import collections
import datetime
import hashlib
import itertools
import json
import math
import pathlib
import platform
import sys
import time
import traceback

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUTPUTS = ROOT / 'attempts/A001-v4-extension/checks/outputs'
START = time.perf_counter()
SOURCE_HASH = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise AssertionError(message)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write_json(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def legal_configurations(q):
    return [c for c in itertools.product(range(1, q + 1), repeat=5)
            if all(c[i] != c[(i + 1) % 5] for i in range(5))]


def base_model():
    variables = {}
    clauses = []
    for i, left, right in itertools.product(range(1, 6), repeat=3):
        choices = []
        for answer in range(1, 6):
            if answer != left and answer != right:
                v = len(variables) + 1
                variables[i, left, right, answer] = v
                choices.append(v)
        clauses.append(tuple(choices))
        clauses.extend((-a, -b) for a, b in itertools.combinations(choices, 2))
    require(len(variables) == 400 and len(clauses) == 575, 'base selection size')
    configurations = legal_configurations(5)
    require(len(configurations) == 1020, 'proper configuration count')
    for c in configurations:
        clauses.append(tuple(variables[i + 1, c[(i - 1) % 5], c[(i + 1) % 5], c[i]]
                             for i in range(5)))
    require(len(clauses) == 1595, 'base formula size')
    return variables, tuple(clauses)


def normal_clause(clause):
    return tuple(sorted(clause))


def cnf(path):
    raw = path.read_bytes()
    header = None
    pending = []
    clauses = []
    for line in raw.decode('ascii').splitlines():
        line = line.strip()
        if not line or line.startswith('c'):
            continue
        if line.startswith('p'):
            require(header is None and not clauses and not pending, f'duplicate/late header: {path}')
            words = line.split()
            require(len(words) == 4 and words[:2] == ['p', 'cnf'], f'invalid header: {path}')
            header = int(words[2]), int(words[3])
            require(header[0] >= 0 and header[1] >= 0, f'negative header: {path}')
            continue
        require(header is not None, f'missing header: {path}')
        for token in line.split():
            lit = int(token)
            if lit == 0:
                clauses.append(tuple(pending))
                pending = []
            else:
                require(abs(lit) <= header[0], f'literal out of range: {path}')
                pending.append(lit)
    require(header is not None and not pending, f'unterminated CNF: {path}')
    require(len(clauses) == header[1], f'clause count mismatch: {path}')
    return header[0], tuple(clauses), hashlib.sha256(raw).hexdigest()


def classify():
    allowable = {(0, 6), (2, 4), (3, 3), (4, 2), (6, 0)}
    vectors = {n: [] for n in range(17, 26)}
    representatives = {n: set() for n in range(17, 26)}
    # Direct scan of every vector in [0,16]^5, not the previous slack algorithm.
    for a in itertools.product(range(17), repeat=5):
        n = sum(a)
        if n not in vectors:
            continue
        pairs = tuple(a[i] + a[(i + 1) % 5] for i in range(5))
        if min(pairs) < 6:
            continue
        if any(pairs[i] == 6 and (a[i], a[(i + 1) % 5]) not in allowable for i in range(5)):
            continue
        if any(pairs[(i - 1) % 5] == pairs[i] == 6 and a[i] not in (0, 4) for i in range(5)):
            continue
        orbit = [tuple(a[(offset + sign * j) % 5] for j in range(5))
                 for sign in (-1, 1) for offset in range(5)]
        chosen = min(orbit, key=lambda b: (b[0] + b[1], b))
        vectors[n].append(a)
        representatives[n].add(chosen)
    summary = []
    for n in vectors:
        recorded = [tuple(a) for a in read_json(OUTPUTS / f'weight{n}-count-profiles/profiles.json')]
        expected = sorted(representatives[n])
        require(recorded == expected, f'count representative mismatch, weight {n}')
        summary.append({'weight': n, 'vectors': len(vectors[n]), 'representatives': len(expected)})
    require(sum(len(v) for v in representatives.values()) == 1413, 'total representatives')
    words = set()
    for raw in itertools.product(range(1, 5), repeat=5):
        labels = {}
        canon = []
        for x in raw:
            if x not in labels:
                labels[x] = len(labels) + 1
            canon.append(labels[x])
        words.add(tuple(canon))
    recursive = {(1,)}
    for _ in range(4):
        recursive = {prefix + (x,) for prefix in recursive
                     for x in range(1, min(4, max(prefix) + 1) + 1)}
    require(words == recursive and len(words) == 51, 'diagonal classes')
    return {n: sorted(v) for n, v in representatives.items()}, sorted(words), summary


def component_check(component, target):
    """Check extension for every input of the requested Hamming weight.

    A component uses inputs 1..16 and auxiliaries >=17. Clauses become Horn
    after substituting inputs. Least-model closure is computed with Python
    integer bitsets; the original full clauses are then evaluated directly.
    """
    rules = []
    evaluations = []
    for clause in component:
        p_in = n_in = p_aux = n_aux = 0
        for lit in clause:
            v = abs(lit)
            bit = 1 << (v - 1)
            if v <= 16:
                if lit > 0:
                    p_in |= bit
                else:
                    n_in |= bit
            elif lit > 0:
                p_aux |= bit
            else:
                n_aux |= bit
        require(p_aux.bit_count() <= 1, 'non-Horn auxiliary residual')
        rules.append((p_in, n_in, n_aux, p_aux))
        evaluations.append((p_in | p_aux, n_in | n_aux))
    checked = 0
    for chosen in itertools.combinations(range(16), target):
        assignment = sum(1 << i for i in chosen)
        residual = [(body, head) for pi, ni, body, head in rules
                    if not (pi & assignment or ni & ~assignment)]
        changed = True
        while changed:
            changed = False
            for body, head in residual:
                if body & assignment == body:
                    require(head != 0, f'no extension for target {target}, input {chosen}')
                    if not assignment & head:
                        assignment |= head
                        changed = True
        # Direct clause evaluation, not merely trusting the closure result.
        for pos, neg in evaluations:
            require(pos & assignment or neg & ~assignment,
                    f'constructed assignment violates clause, count {target}, input {chosen}')
        require((assignment & 65535).bit_count() == target, 'closure changed an input')
        checked += 1
    require(checked == math.comb(16, target), 'legal input enumeration count')
    return checked


def symmetry_checks(variables, base):
    expected = collections.Counter(map(normal_clause, base))
    reverse = {v: key for key, v in variables.items()}
    for perm in itertools.permutations(range(1, 5)):
        color = {i + 1: perm[i] for i in range(4)} | {5: 5}
        mapping = {v: variables[i, color[l], color[r], color[g]] for (i, l, r, g), v in variables.items()}
        transformed = collections.Counter(tuple(sorted((1 if x > 0 else -1) * mapping[abs(x)] for x in c)) for c in base)
        require(transformed == expected, 'color action does not preserve base')
        for i in range(1, 6):
            group = {variables[i, l, r, 5] for l, r in itertools.product(range(1, 5), repeat=2)}
            require({mapping[v] for v in group} == group, 'color action changes a count group')
    for sign in (-1, 1):
        for shift in range(5):
            mapping = {}
            for v, (i, l, r, g) in reverse.items():
                dest = (shift + sign * (i - 1)) % 5 + 1
                mapping[v] = variables[dest, l, r, g] if sign == 1 else variables[dest, r, l, g]
            transformed = collections.Counter(tuple(sorted((1 if x > 0 else -1) * mapping[abs(x)] for x in c)) for c in base)
            require(transformed == expected, 'vertex action does not preserve base')
    return {'color_permutations': 24, 'graph_automorphisms': 10}


def strategy_checks():
    q4 = read_json(ROOT / 'checks/outputs/q4-strategy.json')['tables']
    witness = read_json(OUTPUTS / 'double-layer-bound17/strategy.json')['tables']
    require(len(q4) == len(witness) == 5, 'strategy table count')
    for q, tables in [(4, q4), (5, witness)]:
        for t in tables:
            require(len(t) == q and all(len(row) == q for row in t), 'strategy table dimension')
            require(all(type(g) is int and 1 <= g <= q for row in t for g in row), 'strategy answer domain')
    c4 = legal_configurations(4)
    require(len(c4) == 240, 'four-color configurations')
    for c in c4:
        require(any(q4[i][c[(i - 1) % 5] - 1][c[(i + 1) % 5] - 1] == c[i] for i in range(5)), 'saved four-color strategy loses')
        coords = [((g - 1) >> 1, (g - 1) & 1) for g in c]
        a, b, cc = coords[:3]
        guesses = ((b[0] ^ 1, b[1]), (cc[0] ^ 1, a[1] ^ 1), (b[0], b[1] ^ 1))
        require(any(guesses[i] == coords[i] for i in range(3)), 'displayed four-color formula loses')
    p = [ {(1,2),(2,2)}, {(3,1),(3,3)}, {(1,3),(1,4),(3,3),(3,4)},
          {(1,3),(2,1),(2,2),(2,3),(3,3)}, {(2,2),(2,4),(4,2),(4,4)} ]
    aa = [(3,3,1,1),(3,3,4,1),(2,4,4,2),(2,1,1,2),(2,4,4,1)]
    bb = [(2,4,1,1),(2,4,4,2),(3,4,4,1),(3,3,1,1),(4,3,4,3)]
    tt = [1,4,4,1,4]
    for i, l, r in itertools.product(range(5), range(1,6), range(1,6)):
        displayed = (tt[i] if l == r == 5 else aa[i][r-1] if l == 5 else
                     bb[i][l-1] if r == 5 else 5 if (l,r) in p[i] else
                     min(set(range(1,5)) - {l,r}))
        require(witness[i][l-1][r-1] == displayed, 'appendix table differs from saved strategy')
        require(displayed not in (l,r), 'witness not normalized')
    totals = collections.Counter()
    losses = collections.Counter()
    for c in legal_configurations(5):
        k = c.count(5)
        totals[k] += 1
        if all(witness[i][c[(i-1)%5]-1][c[(i+1)%5]-1] != c[i] for i in range(5)):
            losses[k] += 1
    require([totals[k] for k in range(3)] == [240,540,240], 'layer sizes')
    require([losses[k] for k in range(3)] == [35,55,0], 'local witness loss counts')
    return {'q4_saved_and_formula_configurations': len(c4), 'witness_configurations': 1020,
            'witness_layer_sizes': [totals[k] for k in range(3)], 'witness_layer_losses': [losses[k] for k in range(3)],
            'witness_special_counts': [len(s) for s in p]}


def main():
    report = {'status': 'RUNNING', 'started_at': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
              'source_sha256_at_start': SOURCE_HASH, 'command': [sys.executable, *sys.argv],
              'python': sys.version, 'platform': platform.platform(), 'root': str(ROOT),
              'scope': 'New standard-library implementation: full count classification, actual parent/child inputs, all valid auxiliary extensions, symmetries and explicit strategies. No RUP replay.'}
    write_json('report.json', report)
    try:
        variables, base = base_model()
        base_counter = collections.Counter(map(normal_clause, base))
        representatives, patterns, counts = classify()
        report['classification'] = counts
        report['symmetry'] = symmetry_checks(variables, base)
        report['strategies'] = strategy_checks()
        print('Classification, symmetries and explicit strategies passed.', flush=True)
        branches = read_json(ROOT / 'review/catalog/branches.json')['branches']
        index = {(b['weight'], b['profile']): b for b in branches}
        require(len(index) == len(branches) == 1413, 'branch index duplicates or missing')
        require(set(index) == {(n, k) for n, reps in representatives.items() for k in range(len(reps))}, 'branch index coverage')
        terminal = [json.loads(line) for line in (ROOT / 'review/catalog/terminal-certificates.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
        terminal_index = {(x['weight'], x['profile'], x['case']): x for x in terminal}
        require(len(terminal_index) == len(terminal) == 8613, 'terminal index duplicates or missing')
        expected_terminal = set()
        seen_types = {}
        files = []
        parents = children = 0
        per_weight = []
        for n, reps in representatives.items():
            local_parents = local_children = refined = 0
            for number, a in enumerate(reps):
                branch = index[n, number]
                directory = OUTPUTS / f'weight{n}-count-profiles/profile-{number:03d}'
                require((ROOT / branch['path']).resolve() == directory.resolve(), 'branch path mismatch')
                require(tuple(branch['counts']) == a, 'branch vector mismatch')
                nvars, clauses, digest = cnf(directory / 'instance.cnf')
                require(collections.Counter(map(normal_clause, clauses[:1595])) == base_counter, 'base formula mismatch')
                groups = read_json(directory / 'groups.json')
                require(len(groups) == 5, 'component count')
                prior_end = 1595
                next_aux = 401
                r = [None] * 5
                for j in range(5):
                    r[(2 * j) % 5] = a[j]
                for i, group in enumerate(groups, start=1):
                    require(group['player'] == i and group['count'] == r[i-1], 'component identity/count')
                    expected_inputs = [variables[i,l,rr,5] for l,rr in itertools.product(range(1,5), repeat=2)]
                    require(group['inputs'] == expected_inputs, 'count inputs not semantic special-color group')
                    first, end = group['first_clause'], group['end_clause']
                    low, high = group['first_aux'], group['last_aux']
                    require(first == prior_end and first <= end <= len(clauses), 'component clause boundary')
                    require(low == next_aux and low - 1 <= high <= nvars, 'component auxiliary boundary')
                    rename = {v:j+1 for j,v in enumerate(expected_inputs)}
                    rename.update({v:17+(v-low) for v in range(low,high+1)})
                    component = []
                    for clause in clauses[first:end]:
                        require(all(abs(x) in rename for x in clause), 'component uses unrelated variable')
                        component.append(tuple(sorted((1 if x>0 else -1)*rename[abs(x)] for x in clause)))
                    component = tuple(sorted(component))
                    key = (r[i-1], component)
                    if key not in seen_types:
                        checked = component_check(component, r[i-1])
                        data = {'count':r[i-1], 'valid_inputs_checked':checked, 'clauses':len(component),
                                'auxiliaries':high-low+1, 'component_sha256':hashlib.sha256(repr(component).encode()).hexdigest()}
                        seen_types[key] = data
                        print(f'Component count {r[i-1]} passed {checked} legal inputs.', flush=True)
                    prior_end, next_aux = end, high+1
                require(clauses[prior_end:] == ((variables[1,5,5,1],),), 'parent has unintended trailing constraint')
                require(nvars == next_aux-1, 'parent variable header not exact')
                path = (directory/'instance.cnf').relative_to(ROOT).as_posix()
                files.append({'kind':'parent','weight':n,'profile':number,'path':path,'sha256':digest,'variables':nvars,'clauses':len(clauses)})
                parents += 1
                local_parents += 1
                require(branch['mode'] in ('direct','diagonal-split'), f'unknown branch mode {branch["mode"]}')
                if branch['mode'] == 'direct':
                    require(branch['leaf_count'] == 1, 'direct leaf count')
                    wanted = [(None, directory/'instance.cnf', digest)]
                else:
                    refined += 1
                    require(branch['leaf_count'] == 51, 'split leaf count')
                    wanted = []
                    for pattern in patterns:
                        case = ''.join(map(str,pattern))
                        child = directory/'diagonal-split'/f'case-{case}'/'instance.cnf'
                        nv, cc, dd = cnf(child)
                        required = clauses + tuple((variables[i+1,5,5,pattern[i]],) for i in range(5))
                        require(nv == nvars and cc == required, f'child is not exact parent + pattern units: {child}')
                        wanted.append((case,child,dd))
                        files.append({'kind':'child','weight':n,'profile':number,'case':case,'path':child.relative_to(ROOT).as_posix(),'sha256':dd,'variables':nv,'clauses':len(cc)})
                        children += 1
                        local_children += 1
                for case, filename, hh in wanted:
                    identity = (n,number,case)
                    require(identity in terminal_index, f'missing adopted terminal {identity}')
                    item = terminal_index[identity]
                    require((ROOT/item['cnf']).resolve() == filename.resolve(), 'terminal CNF path')
                    require(item['cnf_sha256'] == hh, 'terminal input hash')
                    require((ROOT/item['proof']).resolve() == filename.with_name('proof.drup').resolve(), 'terminal proof path')
                    require((ROOT/item['proof']).is_file(), 'terminal proof missing')
                    expected_terminal.add(identity)
            per_weight.append({'weight':n,'parents':local_parents,'refined':refined,'children':local_children})
            print(f'Weight {n}: {local_parents} parents, {local_children} children passed.', flush=True)
        require(expected_terminal == set(terminal_index), 'adopted terminal set mismatch')
        require(parents == 1413 and children == 7344, 'complete input totals')
        (HERE/'input-files.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in files),encoding='utf-8')
        report.update({'status':'PASSED_FOR_RECORDED_SCOPE','base_variables':len(variables),'base_clauses':len(base),
                       'parent_inputs':parents,'child_inputs':children,'terminal_inputs':len(expected_terminal),
                       'per_weight':per_weight,'component_types':sorted(seen_types.values(),key=lambda x:(x['count'],x['component_sha256'])),
                       'valid_auxiliary_inputs':sum(v['valid_inputs_checked'] for v in seen_types.values()),
                       'random_seed':None,'no_old_program_imports':True,'no_old_success_cache_used':True})
        require(len(seen_types)==14 and report['valid_auxiliary_inputs']==65399, 'component totals differ from paper')
    except Exception:
        report['status']='FAILED_OR_INCOMPLETE'
        report['error']=traceback.format_exc()
        raise
    finally:
        report['elapsed_seconds']=time.perf_counter()-START
        report['source_sha256_at_end']=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
        report['source_unchanged']=report['source_sha256_at_end']==SOURCE_HASH
        write_json('report.json',report)
    print(json.dumps({'status':report['status'],'parents':parents,'children':children,'valid_auxiliary_inputs':report['valid_auxiliary_inputs'],'seconds':report['elapsed_seconds']}),flush=True)


if __name__ == '__main__':
    main()
