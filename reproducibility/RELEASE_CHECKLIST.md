# Versioned archive checklist

This bundle is the code-only release candidate for the timestamped research
archive. It is intended to be published as GitHub release `v0.2.1`. The
manuscript source is intentionally withheld; the historical `v0.2.0` tag still
contains it and must remain private.

## Frozen material included

- formal problem, experiment, oracle/eligibility, and claim-metric specifications;
- C1 and C2 machine-readable contracts;
- locked oracle thresholds;
- C1 and C2 decision snapshots and split scores;
- compact C2 oracle-relative audit artifacts;
- calibration and shared-model C-MAPSS scripts and compact outputs.

The decision snapshots are part of the record even when a claim fails. In this
version, C1 is recorded as `C1-OA-PASS` and C2 as `C2-CORE-FAIL`.

## Zenodo publication sequence

1. Confirm that the GitHub repository contains the `v0.2.1` release tag.
2. In Zenodo, enable the repository under GitHub integrations.
3. Create or select the GitHub release `v0.2.1` and import it into Zenodo after
   the repository is ready to be public.
4. Use `zenodo.json` to populate the title, description, creator, keywords, and
   related repository. Select the final repository license in the deposit form.
5. Review the file list for the exclusions in `freeze_manifest.json`.
6. Publish the Zenodo record and copy its DOI into the next version of
   `CITATION.cff` and the README. Add it to the manuscript Data Availability
   Statement when the manuscript is released.

Until step 6 is complete, the archive has no DOI; the repository URL and release
tag are the only public identifiers.
