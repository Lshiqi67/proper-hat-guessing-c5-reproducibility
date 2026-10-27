# Offline reproduction instructions

These commands operate only on local files. Tested preparation platform:
Windows, Python 3.13.0, and the installed .NET Framework 4.x C# compiler.
The Python entry point requires Python **3.11+** (`hashlib.file_digest`). Do not
use Python `-O`. No Linux or macOS execution is claimed; the C# source is supplied
so another build route can be reviewed separately. No executable is needed in
the code ZIP.

## 1. Extract the code and check its inventory

Place all delivery ZIPs in a local archive directory. Expand the code ZIP into
a **new, short** directory. It creates `c5-reviewed-evidence-20261027-v2`.
For example, in PowerShell (replace drive paths as appropriate):

```powershell
Expand-Archive -LiteralPath D:\c5-archives\c5-reviewed-evidence-20261027-v2-code.zip -DestinationPath D:\c5-review
$pkg = 'D:\c5-review\c5-reviewed-evidence-20261027-v2'
python -X utf8 -B "$pkg\tools\verify.py" integrity --root "$pkg" --out D:\c5-runs\integrity-01
```

The code ZIP hash is in the delivery `SHA256SUMS.txt` and delivery manifest.
The code manifest excludes itself; the outer ZIP hash covers that manifest.
All expected source/document files are hashed before the tool proceeds.
Each `--out` directory must be nonexistent, outside the input package and must
not contain the package. Reusing an output directory is refused. Logs and fresh
binaries go only to that output. Original audit records are never updated.

## 2. Restore every saved input and certificate

```powershell
python -X utf8 -B "$pkg\tools\verify.py" restore --root "$pkg" --archives D:\c5-archives --full --out D:\c5-runs\restore-01
```

Restore verifies each complete archive's size and SHA-256, the exact unique
member inventory, every member's size, SHA-256 and ZIP CRC, then writes the
member under the extracted package. Paths escaping the package and ZIP symlinks
are refused. Existing evidence files are refused even when identical; start
with another fresh extraction if restoring again. On Windows the maximum
resulting evidence path length is limited to 235 characters; choose a shorter
root if needed. Allow approximately **10 GB** for one set of compressed archives,
one restored copy, and modest outputs; additional copies need additional space.

For a small initial trial use `--weight 17` instead of `--full`. A subsequent
full restore into that same root will be refused because some files exist;
use a fresh extraction for the full run. The complete input audit below needs
all nine weights. A failure or interruption may leave a partial restored tree;
it must not be presented as successful. Inspect `wrapper-report.json` and
`member-readback.jsonl` in the new output directory.

The old evidence manifest is cross-checked against the new audit's selected
terminal list: every one of the 17,226 terminal files must match in path, size
and hash. Metadata and nonterminal parents are checked against the original
complete evidence manifest. This comparison validates archived bytes; it does
not, by itself, establish logical correctness.

## 3. Check all actual CNF inputs

```powershell
python -X utf8 -B "$pkg\tools\verify.py" inputs --root "$pkg" --out D:\c5-runs\inputs-01
```

This standard-library-only audit reads all 1,413 parent CNFs and 7,344 refined
children; checks catalogue coverage, base clauses, counter blocks, and the
exact parent-plus-pattern construction; and checks every admissible original
input has a satisfying auxiliary extension for each of the 14 actual counter
component types (65,399 cases in total). Only the encoding preservation direction
needed to infer nonexistence from UNSAT is claimed. It also checks the finite
profile/orbit classification, all 240 proper four-colorings and the explicit
five-color witness over all 1,020 proper colorings. See the fresh `report.json`
and `input-files.jsonl`. This command does not replay proof inferences.

The original `fresh-audit/audit_inputs.py` bytes are unchanged. The adapter uses
`importlib` and sets `ROOT = <package>/research`, `OUTPUTS` to that root's A001
outputs, `HERE = <new output>`, and `START` to a fresh timer origin, then calls
`main()`. No mathematical function is replaced. Its source hash is checked
before and after execution. Do not run the historical source directly: its
unadapted default paths belong to the original research layout.

## 4. Replay a real certificate, then the entire terminal set

```powershell
python -X utf8 -B "$pkg\tools\verify.py" replay --root "$pkg" --weight 17 --profile 0 --out D:\c5-runs\leaf-17-0-01
python -X utf8 -B "$pkg\tools\verify.py" replay --root "$pkg" --full --out D:\c5-runs\replay-all-01
```

The first command verifies one actual proof, **4,899 additions**, through its
empty clause. The second verifies all **8,613** proofs and **66,403,934** additions.
The provided entry point runs one checker process sequentially; it can take
substantially longer than the recorded 27 October full run, which used eight
independent batches. It has no built-in timeout. A full success requires the
exact unique expected identity set, actual selected CNF/proof hashes, checked
empty clauses, and matching addition totals. No count-only full-scope flag is
accepted. `--full` cannot be combined with a narrower selection. Partial mode
also supports `--profile N` and a positive `--limit N`, always with `--weight`.
Partial success remains partial, regardless of the requested name of the output
directory.

The tool compiles `fresh-audit/FreshRup.cs` with
`C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe`; override with
`--csc PATH_TO_CSC` if necessary. Review compiler logs, `batch.tsv`, `replay.tsv`,
checker stdout/stderr and `wrapper-report.json`. Every successful result contains
the source and compiled executable SHA-256 and actual commands. Deletion records
are strictly parsed and ignored. Every addition is checked against the retained
original and previously checked clauses. A bad step or missing empty clause
causes failure; the tool does not fall back to a cached result or a different
checker.

To rehash all restored files without running inference checks:

```powershell
python -X utf8 -B "$pkg\tools\verify.py" integrity --root "$pkg" --full --out D:\c5-runs\integrity-all-01
```

## 5. Optional generation and SAT search

Saved-evidence verification above needs **no** `python-sat`, Glucose, or `six`.
The original generator/import closure is preserved under `research/attempts/`.
Its optional historical environment was `python-sat==1.9.dev17` and `six==1.17.0`;
see `research/attempts/A003-complete-sat/checks/requirements-solver.txt`.
These third-party dependencies are not bundled. The generator uses Glucose3
and sequential-counter cardinality constraints. Install optional dependencies
separately under their own terms if choosing to rerun search.

The legacy source files are preserved for inspection and optional experiments,
not used by the fresh input auditor or new replay tool. Before invoking a legacy
CLI, inspect its help and provide a distinct new output path; do not write into
the archived evidence. New searches may produce different proofs or UNKNOWN
under a conflict budget and require their own verification. Neither packaging
nor the two-stage audit claims to have rerun the original search.

## 6. Distinguish historical and new results

The detailed consolidated review archive records the 27 October mathematical
and computational audits and their limitations. `historical-records/` contains
selected records of that completed full run. The delivery's `checks/` directory
records this v2 packaging exercise: complete member read-back/restoration,
complete input audit and a single real leaf replay. They are separate runs.
Hashes are integrity identifiers, not signatures or trusted publication links.
No public permanent identifier currently exists.
