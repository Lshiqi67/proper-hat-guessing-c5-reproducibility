# Manuscript and evidence versions

**Public version, 30 October 2026:** [Zenodo preprint v1.0](https://doi.org/10.5281/zenodo.23769672)
is the same 23-page PDF as `20261027-arxiv-preparation`, SHA-256
`170e5f40b5cd0695997760935df38ba8097be07b179c7d4f48ecc597231749e7`.
The DOI identifies the paper only; the evidence remains at the fixed GitHub Release.
The manuscript date is 27 October; its Zenodo publication date is 30 October.

| Identifier | Role | Relationship |
| --- | --- | --- |
| `20261026-audit-integrated` | The 22-page manuscript examined in the consolidated audit | Its PDF remains inside the frozen v2 code archive. |
| `20261027-reader-revision` | The subsequent 22-page exposition revision | Clarifies the proof and reproduction; does not alter inputs or certificates. |
| `20261027-arxiv-preparation` | Current submission candidate in `paper/` | Updates publication access, metadata and submission presentation from the reader revision. Its own manifest identifies its exact files. |
| `c5-reviewed-evidence-20261027-v2` | The unchanged code and reproduction package | This version is the verifier and input/certificate mapping used here. |
| `p001-two-stage-review-20261027` | The consolidated mathematical and computational review | The complete archive contains the reports, source snapshots, failures and per-leaf records. |
| `c5-evidence-20261026-v1` | Nine unchanged evidence archives, weights 17 through 25 | They are reused by the v2 package and this deposit without recompression. |
| `c5-arxiv-v1-evidence-20261027` | The curated hosting deposit | Provides the current paper and fixed download locations for the unchanged archives. |

The frozen v2 code archive has SHA-256
`830ac5e4f806cff722a02ac0e72da6d7ebd0e6543739059f1c1dcfba447c2d4a`.
The audited PDF inside it has SHA-256
`5ae7ed9858c5064ee894f52d9825ac6cbed38b533428b1426a03d365ed9c28e6`.
The consolidated audit ZIP has SHA-256
`1d2d0151f7106d114ed602bd801f82e11a3e65b1d5f820facde3276dd042c6d4`.

The reader-revision PDF, an earlier manuscript version rather than the new
submission candidate, has SHA-256
`0f5eb469213dfdcc379bf009f9b71678d5ad28cafdd8a290ee62950053530143`.
The current candidate's new hashes belong in its own manifest. Do not substitute
that PDF inside an already sealed archive.

`LOCAL_ONLY`, null URLs and private-review notices inside preserved files report
their historical preparation state. The current access and intended hosting
locations are stated separately in the root documentation and
`metadata/evidence-manifest.json`. Those frozen fields are not current access metadata. The repository is now
public; the paper DOI and current status are recorded in
[PUBLICATION-20261030.md](docs/PUBLICATION-20261030.md).

The public release should keep this tag fixed. Any changed source, certificate,
manifest or paper must receive a new version identifier and new hashes; old
files remain traceable.
