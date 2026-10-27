# Proper hat guessing on the five-cycle

**Preparation completed 28 October 2026:** the private Release contains all 17
verified assets. The current paper has 23 pages. Selected return downloads,
restoration and a fresh single-leaf replay passed; see the
[completed checks and exact limits](docs/PREPUBLICATION-VALIDATION.md).
arXiv website compilation/submission and anonymous access remain pending.

This repository is the curated reproduction deposit for Shiqi Liu's manuscript,
*The Proper Hat-Guessing Number of the Five-Cycle: A Computer-Assisted Argument*.
The paper gives a computer-assisted argument for HG_P(C5) = 4 for arbitrary
deterministic local strategies under the proper-colouring constraint.

**Prepublication status, 27 October 2026:** this repository is being prepared
privately. Public access and an arXiv announcement are not claimed. The intended
public release is coordinated with the paper's actual arXiv announcement; see
[the publication checklist](docs/PUBLICATION-CHECKLIST.md). The [license map](LICENSES/SCOPE.md) applies MIT to author-controlled code
and CC BY 4.0 to reproduction documentation and audit reports; the manuscript
retains its separate arXiv license selection.

## Start here

| Purpose | Entry |
| --- | --- |
| Read the current submission candidate | [Paper PDF](paper/c5-proper-hat-guessing-arxiv.pdf) |
| Build that candidate | [LaTeX source](paper/main.tex), [build instructions](paper/BUILDING.md) |
| Download and verify the computational evidence | [English reproduction guide](REPRODUCING.md) |
| Read the computational verification scope | [Audit overview](audit/README.md) |
| Identify the exact archived inputs and proofs | [Evidence manifest](metadata/evidence-manifest.json), [SHA-256 list](metadata/evidence-SHA256SUMS.txt) |
| Understand the manuscript and evidence versions | [Version map](VERSION-MAP.md) |
| Understand AI assistance | [Authorship statement](AUTHORSHIP.md) |

The fixed deposit identifier is `c5-arxiv-v1-evidence-20261027`. Its
[Release](https://github.com/Lshiqi67/proper-hat-guessing-c5-reproducibility/releases/tag/c5-arxiv-v1-evidence-20261027) is the intended home of all eleven sealed reproduction
archives. They total **1,910,553,676 bytes**. A repository clone does not contain
the complete CNF and DRUP files; download the Release assets before restoring
the evidence. Private access requires an authorized GitHub account.

## What was checked

The full local audit completed on 27 October 2026 checked all **1,413 parent
CNFs**, **7,344 child CNFs**, **14 counter-component types** and **65,399 admissible
auxiliary inputs**. The frozen `FreshRup` checker replayed **8,613 terminal
proofs** and **66,403,934 additions**, including all final empty clauses.

The later v2 packaging check restored all evidence, repeated the input audit,
and replayed one real leaf. It was not another full 66-million-step replay.
This publication preparation preserves that distinction. Separate programs
were developed within one AI-assisted workflow; this is neither external
human peer review nor proof-assistant formalization.

## Repository layout

- `paper/`: the current arXiv submission candidate, supplied separately from the sealed evidence.
- `reproduction/`: the original 44-file v2 package, copied byte-for-byte for source inspection.
- `audit/`: a concise English overview and unchanged derived ledgers.
- `metadata/`: the new hosting manifest and unchanged historical manifests.
- `tools/`: download and integrity tooling for the publication deposit.
- `docs/`: version, release and terms preparation notes.

The full Chinese audit report, frozen source records, checker tests and failures
are in `p001-two-stage-review-20261027.zip`. The nine evidence ZIPs provide the
actual inputs and refutations. Neither component substitutes for the other.

The old manuscript inside the sealed v2 code ZIP remains unchanged. Use `paper/`
for the current submission candidate and [VERSION-MAP.md](VERSION-MAP.md) to
interpret their relationship. Publication does not silently replace any sealed
archive or retroactively change the scope of a historical check.
