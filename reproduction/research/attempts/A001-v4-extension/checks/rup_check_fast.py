"""双监视文字实现的 RUP 重放；删除行忽略。与朴素检查器分别实现。"""
class Database:
    def __init__(self,clauses):
        self.clauses=[];self.watch={};self.units=[];self.empty=False
        for clause in clauses:self.add(clause)

    def add(self,clause):
        clause=list(dict.fromkeys(clause))
        if any(-x in clause for x in clause):return
        if not clause:self.empty=True;return
        if len(clause)==1:self.units.append(clause[0]);return
        index=len(self.clauses);self.clauses.append(clause)
        self.watch.setdefault(clause[0],[]).append(index)
        self.watch.setdefault(clause[1],[]).append(index)

    def conflict(self,assumptions=()):
        if self.empty:return True
        values={};queue=[]
        def enqueue(lit):
            var=abs(lit);val=lit>0
            if var in values:return values[var]==val
            values[var]=val;queue.append(lit);return True
        def val(lit):
            if abs(lit) not in values:return None
            return values[abs(lit)]==(lit>0)
        for lit in self.units:
            if not enqueue(lit):return True
        for lit in assumptions:
            if not enqueue(lit):return True
        head=0
        while head<len(queue):
            false=-queue[head];head+=1
            watching=self.watch.get(false,[])
            k=0
            while k<len(watching):
                index=watching[k];clause=self.clauses[index]
                if clause[0]==false:clause[0],clause[1]=clause[1],clause[0]
                assert clause[1]==false
                other=clause[0]
                if val(other) is True:k+=1;continue
                replacement=next((j for j in range(2,len(clause)) if val(clause[j]) is not False),None)
                if replacement is not None:
                    clause[1],clause[replacement]=clause[replacement],clause[1]
                    watching[k]=watching[-1];watching.pop()
                    self.watch.setdefault(clause[1],[]).append(index)
                else:
                    if not enqueue(other):return True
                    k+=1
        return False


def verify_rup(initial,lines):
    db=Database(initial);additions=0;deletions=0;empty=False
    for n,line in enumerate(lines,1):
        words=line.split()
        if not words or words[0]=='c':continue
        if words[0]=='d':deletions+=1;continue
        ints=list(map(int,words))
        assert ints[-1]==0 and all(ints[:-1])
        clause=ints[:-1]
        assert db.conflict([-x for x in clause]),('non-RUP',n,clause)
        db.add(clause);additions+=1
        if not clause:empty=True
    assert empty,'missing checked empty clause'
    return {'verified_additions':additions,'ignored_deletions':deletions,'empty_clause_verified':True}
