# Completed private preparation checks

> Historical preparation record (27–28 October 2026). For the current public
> status, paper DOI and additional PDF license, see
> [PUBLICATION-20261030.md](PUBLICATION-20261030.md). The original plan to wait
> for arXiv was superseded by the author's Zenodo publication decision.

Recorded 2026-10-28T00:12:18.742561+08:00. Repository visibility remains **private**. No arXiv
submission, server build, announcement or anonymous access is claimed.

The fixed tag `c5-arxiv-v1-evidence-20261027` identifies core commit
`baa09bd5ab63ed1dd3826a5875d0e0e7585e6a3d`. This document and its
[machine-readable receipt](../metadata/prepublication-validation.json) are an
additive verification record on `main`; they do not move that tag or change
any sealed asset. The core manifest describes the tagged snapshot.

| Check | Actual result |
| --- | --- |
| Manuscript | 23 pages; 13 TeX source files; two local and two isolated compilations; final warnings zero; extracted page texts identical |
| Frozen files | 44 v2 files and all eleven sealed ZIPs unchanged; older manuscripts and original research checkout retained |
| Git transport | All 108 tagged file blobs matched local content |
| Release transport | Exact set of 17 assets, 1,911,268,859 bytes, all server SHA-256 digests matched |
| Complete evidence transfer | Eleven original ZIPs, 1,910,553,676 bytes, downloaded and hashed in GitHub Actions before upload; no recompression |
| Download helper tests | 15 offline cases passed; 11 private transfer guard cases passed |
| Local return downloads | Code ZIP, weight17 ZIP, current PDF, current source ZIP and notices ZIP actually downloaded and hashed |
| Restored sample | Weight17: 10 files, 1,183,936 bytes; archive/member hashes, inventory and CRC checked |
| Fresh replay | Recompiled `FreshRup`; `17/000/direct`; 4,899 additions and final empty clause checked; 2,514 deletion records parsed and ignored |

The local trial used Windows, Python 3.12.14 and the Windows .NET Framework
C# compiler. It did not run the full input-semantic audit, all 8,613 terminal
proofs or a new SAT search. The earlier full audit remains the separate
historical record. The five local downloads do not imply all 17 assets were
downloaded back to the local computer; the full server digest check and the
cloud copy have their own stated scopes.

Some GitHub CLI requests failed with TLS/timeout errors. They remain recorded;
the current small files were then obtained by the verified asset-ID endpoint
as needed. No credential or transient signed URL is included in this receipt.

The author's explicit grants are now MIT for author-controlled code and CC BY
4.0 for reproduction documentation and audit reports, as defined by
[LICENSES/SCOPE.md](../LICENSES/SCOPE.md). The paper retains its separate arXiv
license selection. Historical frozen notices are not silently edited.

Remaining steps: inspect the current arXiv draft, upload the current source,
check arXiv's generated PDF and metadata, and obtain the author's final content
review. Formal submission and coordinated repository publicity follow the
author's final decision; see [PUBLICATION-CHECKLIST.md](PUBLICATION-CHECKLIST.md).
