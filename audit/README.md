# Audit scope and records

Two reviews are consolidated in the unchanged
[`p001-two-stage-review-20261027.zip`](https://github.com/Lshiqi67/proper-hat-guessing-c5-reproducibility/releases/download/c5-arxiv-v1-evidence-20261027/p001-two-stage-review-20261027.zip).
Its SHA-256 is `1d2d0151f7106d114ed602bd801f82e11a3e65b1d5f820facde3276dd042c6d4`.
Extract it into a fresh directory to read `report.md`, the frozen `snapshot/`
records and the original relative links together. The report is in Chinese;
this overview and the reproduction guide supply an English entry point.

## Distinct scopes

1. The mathematical review checked the definitions, quantifiers, combinatorial
   reductions, branch coverage, encoding-extension logic, RUP soundness and
   final deduction. It accepted the stated finite computations as premises.
2. The computational review freshly rebuilt the classification, checked actual
   generated inputs and auxiliary extensions, and replayed every adopted proof
   with a separately implemented frozen checker. No SAT search was repeated.

| Quantity | Full 27 October audit |
| --- | ---: |
| Parent count representatives | 1,413 |
| Direct terminal parents | 1,269 |
| Parents refined into 51 cases | 144 |
| Child input formulas | 7,344 |
| Terminal proofs | 8,613 |
| Counter-component types | 14 |
| Valid auxiliary inputs | 65,399 |
| RUP additions, including empty clauses | 66,403,934 |
| Checked final empty clauses | 8,613 |

The principal checker is `FreshRup`: deletion records are parsed but their
deletion effect is ignored. `FreshRupActive` belongs to supplementary tests,
not this full replay. The 449 historical fallback events belong to the
26 October audit, not the 27 October `FreshRup` run. Main random tests use
seed 20261027; the supplementary Active differential suite uses 20261028.

## Data provided in Git

The files under [data/](data/) are byte-identical copies of the consolidated
audit's derived data. [The original data dictionary](data/README.md) explains
each field; [summary.json](data/summary.json) distinguishes run time from later
organization time.

- `weight-summary.json` and `.tsv`: the nine weight totals.
- `leaf-audit.jsonl` and `.tsv`: all 8,613 terminal identities, hashes and results.
- `input-audit.jsonl`: all 8,757 audited parent/child inputs.
- `evidence-files.jsonl`: all 17,226 terminal CNF/proof files.
- `component-types.json`, `test-summary.json`, `source-records.json`: component
  coverage, testing scope, and derivation sources.

Paths named `snapshot_*` or `original_*` in the preserved data refer to the
complete audit archive or the research root documented there. They are source
identifiers, not claims that every source file is copied into this Git tree.

[The v2 packaging report](v2-packaging-report.json) separately records a complete
restore of 18,936 files / 6,593,413,117 bytes, another full input check and one
4,899-addition leaf replay. It explicitly says the full RUP replay was not
repeated during packaging. This preparation does not expand those checks into
external peer review or formal certification.
