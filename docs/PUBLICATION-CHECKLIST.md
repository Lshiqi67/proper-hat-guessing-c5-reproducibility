# Coordinated publication checklist

The repository is prepared privately. This checklist does not execute a
visibility change, an arXiv submission or a release announcement.

## Before arXiv submission

- Check that the submitted manuscript is the current `paper/` candidate, not
  the older PDF sealed inside the v2 code archive.
- Verify all manuscript/source hashes, all eleven evidence archive hashes and
  their version correspondence. Retain the exact input ZIP sent to arXiv.
- Inspect arXiv's generated PDF, final author information, title, abstract,
  classification, publication-status wording and licence selection.
- Keep the curated repository private. The paper should describe its intended
  availability upon the preprint's announcement without claiming current
  anonymous access.
- Preserve the adopted license map: author-controlled code MIT; reproduction
  documentation and audit reports CC BY 4.0; manuscript arXiv non-exclusive
  selection. See `../LICENSES/SCOPE.md`; historical archive bytes stay unchanged.
- Preserve all frozen files. No original success report becomes a new run merely
  because it is copied or uploaded.

## When the preprint is actually public

- Verify the public arXiv article page, not just an incomplete/processing/submitted
  dashboard status or a temporary submission identifier.
- Change only the curated repository to public at the agreed publication step;
  retain the full historical research repository as private.
- Confirm the tagged Release and all required assets are accessible without a
  GitHub login. Check exact asset names, sizes and SHA-256 digests, then perform
  an anonymous download check. Record which downloads were actually tested.
- Add the real arXiv identifier and URL to the repository and citation metadata.
  Do not use a submission number as the permanent article identifier.
- Update the root access-status text and record when anonymous access was checked.
  Keep the versioned asset manifest and frozen evidence bytes unchanged.
- If a long-term archive/DOI is later created, verify the actual record and update
  the access documentation. No DOI is assigned by this preparation.

## Version preservation

Do not move the released tag or overwrite sealed assets. Corrections receive a
new version and a change record. Check that public-facing Git history, release
notes, workflow logs and artifacts contain only intended publication materials.
