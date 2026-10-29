# License scope and historical notices

Historical selection, confirmed on 27 October 2026: manuscript arXiv
perpetual non-exclusive distribution license; author-controlled reproducibility
code MIT; reproduction instructions and audit reports CC BY 4.0. This replaces
the earlier, unadopted limited-reproduction proposal.

On 30 October 2026 the repository became public and the author additionally
published the exact current 23-page PDF under CC BY 4.0 at
https://doi.org/10.5281/zenodo.23769672. This later grant is limited to that
published manuscript; older manuscripts and source files are not automatically
relicensed. Historical inventories and sealed notices remain unchanged.

## Scope

| Material | Applicable notice |
| --- | --- |
| Author-controlled Python and C# reproduction, verification, audit and packaging programs; the accompanying workflow; compiled copies of those programs | [MIT](MIT.txt) |
| Author-controlled READMEs, English reproduction instructions, authorship/version notes, audit reports and explanatory report tables/metadata | [CC BY 4.0](CC-BY-4.0.txt) |
| Exact 23-page PDF published as Zenodo v1.0 | [CC BY 4.0](CC-BY-4.0.txt); exact identity in [Paper notice](PAPER.md) |
| Other manuscript versions, `.tex`, source figures and manuscript source ZIPs | [Paper notice](PAPER.md); no automatic extension of the new PDF grant |
| CNF inputs, DRUP certificates, test inputs and numerical results | Mathematical evidence; see below |
| Third-party components, notices, quoted material and license texts | Their own terms; no relicensing of third-party rights |

The historical 27 October file-level [scope inventory](../metadata/license-scope.json) identifies the
copied frozen files and every member of the sealed code/audit archives, using
member paths and SHA-256. The nine complete evidence ZIPs are identified by
their outer hashes in [the evidence manifest](../metadata/evidence-manifest.json).
The scope descriptions apply to new files of the same kind at this release.
For software, comments and embedded usage help are part of the MIT software;
separate reproduction manuals and reports are CC BY 4.0.

The grants are limited to rights the author holds and may license. Naming an
external dependency is not licensing it. Python, .NET, GitHub Actions, SAT
solvers, PySAT and other third-party software retain their own terms. Neither
SAT solver binaries nor a solver installation are needed to check the saved
evidence with the supplied verifier. Any protected third-party content inside
a report remains excluded from the author's grant.

## Evidence and compiled files

No exclusive copyright is asserted in mathematical facts, numerical values,
CNF clauses or DRUP inference sequences as such. Readers may download, copy,
parse and check the supplied evidence for scholarly verification. This notice
does not impose a license on uses that do not require permission. Any
author-controlled explanatory prose or protectable report arrangement remains
covered by CC BY 4.0; software remains MIT. No CC0 dedication is asserted.

Historical `.exe` files in the audit ZIP are preserved audit artifacts compiled
from the supplied author's checker/test sources. They fall within the same
MIT grant to the extent of the author's rights. Reproduction instructions
compile the inspected sources afresh rather than relying on those old binaries.

## Frozen archives

Do not edit an archive to replace its embedded `LICENSE` or private-access
warning: doing so would invalidate the published hash and provenance. The
current top-level notice is a later, additional permission from the author.
It supersedes inconsistent historical restrictions **for the covered
author-controlled code and documentation only**, without removing prior
permissions or third-party notices. Old private-hosting statements describe
their historical package, not current access status.

When redistributing covered files from a frozen archive, include this scope
notice, the relevant MIT/CC BY text or link and the original attribution.
The mixed archive as a whole is not labelled MIT or CC BY: manuscripts and
third-party content retain their separate status. Reuse of protected material
outside these grants still requires applicable permission.

## Attribution

Identify Shiqi Liu as author, retain applicable notices and cite the exact
deposit version `c5-arxiv-v1-evidence-20261027`. For CC BY materials, link to
the license and indicate modifications. A citation must not imply endorsement,
external peer review or proof-assistant certification. See [AUTHORSHIP.md](../AUTHORSHIP.md)
for the disclosed AI-assisted workflow.
