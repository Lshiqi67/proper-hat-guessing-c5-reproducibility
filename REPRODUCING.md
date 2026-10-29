# Download and reproduce the current evidence

Current deposit: **`c5-arxiv-v1-evidence-20261027`**. Published manuscript: **Zenodo v1.0**, identical to **`20261027-arxiv-preparation`**; use the PDF and build instructions in `paper/`. Sealed reproduction package: **`c5-reviewed-evidence-20261027-v2`**.

This guide uses the v2 verifier and complete evidence selected for the 27 October audit. The unchanged v2 instructions are preserved under [reproduction/](reproduction/README.md); [VERSION-MAP.md](VERSION-MAP.md) explains the manuscript history. The repository and Release are public as of 30 October 2026. The paper is archived at https://doi.org/10.5281/zenodo.23769672; this DOI does not archive the evidence. See [the public release record](docs/PUBLICATION-20261030.md) for the actual access-check scope.

## 1. Requirements and scope

Use Windows, Python **3.11+**, GitHub CLI and the Windows .NET Framework C# compiler. The historical v2 package validation used Python 3.13.0 and .NET Framework 4.x. This prepublication preparation uses Python 3.12.14; its separately recorded checks do not replace the historical full audit. Python's standard library is sufficient for hashing, restoration and the full input audit. Certificate replay additionally compiles the supplied C# checker. **No SAT solver or PySAT is required to verify saved evidence.** No Linux or macOS execution is claimed.

Use fresh, short directories. Allow approximately **10 GB** for the eleven compressed archives, one restored evidence copy and modest outputs; additional copies require more space. The verifier enforces a 235-character Windows evidence-path limit. Do not restore the evidence directly inside a long repository checkout path.

Every `--out` directory below must be new, outside the input package, and must not contain the package. Do not run Python with `-O`. Keep failures and partial output; do not edit hashes or reuse old PASS records to make a new check succeed.

## 2. Download this tagged deposit

With GitHub CLI authenticated to a GitHub account, choose a new archive directory. Repository membership is not required; for downloads without a GitHub account, use the HTTPS helper below:

```powershell
$archives = 'D:\c5-archives'
New-Item -ItemType Directory -Path $archives | Out-Null
gh release download c5-arxiv-v1-evidence-20261027 `
  --repo Lshiqi67/proper-hat-guessing-c5-reproducibility `
  --dir $archives
```

The [Release](https://github.com/Lshiqi67/proper-hat-guessing-c5-reproducibility/releases/tag/c5-arxiv-v1-evidence-20261027) provides the eleven unchanged archives named by
[the evidence manifest](metadata/evidence-manifest.json):

- `c5-reviewed-evidence-20261027-v2-code.zip`;
- `p001-two-stage-review-20261027.zip`;
- all nine `c5-evidence-20261026-v1-weightNN.zip` files, for NN = 17 through 25.

They total **1,910,553,676 bytes**. A clone or GitHub-generated source ZIP does
not contain the complete CNF/DRUP evidence. The code archive contains the prior
audited PDF; the current candidate in `paper/` is a separate document.

The repository's download helper fetches only this manifest's named files,
checks their size and SHA-256, and refuses an existing output directory:

```powershell
python -X utf8 -B tools/download_evidence.py --transport https --out D:\c5-archives
```

Run either this helper or the preceding `gh release download` example, not both
into the same directory. For a small trial, add
`--asset c5-evidence-20261026-v1-weight17.zip` and use a different fresh directory.
`--transport https` downloads from the public Release without a GitHub account.
The authenticated `--transport gh` remains an alternative. Access-check results
and their limits are recorded in [the public release record](docs/PUBLICATION-20261030.md).

For files downloaded manually, check every line of
[the evidence SHA-256 list](metadata/evidence-SHA256SUMS.txt) before extraction:

```powershell
Get-Content -LiteralPath metadata/evidence-SHA256SUMS.txt | ForEach-Object {
    if ($_ -notmatch '^([0-9a-fA-F]{64})  ([^/\\:]+)$') {
        throw 'Malformed checksum entry'
    }
    $expected = $Matches[1]
    $name = $Matches[2]
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $archives $name)).Hash
    if ($actual -ine $expected) { throw "SHA-256 mismatch: $name" }
    Write-Output "SHA-256 OK: $name"
}
```

The helper stores a receipt in the new output directory. A hash match identifies
the frozen bytes; it is not a mathematical proof or an independent signature.
Keep the manifest version with any result you report.

## 3. Extract the code and check its inventory

Expand the unchanged code ZIP into a new short directory:

```powershell
$code = Join-Path $archives 'c5-reviewed-evidence-20261027-v2-code.zip'
Expand-Archive -LiteralPath $code -DestinationPath D:\c5-review
$pkg = 'D:\c5-review\c5-reviewed-evidence-20261027-v2'
$tool = Join-Path $pkg 'tools\verify.py'
python -X utf8 -B $tool integrity --root $pkg --out D:\c5-runs\integrity-01
```

The entry point checks the package's complete expected source/document inventory and the selected terminal identities. The code manifest excludes itself; the outer ZIP hash identifies that manifest. Read the extracted `README.md`, `REPRODUCING.md` and `DEPENDENCIES.md` for the preserved package instructions. Its historical `LICENSE` must be read together with the later [top-level license](LICENSE) and [scope notice](LICENSES/SCOPE.md), which grant MIT / CC BY permissions for the specified author-controlled files without changing the sealed ZIP.

## 4. Restore all actual inputs and certificates

```powershell
python -X utf8 -B $tool restore --root $pkg `
  --archives $archives --full --out D:\c5-runs\restore-01
```

Restore checks archive size and SHA-256, the exact unique member inventory, every member's size/SHA-256/ZIP CRC, and the connection to the 27 October terminal selection. It then restores **18,936 files / 6,593,413,117 bytes** beneath the extracted package. These include all 8,613 CNF/proof pairs, nonterminal parent CNFs and required metadata. Unknown or duplicate members, escaping paths and ZIP symlinks are rejected.

Existing evidence is rejected even if its bytes match. An interrupted run may leave partial files; inspect `wrapper-report.json` and `member-readback.jsonl`, then use a fresh code extraction for another restore. Do not present a partial restore as complete.

A small trial may replace `--full` with `--weight 17`. The full input audit in the next section still requires all nine weights. A later full restore must use another fresh extraction because reusing the partially populated package is refused.

## 5. Audit input semantics

After a complete restore:

```powershell
python -X utf8 -B $tool inputs --root $pkg --out D:\c5-runs\inputs-01
```

This checks **1,413 parent CNFs, 7,344 child CNFs, 14 actual counter-component types and 65,399 valid auxiliary extensions**. It checks the finite profile/orbit classification, base clauses, counter boundaries, the exact parent-plus-pattern construction, the four-colour strategy over 240 proper colourings, and the local witness over all 1,020 five-colour configurations. The extension direction needed by the UNSAT argument is the one claimed.

Read the fresh input `report.json`, `input-files.jsonl` and wrapper report. This step checks input semantics; it does not replay RUP inferences. The wrapper imports the unchanged `fresh-audit/audit_inputs.py`, redirects its input/output locations and timer origin, and checks its source identity. Do not invoke the historical auditor directly using its original workspace paths.

## 6. Replay a real leaf, then all terminal proofs

```powershell
python -X utf8 -B $tool replay --root $pkg `
  --weight 17 --profile 0 --out D:\c5-runs\leaf-17-0-01
python -X utf8 -B $tool replay --root $pkg `
  --full --out D:\c5-runs\replay-all-01
```

The first checks **17/000/direct**, with **4,899 additions including its final empty clause**. The second requires exactly **8,613 unique terminal identities and 66,403,934 additions including all 8,613 empty clauses**. A successful sample is not a full replay.

The entry point compiles unchanged `fresh-audit/FreshRup.cs` with `C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe`; supply `--csc PATH_TO_CSC` if needed. It parses deletion records but ignores their deletion effect, retaining only original and previously justified clauses. Every addition is checked by reverse unit propagation and a checked empty clause is mandatory. It does not switch to another checker or a cached result after failure.

A full result requires matching actual input/proof hashes, exact identity set and order, per-leaf success and addition counts, and checked final empty clauses. Counting output rows alone is insufficient. `--full` cannot be combined with a narrower selection. Partial mode supports `--profile N` and `--limit N` with `--weight`.

The supplied wrapper runs checker processes sequentially with no built-in timeout. It can take substantially longer than the historical full audit, which used eight batches. Inspect compiler logs, checker output, `batch.tsv`, `replay.tsv` and `wrapper-report.json`; retain failed runs as well as successful ones.

To rehash restored evidence without replaying inference steps:

```powershell
python -X utf8 -B $tool integrity --root $pkg --full --out D:\c5-runs\integrity-all-01
```

## 7. Read the complete audit and build the manuscript

The consolidated audit ZIP contains the detailed Chinese report, data ledgers, source snapshots, complete full-run records, test records, failures and limitations. It does not replace the nine evidence ZIPs. Its separate `tools/verify_package.py --package .` checks its own complete member inventory; this is a package integrity check, not RUP replay.

The current submission candidate and its TeX sources are under `paper/`.
Follow [paper/BUILDING.md](paper/BUILDING.md). Building the paper does not require
the evidence or a SAT solver. Its separate manuscript manifest identifies the
new PDF and source ZIP; [VERSION-MAP.md](VERSION-MAP.md) identifies the older
PDF retained inside the v2 archive. Never replace that archived PDF in place.

## 8. Recorded validation and limits

The 27 October computational audit freshly checked all inputs and all 66,403,934 additions. The later v2 package validation separately restored every member, repeated the full input audit, compiled the checker and replayed one real 4,899-addition leaf plus rejection-boundary tests. The reader revision separately checked logic presentation, data correspondence, all 22 page images and isolated source compilation. This upload does not repeat the full audit.

See [the audit overview](audit/README.md), its linked complete two-stage
archive, the [v2 package validation](audit/v2-packaging-report.json), and the
current manuscript's build records. FreshRupActive belongs to supplementary
testing and was not the checker used in the main 27 October replay.

Optional regeneration or SAT search is a different task. Historical generator dependencies are documented inside the package; they are not required for the checks above. This guide does not report a new SAT search, external human peer review or proof-assistant certification. Current licenses are described in [LICENSES/SCOPE.md](LICENSES/SCOPE.md).

## Publication status

The repository is public and the preprint is published on [Zenodo](https://doi.org/10.5281/zenodo.23769672),
version 1.0, dated 30 October 2026. arXiv submission remains pending.
Frozen metadata retains its original preparation status; the current public
status and paper license are recorded separately without changing archive hashes.
