# Local review deposit: proper five-color hat guessing on C5

Version **c5-reviewed-evidence-20261027-v2**, prepared 27 October 2026.
This is an unpublished local deposit. No public archive URL or DOI has been
assigned; the corresponding fields in `VERSION.json` are null. Retain `LICENSE`
and `AUTHORSHIP.md`. This preparation does not select a public license.

The package supports review of the manuscript
`paper/c5-proper-hat-guessing-audited.pdf` and the computational assertion that
all adopted terminal CNFs are unsatisfiable. The manuscript concerns arbitrary
deterministic local rules with ordered neighbors on the cycle C5, restricted to
proper colorings. Code, mathematical reasoning, and the stored certificates
must be assessed together; a file hash or a saved PASS record is not a proof.

## What to obtain together

The delivery consists of the new code ZIP, a separate consolidated two-stage
review ZIP, and **nine complete evidence ZIPs**, one for each weight 17 through
25. The nine evidence ZIPs retain their original `c5-evidence-20261026-v1-weightNN.zip`
names and bytes. Their version label records immutable evidence provenance;
it does not mean that version 1's checker is used by the new entry point.
The top-level delivery manifest gives every archive's size and SHA-256.

The evidence archives contain **18,936 files / 6,593,413,117 uncompressed bytes**.
This includes all **8,613 CNF/proof pairs** (17,226 files / 6,585,642,510 bytes),
144 additional nonterminal parent CNFs, parent counter metadata, profile lists,
and diagonal-pattern metadata. A compact review ZIP by itself does not contain
these large certificates. `evidence/files.jsonl` identifies every evidence file;
`evidence/assets.json` gives the nine archive hashes. The code ZIP contains the
remaining small inputs, catalogues, paper, and source code.

## Verification and its scope

Use `tools/verify.py`, with explicit `--root` and a new external `--out`, as
described in [REPRODUCING.md](REPRODUCING.md). Python 3.11+ and its standard
library suffice for restoring, hashing, and checking all actual CNF inputs.
Replaying saved certificates additionally needs the Windows .NET Framework
C# compiler. **No SAT solver or PySAT installation is needed to verify saved
evidence.** Optional generation/search dependencies are listed separately.

The entry point imports the unchanged fresh input auditor and redirects only
its input/output paths and elapsed-time origin. It compiles the unchanged
`fresh-audit/FreshRup.cs` and checks real CNF/proof files. The checker ignores
deletions, validates every added clause by reverse unit propagation, and
requires a checked empty clause. Ignoring a deletion retains a previously
entailed clause and is sound for this monotone verification mode. It may cost
memory; this is not an active-clause-deletion checker. No old success cache is used.

Before any action, the entry point checks the complete catalogue against all
1,413 parent identities and their required direct or 51-case diagonal branches.
A full replay must return exactly the unique 8,613 expected identities and
66,403,934 checked additions. Merely counting 8,613 output rows is insufficient.

## Completed work and provenance

The historical **27 October 2026** full audit freshly replayed all 8,613 leaves
and 66,403,934 additions through all 8,613 empty clauses, using the frozen
FreshRup source. Its input audit checked all 1,413 parent and 7,344 child CNFs,
14 actual counter-component types and all 65,399 admissible component inputs.
The separate review ZIP preserves the detailed mathematical review, complete
run records, source snapshots, differential tests, and limitations.

`historical-records/` contains selected unchanged records of that completed
audit, not results newly produced by extracting this package. The new v2
packaging check separately restores all evidence, hashes every member against
both the old evidence manifest and the fresh leaf selection, reruns the complete
input audit, and replays the real weight-17/profile-0 certificate. Its machine
records are shipped at delivery level under `checks/`; it does **not** claim a
second full 66-million-addition replay.

The older 26 October packaging checks (55 sample proofs / 351,901 additions)
are historical v1 work, not a v2 full replay. The active-deletion checker in
supplementary records was not the checker used in the 27 October full replay.

See [docs/SELECTION.md](docs/SELECTION.md) for selection and
[docs/PUBLICATION-NOTES.md](docs/PUBLICATION-NOTES.md) for the remaining public
release metadata. No proof-assistant certification or independent human peer
review is asserted. No original SAT search was rerun during packaging.
