"""按五个 f_i(5,5) 的颜色相等模式完整分支；原输入及旧报告保留。"""
import argparse,collections,hashlib,json,platform,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[5]/'.research-deps'))
from pysat.solvers import Solver
from audit_count_profiles_native import read_cnf

def patterns(prefix=(1,)):
    if len(prefix)==5:
        yield prefix;return
    for x in range(1,min(4,max(prefix)+1)+1):yield from patterns(prefix+(x,))

def solve(parent,pattern,out,budget):
    out.mkdir(parents=True,exist_ok=False);nv,base=read_cnf(parent/'instance.cnf')
    variables=[(i,a,b,g) for i in range(1,6) for a in range(1,6) for b in range(1,6)
               for g in range(1,6) if g not in(a,b)]
    ids={v:k for k,v in enumerate(variables,1)}
    units=[[ids[i,5,5,g]] for i,g in enumerate(pattern,1)];clauses=base+units
    cnf=f'p cnf {nv} {len(clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses)
    (out/'instance.cnf').write_text(cnf,encoding='ascii',newline='\n');start=time.monotonic()
    with Solver(name='g3',bootstrap_with=clauses,with_proof=True) as solver:
        solver.conf_budget(budget);answer=solver.solve_limited();stats=solver.accum_stats()
        if answer is False:
            proof=solver.get_proof()
            if not proof or proof[-1].strip()!='0':proof.append('0')
            (out/'proof.drup').write_text('\n'.join(proof)+'\n',encoding='ascii',newline='\n')
        elif answer is True:(out/'model.json').write_text(json.dumps(solver.get_model()),encoding='ascii')
    report={'diagonal_pattern':pattern,'status':{True:'SAT_PENDING_STRATEGY_CHECK',False:'UNSAT_PENDING_CERTIFICATE_CHECK',None:'UNKNOWN'}[answer],
            'variables':nv,'clauses':len(clauses),'stats':stats,'seconds':time.monotonic()-start,
            'cnf_sha256':hashlib.sha256((out/'instance.cnf').read_bytes()).hexdigest()}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('parent',type=Path)
    p.add_argument('--conflicts',type=int,default=300000);p.add_argument('--pattern');args=p.parse_args()
    if args.pattern:
        pattern=tuple(map(int,args.pattern.split(',')))
        print(json.dumps(solve(args.parent,pattern,args.parent/'diagonal-split'/('case-'+''.join(map(str,pattern))),args.conflicts)));return
    out=args.parent/'diagonal-split';out.mkdir(exist_ok=False);ps=list(patterns());assert len(ps)==51
    (out/'patterns.json').write_text(json.dumps(ps),encoding='ascii');records=[];start=time.monotonic()
    for pattern in ps:
        command=[sys.executable,str(Path(__file__)),str(args.parent),'--conflicts',str(args.conflicts),'--pattern',','.join(map(str,pattern))]
        done=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        child=out/('case-'+''.join(map(str,pattern)))
        (child/'console.txt').write_text(done.stdout+'\n'+done.stderr,encoding='utf-8')
        report=json.loads((child/'report.json').read_text(encoding='utf-8'));report['exit_code']=done.returncode;records.append(report)
        print('diagonal',pattern,report['status'],round(report['seconds'],3),flush=True)
    result={'date_beijing':'2026-10-25','command':sys.argv,'python':platform.python_version(),
            'parent_cnf_sha256':hashlib.sha256((args.parent/'instance.cnf').read_bytes()).hexdigest(),
            'patterns':len(ps),'statuses':dict(collections.Counter(r['status'] for r in records)),
            'nonzero_exit_codes':sum(r['exit_code']!=0 for r in records),'records':records,'seconds':time.monotonic()-start,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope':'原始求解结果；需独立核对 51 种相等模式的覆盖、各子输入及全部证明。'}
    (out/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},ensure_ascii=True))

if __name__=='__main__':main()
