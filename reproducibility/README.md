# Reproducibility archive

This directory contains the frozen protocol record for the manuscript. The
contracts define the scientific objects, splits, estimands, thresholds, bootstrap
rules, and decision logic before outcomes are interpreted.

- `contracts/` contains the formal specifications, machine-readable contracts,
  and locked oracle thresholds.
- `decisions/` contains the C1 and C2 final decision snapshots and compact split
  score reports. The recorded C2 failure is intentionally preserved.
- `oracle_audit/` contains the compact audit inputs and summary used for the
  post-hoc oracle-relative geometry table.
- `freeze_manifest.json` maps each archived artifact to its role in the frozen
  record and lists excluded private or large inputs.
- `RELEASE_CHECKLIST.md` describes the Zenodo publication sequence.

The archive does not include raw C-MAPSS data, large prediction stores, GPU
checkpoints, or credentials.
