# Versioned archive checklist

This bundle is the release candidate for the timestamped research archive. It is
intended to be published as GitHub release `v0.2.0` and then archived through the
Zenodo GitHub integration.

## Frozen material included

- formal problem, experiment, oracle/eligibility, and claim-metric specifications;
- C1 and C2 machine-readable contracts;
- locked oracle thresholds;
- C1 and C2 decision snapshots and split scores;
- compact C2 oracle-relative audit artifacts;
- current manuscript source, bibliography, figures, tables, and compiled PDF;
- calibration and shared-model C-MAPSS scripts and compact outputs.

The decision snapshots are part of the record even when a claim fails. In this
version, C1 is recorded as `C1-OA-PASS` and C2 as `C2-CORE-FAIL`.

## Zenodo publication sequence

1. Confirm that the GitHub repository contains the `v0.2.0` release tag.
2. In Zenodo, enable the repository under GitHub integrations.
3. Create or select the GitHub release `v0.2.0` and import it into Zenodo.
4. Use `zenodo.json` to populate the title, description, creator, keywords, and
   related repository. Select the final repository license in the deposit form.
5. Review the file list for the exclusions in `freeze_manifest.json`.
6. Publish the Zenodo record and copy its DOI into the next version of
   `CITATION.cff`, the manuscript Data Availability Statement, and the README.

Until step 6 is complete, the archive has no DOI; the repository URL and release
tag are the only public identifiers.
