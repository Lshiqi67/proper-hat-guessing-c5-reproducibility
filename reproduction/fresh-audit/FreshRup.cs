// Independent implementation written 2026-10-27 without reading earlier checker sources.
// RUP additions only. Deletions are parsed, then ignored: all established consequences remain.
using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;

sealed class Engine {
    readonly int n;
    readonly sbyte[] values;
    readonly List<int>[] watches;
    readonly List<int[]> clauses = new List<int[]>();
    readonly List<int> trail = new List<int>();
    readonly int[] seen;
    int epoch, head;
    public bool RootConflict;
    public Engine(int count) {
        n=count; values=new sbyte[n+1]; seen=new int[n+1];
        watches=new List<int>[2*(n+1)];
        for(int i=0;i<watches.Length;i++) watches[i]=new List<int>();
    }
    int Index(int lit) { return lit>0 ? 2*lit : -2*lit+1; }
    int Value(int lit) { return lit>0 ? values[lit] : -values[-lit]; }
    bool Assign(int lit) {
        int v=Math.Abs(lit), desired=lit>0?1:-1;
        if(values[v]!=0) return values[v]==desired;
        values[v]=(sbyte)desired; trail.Add(lit); return true;
    }
    // null denotes a tautology. Otherwise retain the first occurrence of each literal.
    public int[] Normalize(List<int> raw) {
        if(epoch==Int32.MaxValue) { Array.Clear(seen,0,seen.Length); epoch=0; }
        epoch++; var result=new List<int>(raw.Count); bool tautology=false;
        foreach(int lit in raw) {
            int v=Math.Abs(lit), mark=lit>0?epoch:-epoch;
            if(seen[v]==mark) continue;
            if(seen[v]==-mark) { tautology=true; continue; }
            seen[v]=mark; result.Add(lit);
        }
        return tautology?null:result.ToArray();
    }
    // Watch slots are c[0], c[1]. Watch relocation survives backtracking.
    bool Propagate() {
        while(head<trail.Count) {
            int falseLit=-trail[head++]; List<int> list=watches[Index(falseLit)];
            int j=0;
            while(j<list.Count) {
                int id=list[j]; int[] c=clauses[id];
                if(c[0]==falseLit) { int swap=c[0]; c[0]=c[1]; c[1]=swap; }
                if(c[1]!=falseLit) throw new Exception("internal watch invariant failure");
                if(Value(c[0])>0) { j++; continue; }
                int k=2; while(k<c.Length && Value(c[k])<0) k++;
                if(k<c.Length) {
                    int replacement=c[k]; c[k]=c[1]; c[1]=replacement;
                    list[j]=list[list.Count-1]; list.RemoveAt(list.Count-1);
                    watches[Index(replacement)].Add(id);
                    continue;
                }
                if(!Assign(c[0])) return false;
                j++;
            }
        }
        return true;
    }
    public void FinishInitial() { if(!RootConflict && !Propagate()) RootConflict=true; }
    // Called only at root, after initial input parsing or after a successful RUP check.
    public void Add(int[] c, bool propagate) {
        if(c==null || RootConflict) return;
        // Choose nonfalse watches under the permanent root assignment.
        int good=0;
        for(int j=0;j<c.Length;j++) if(Value(c[j])>=0) {
            int swap=c[good]; c[good]=c[j]; c[j]=swap; good++;
            if(good==2) break;
        }
        if(good==0) { RootConflict=true; return; }
        if(good==1) {
            // All other literals are root-false, so c[0] is a permanent unit.
            if(!Assign(c[0])) RootConflict=true;
            // No watch is required: this unit remains permanently true.
        } else {
            int id=clauses.Count; clauses.Add(c);
            watches[Index(c[0])].Add(id); watches[Index(c[1])].Add(id);
        }
        if(propagate && !RootConflict && !Propagate()) RootConflict=true;
    }
    public bool Rup(int[] c) {
        if(RootConflict || c==null) return true;
        int rootSize=trail.Count;
        if(head!=rootSize) throw new Exception("root is not propagation-closed");
        bool conflict=false;
        foreach(int lit in c) if(!Assign(-lit)) { conflict=true; break; }
        if(!conflict) conflict=!Propagate();
        for(int j=trail.Count-1;j>=rootSize;j--) values[Math.Abs(trail[j])]=0;
        if(trail.Count>rootSize) trail.RemoveRange(rootSize,trail.Count-rootSize);
        head=rootSize;
        return conflict;
    }
}

sealed class Result {
    public long Additions, Deletions;
    public bool CheckedEmpty;
    public double Seconds;
}

static class FreshRup {
    static bool White(char c) { return c==' ' || c=='\t' || c=='\r' || c=='\n'; }
    static int First(string s) { int k=0; while(k<s.Length&&White(s[k])) k++; return k; }
    static int Integer(string s, ref int pos) {
        while(pos<s.Length&&White(s[pos])) pos++;
        bool neg=false;
        if(pos<s.Length&&s[pos]=='-') { neg=true;pos++; }
        int start=pos; long value=0;
        while(pos<s.Length&&s[pos]>='0'&&s[pos]<='9') {
            value=value*10+(s[pos]-'0'); pos++;
            if(value>Int32.MaxValue) throw new Exception("integer overflow");
        }
        if(pos==start || (pos<s.Length&&!White(s[pos]))) throw new Exception("invalid integer token");
        return neg?-(int)value:(int)value;
    }
    static Engine ReadCnf(string path, out int n) {
        Engine engine=null; n=0; int expected=0, actual=0, lineNo=0;
        var raw=new List<int>();
        using(var reader=new StreamReader(path,Encoding.UTF8,true,65536)) {
            string s;
            while((s=reader.ReadLine())!=null) {
                lineNo++; int pos=First(s); if(pos==s.Length || s[pos]=='c') continue;
                if(engine==null) {
                    string[] h=s.Trim().Split((char[])null,StringSplitOptions.RemoveEmptyEntries);
                    if(h.Length!=4||h[0]!="p"||h[1]!="cnf"||!Int32.TryParse(h[2],out n)||
                       !Int32.TryParse(h[3],out expected)||n<0||n>10000000||expected<0)
                        throw new Exception("invalid CNF header at line "+lineNo);
                    engine=new Engine(n); continue;
                }
                while(pos<s.Length) {
                    while(pos<s.Length&&White(s[pos]))pos++; if(pos==s.Length)break;
                    int lit=Integer(s,ref pos);
                    if(lit==0) {
                        actual++; if(actual>expected)throw new Exception("too many CNF clauses");
                        engine.Add(engine.Normalize(raw),false);raw.Clear();
                    } else {
                        if(Math.Abs(lit)>n)throw new Exception("CNF literal outside declared range at line "+lineNo);
                        raw.Add(lit);
                    }
                }
            }
        }
        if(engine==null||raw.Count!=0||actual!=expected)throw new Exception("incomplete CNF or clause-count mismatch");
        engine.FinishInitial(); return engine;
    }
    static Result Check(string cnf,string proof,bool requireEmpty) {
        var timer=Stopwatch.StartNew();int n;Engine engine=ReadCnf(cnf,out n);
        var result=new Result();var raw=new List<int>();int lineNo=0;
        using(var reader=new StreamReader(proof,Encoding.UTF8,true,65536)) {
            string s;
            while((s=reader.ReadLine())!=null) {
                lineNo++;int pos=First(s);if(pos==s.Length||s[pos]=='c')continue;
                bool deletion=s[pos]=='d';
                if(deletion) {pos++;if(pos==s.Length||!White(s[pos]))throw new Exception("invalid deletion prefix at line "+lineNo);}
                raw.Clear();bool terminated=false;
                while(pos<s.Length) {
                    while(pos<s.Length&&White(s[pos]))pos++;if(pos==s.Length)break;
                    int lit=Integer(s,ref pos);
                    if(lit==0) {terminated=true;while(pos<s.Length&&White(s[pos]))pos++;if(pos!=s.Length)throw new Exception("tokens after proof terminator at line "+lineNo);break;}
                    if(Math.Abs(lit)>n)throw new Exception("proof literal outside declared range at line "+lineNo);
                    raw.Add(lit);
                }
                if(!terminated)throw new Exception("missing proof terminator at line "+lineNo);
                if(deletion) {result.Deletions++;continue;}
                if(result.CheckedEmpty)throw new Exception("addition after final empty clause at line "+lineNo);
                int[] candidate=engine.Normalize(raw);
                if(!engine.Rup(candidate))throw new Exception("not RUP at proof line "+lineNo+", addition "+(result.Additions+1));
                result.Additions++;if(raw.Count==0)result.CheckedEmpty=true;
                engine.Add(candidate,true);
            }
        }
        if(requireEmpty&&!result.CheckedEmpty)throw new Exception("proof does not end with a checked empty clause");
        timer.Stop();result.Seconds=timer.Elapsed.TotalSeconds;return result;
    }
    static string Seconds(double d) { return d.ToString("F6",CultureInfo.InvariantCulture); }
    static int Main(string[] args) {
        try {
            if(args.Length==3&&args[0]=="--batch") {
                using(var output=new StreamWriter(args[2],false,new UTF8Encoding(false))) {
                    foreach(string line in File.ReadLines(args[1])) {
                        if(String.IsNullOrWhiteSpace(line))continue;
                        string[] p=line.Split('\t');if(p.Length!=3)throw new Exception("batch row must have id, cnf, proof");
                        Result r=Check(p[1],p[2],true);
                        output.WriteLine(p[0]+"\t"+r.Additions+"\t"+r.CheckedEmpty.ToString().ToLowerInvariant()+"\t"+Seconds(r.Seconds)+"\t"+r.Deletions);output.Flush();
                    }
                }
            } else {
                bool probe=args.Length==3&&args[0]=="--probe";
                if((!probe&&args.Length!=2))throw new Exception("usage: FreshRup input.cnf proof.drup | --probe input.cnf proof.drup | --batch input.tsv output.tsv");
                Result r=Check(args[probe?1:0],args[probe?2:1],!probe);
                Console.WriteLine("{\"status\":\"passed\",\"additions\":"+r.Additions+",\"deletions\":"+r.Deletions+",\"checked_empty\":"+r.CheckedEmpty.ToString().ToLowerInvariant()+",\"seconds\":"+Seconds(r.Seconds)+"}");
            }
            return 0;
        } catch(Exception e) {Console.Error.WriteLine("FAILED: "+e.Message);return 1;}
    }
}
