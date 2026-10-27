"""标准库独立核对计数类型、原题 CNF、合法计数赋值的辅助扩展，并重放所有 RUP。"""
import argparse,collections,hashlib,itertools,json,time,subprocess
from pathlib import Path
from rup_check_fast import verify_rup


def read_cnf(path):
    clauses=[];header=None
    for line in path.read_text(encoding='ascii').splitlines():
        if line.startswith('p'):
            _,_,n,m=line.split();header=(int(n),int(m))
        elif line and not line.startswith('c'):
            x=list(map(int,line.split()));assert x[-1]==0 and all(x[:-1]);clauses.append(x[:-1])
    assert header[1]==len(clauses)
    return header[0],clauses


def independent_profiles(weight):
    slack=2*weight-30;vectors=[];types=set()
    for initial in itertools.product(range(slack+1),repeat=4):
        last=slack-sum(initial)
        if last<0:continue
        s=tuple(6+e for e in initial+(last,));numerator=s[0]-s[1]+s[2]-s[3]+s[4]
        if numerator%2:continue
        a=[numerator//2]
        for j in range(4):a.append(s[j]-a[-1])
        if any(x<0 or x>16 for x in a) or sum(a)!=weight:continue
        if any(s[j]==6 and a[j] not in(0,2,3,4,6) for j in range(5)):continue
        if any(s[j-1]==s[j]==6 and a[j] not in(0,4) for j in range(5)):continue
        a=tuple(a);vectors.append(a)
        opts=[b[j:]+b[:j] for b in(a,a[::-1]) for j in range(5)]
        types.add(min(opts,key=lambda b:(b[0]+b[1],b)))
    return sorted(types),len(vectors)


def audit_horn_extension(clauses,count):
    # 输入为 1..16。输入固定后，辅助变量上的子句必须是 Horn 子句。
    for clause in clauses:assert sum(x>16 for x in clause)<=1
    tested=0
    for positions in itertools.combinations(range(1,17),count):
        true_inputs=set(positions);rules=[]
        for clause in clauses:
            if any((x in true_inputs if x>0 else -x not in true_inputs) for x in clause if abs(x)<=16):continue
            aux=[x for x in clause if abs(x)>16]
            head=next((x for x in aux if x>0),None)
            rules.append(([-x for x in aux if x<0],head))
        true_aux=set();changed=True
        while changed:
            changed=False
            for body,head in rules:
                if all(x in true_aux for x in body):
                    assert head is not None,('valid count has no extension',count,positions)
                    if head not in true_aux:true_aux.add(head);changed=True
        true=true_inputs|true_aux
        assert all(any((x in true) if x>0 else (-x not in true) for x in c) for c in clauses)
        tested+=1
    return tested


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path)
    p.add_argument('--weight',type=int,required=True);args=p.parse_args();start=time.monotonic()
    listed=[tuple(v) for v in json.loads((args.directory/'profiles.json').read_text(encoding='ascii'))]
    expected,vector_count=independent_profiles(args.weight);assert listed==expected
    variables=[(i,a,b,g) for i in range(1,6) for a in range(1,6) for b in range(1,6) for g in range(1,6) if g not in(a,b)]
    ids={v:j for j,v in enumerate(variables,1)};base=[];configs=0
    for i,a,b in itertools.product(range(1,6),repeat=3):
        group=[ids[i,a,b,g] for g in range(1,6) if g not in(a,b)]
        base.append(group);base.extend([[-x,-y] for x,y in itertools.combinations(group,2)])
    for c in itertools.product(range(1,6),repeat=5):
        if all(c[i]!=c[(i+1)%5] for i in range(5)):
            base.append([ids[i+1,c[i-1],c[(i+1)%5],c[i]] for i in range(5)]);configs+=1
    assert len(base)==1595 and configs==1020
    base_set=collections.Counter(tuple(sorted(c)) for c in base)
    counters={};reports=[];bundle=hashlib.sha256()
    for k,profile in enumerate(listed):
        folder=args.directory/f'profile-{k:03d}';nv,clauses=read_cnf(folder/'instance.cnf')
        assert collections.Counter(tuple(sorted(c)) for c in clauses[:1595])==base_set
        groups=json.loads((folder/'groups.json').read_text(encoding='ascii'));assert len(groups)==5
        original=[None]*5
        for i,n in zip((0,2,4,1,3),profile):original[i]=n
        previous_var=400;previous_clause=1595
        for i,g in enumerate(groups,1):
            expected_inputs=[ids[i,a,b,5] for a in range(1,5) for b in range(1,5)]
            assert g['player']==i and g['inputs']==expected_inputs and g['count']==original[i-1]
            assert g['first_clause']==previous_clause and g['first_aux']==previous_var+1
            assert g['last_aux']>=previous_var
            component=clauses[g['first_clause']:g['end_clause']]
            mapping={v:j for j,v in enumerate(expected_inputs,1)}
            mapping.update({v:17+v-g['first_aux'] for v in range(g['first_aux'],g['last_aux']+1)})
            assert all(abs(x) in mapping for c in component for x in c)
            normalized=tuple(tuple((1 if x>0 else -1)*mapping[abs(x)] for x in c) for c in component)
            key=(g['count'],normalized)
            if key not in counters:
                counters[key]=audit_horn_extension(normalized,g['count'])
                print('counter extension audited',g['count'],counters[key],flush=True)
            previous_clause=g['end_clause'];previous_var=g['last_aux']
        assert nv==previous_var and len(clauses)==previous_clause+1 and clauses[-1]==[ids[1,5,5,1]]
        raw=(folder/'proof.drup').read_bytes();bundle.update(raw)
        done=subprocess.run([str(Path(__file__).with_name('RupCheckNative.exe')),
                             str(folder/'instance.cnf'),str(folder/'proof.drup')],
                            capture_output=True,text=True,check=True,
                            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        check=json.loads(done.stdout);reports.append({'profile':k,**check})
        print('profile proof checked',k,check['verified_additions'],flush=True)
    report={'date_beijing':'2026-10-25','status':'ALL_COUNT_PROFILE_INPUTS_AND_RUP_VERIFIED',
            'weight':args.weight,'necessary_count_vectors':vector_count,'count_profiles':len(listed),
            'original_configurations':configs,'original_clauses':len(base),
            'cardinality_components':len(counters),'valid_input_assignments_extended':sum(counters.values()),
            'cardinality_counts_tested':sorted({k[0] for k in counters}),
            'proofs_verified':len(reports),'verified_additions':sum(r['verified_additions'] for r in reports),
            'proof_reports':reports,'proof_bundle_sha256':bundle.hexdigest(),
            'seconds':time.monotonic()-start,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'rup_checker_cs_sha256':hashlib.sha256(Path(__file__).with_name('RupCheckNative.cs').read_bytes()).hexdigest(),
            'rup_checker_exe_sha256':hashlib.sha256(Path(__file__).with_name('RupCheckNative.exe').read_bytes()).hexdigest(),
            'scope':'独立重建计数类型与原题约束；穷举每种合法计数输入并构造辅助扩展，检查不误删真策略；重放全部反证。'}
    (args.directory/'independent-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='proof_reports'},ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
