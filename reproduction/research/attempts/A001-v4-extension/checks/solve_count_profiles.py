"""按五个玩家的输出计数完整分支；每个分支保存原始 CNF 与 RUP 证书。"""
import argparse,collections,hashlib,itertools,json,platform,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[5]/'.research-deps'))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'A003-complete-sat/checks'))
from encode import build
from pysat.card import CardEnc,EncType
from pysat.solvers import Solver


def profiles(weight):
    result=set()
    for first in itertools.product(range(17),repeat=4):
        a=first+(weight-sum(first),)
        if not 0<=a[-1]<=16:continue
        sums=[a[j]+a[(j+1)%5] for j in range(5)]
        if min(sums)<6:continue
        if any(sums[j]==6 and a[j] not in(0,2,3,4,6) for j in range(5)):continue
        if any(sums[j-1]==sums[j]==6 and a[j] not in(0,4) for j in range(5)):continue
        options=[v[j:]+v[:j] for v in(a,a[::-1]) for j in range(5)]
        result.add(min(options,key=lambda v:(v[0]+v[1],v)))
    return sorted(result)


def make_model(profile):
    vs,clauses,_=build(5,False);ids={v:k for k,v in enumerate(vs,1)};nv=len(vs);groups=[]
    original=[0]*5
    for i,n in zip((0,2,4,1,3),profile):original[i]=n
    for i,n in enumerate(original,1):
        inputs=[ids[i,a,b,5] for a in range(1,5) for b in range(1,5)]
        start=len(clauses);previous=nv
        card=CardEnc.equals(lits=inputs,bound=n,top_id=nv,encoding=EncType.seqcounter)
        clauses+=card.clauses;nv=max(nv,card.nv)
        groups.append({'player':i,'count':n,'inputs':inputs,'first_clause':start,'end_clause':len(clauses),
                       'first_aux':previous+1,'last_aux':nv})
    clauses.append([ids[1,5,5,1]])
    return clauses,nv,groups,original


def solve_one(profile,out,budget):
    out.mkdir(parents=True,exist_ok=False);clauses,nv,groups,original=make_model(profile)
    cnf=f'p cnf {nv} {len(clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses)
    (out/'instance.cnf').write_text(cnf,encoding='ascii')
    (out/'groups.json').write_text(json.dumps(groups),encoding='ascii')
    start=time.monotonic()
    with Solver(name='g3',bootstrap_with=clauses,with_proof=True) as solver:
        solver.conf_budget(budget);answer=solver.solve_limited();stats=solver.accum_stats()
        if answer is False:
            proof=solver.get_proof()
            if not proof or proof[-1].strip()!='0':proof.append('0')
            (out/'proof.drup').write_text('\n'.join(proof)+'\n',encoding='ascii')
        elif answer is True:(out/'model.json').write_text(json.dumps(solver.get_model()),encoding='ascii')
    report={'profile_cycle_order':profile,'counts_original_order':original,
            'status':{True:'SAT_PENDING_STRATEGY_CHECK',False:'UNSAT_PENDING_CERTIFICATE_CHECK',None:'UNKNOWN'}[answer],
            'stats':stats,'seconds':time.monotonic()-start,'variables':nv,'clauses':len(clauses),
            'cnf_sha256':hashlib.sha256(cnf.encode()).hexdigest()}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--weight',type=int,default=20)
    p.add_argument('--conflicts',type=int,default=1000000);p.add_argument('--profile')
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.profile:
        result=solve_one(tuple(map(int,args.profile.split(','))),args.output,args.conflicts)
        print(json.dumps(result),flush=True);return
    args.output.mkdir(parents=True,exist_ok=False);types=profiles(args.weight)
    (args.output/'profiles.json').write_text(json.dumps(types),encoding='ascii')
    records=[];start=time.monotonic()
    for k,profile in enumerate(types):
        directory=args.output/f'profile-{k:03d}'
        command=[sys.executable,str(Path(__file__)), '--profile',','.join(map(str,profile)),
                 '--conflicts',str(args.conflicts),'--output',str(directory)]
        done=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',
                            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        (directory/'console.txt').write_text(done.stdout+'\n'+done.stderr,encoding='utf-8')
        report=json.loads((directory/'report.json').read_text(encoding='utf-8'))
        report.update(index=k,exit_code=done.returncode);records.append(report)
        print('profile',k,profile,report['status'],'seconds',round(report['seconds'],3),flush=True)
    report={'date_beijing':'2026-10-25','weight':args.weight,'profiles':len(types),
            'statuses':dict(collections.Counter(r['status'] for r in records)),
            'nonzero_exit_codes':sum(r['exit_code']!=0 for r in records),'seconds':time.monotonic()-start,
            'python':platform.python_version(),'solver':'g3','conflict_budget_each':args.conflicts,
            'records':records,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope':'原始求解输出；仍须计数类型完整性、计数编码及每份证书的独立核验。'}
    (args.output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
