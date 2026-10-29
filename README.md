# Proper hat guessing on the five-cycle

**Public release, 30 October 2026:** the 23-page preprint is available on
[Zenodo](https://doi.org/10.5281/zenodo.23769672) as version **1.0**, under **CC BY 4.0**.
This curated repository and its existing 17 Release assets are public.
The paper has not been submitted to arXiv and has not undergone external peer review.

This repository accompanies Shiqi Liu's manuscript,
*The Proper Hat-Guessing Number of the Five-Cycle: A Computer-Assisted Argument*.
The paper gives a computer-assisted argument for HG_P(C5) = 4 for arbitrary
deterministic local strategies under the proper-colouring constraint.

## Cite the paper and evidence

> Liu, Shiqi (2026). *The Proper Hat-Guessing Number of the Five-Cycle:
> A Computer-Assisted Argument* (Version 1.0). Zenodo.
> https://doi.org/10.5281/zenodo.23769672

The DOI identifies the **paper**, not a Zenodo archive of the computational evidence.
For reproducibility, also identify the fixed evidence Release
[`c5-arxiv-v1-evidence-20261027`](https://github.com/Lshiqi67/proper-hat-guessing-c5-reproducibility/releases/tag/c5-arxiv-v1-evidence-20261027).
See [CITATION.cff](CITATION.cff) and the [public release record](docs/PUBLICATION-20261030.md).

Author-controlled code is MIT; reproduction documentation and audit reports
are CC BY 4.0. The exact published manuscript PDF is now also CC BY 4.0;
older manuscripts and source files retain their separate permissions.
See the [license scope](LICENSES/SCOPE.md).

The [28 October preparation checks](docs/PREPUBLICATION-VALIDATION.md) are
historical records. Public release does not constitute a new mathematical audit.

## Start here

| Purpose | Entry |
| --- | --- |
| Read the published manuscript | [Paper PDF](paper/c5-proper-hat-guessing-arxiv.pdf) |
| Build the manuscript | [LaTeX source](paper/main.tex), [build instructions](paper/BUILDING.md) |
| Download and verify the computational evidence | [English reproduction guide](REPRODUCING.md) |
| Read the computational verification scope | [Audit overview](audit/README.md) |
| Identify the exact archived inputs and proofs | [Evidence manifest](metadata/evidence-manifest.json), [SHA-256 list](metadata/evidence-SHA256SUMS.txt) |
| Understand the manuscript and evidence versions | [Version map](VERSION-MAP.md) |
| Understand AI assistance | [Authorship statement](AUTHORSHIP.md) |

The fixed deposit identifier is `c5-arxiv-v1-evidence-20261027`. Its
[Release](https://github.com/Lshiqi67/proper-hat-guessing-c5-reproducibility/releases/tag/c5-arxiv-v1-evidence-20261027) contains all eleven sealed reproduction
archives. They total **1,910,553,676 bytes**. A repository clone does not contain
the complete CNF and DRUP files; download the Release assets before restoring
the evidence. The public Release can be accessed without repository membership.

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
