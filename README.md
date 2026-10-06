# Sensor-Set Conditioning for Prognostic Posterior Consistency

This repository contains the analysis code, frozen protocol documents, and
compact result artifacts for the study of sensor-set conditioning in
probabilistic remaining-useful-life prediction. The manuscript source is
temporarily withheld and may be added in a later release.

The paper's primary evidence comes from a controlled synthetic benchmark with
an exact oracle posterior. C-MAPSS FD001 is included as a public simulated
benchmark under a shared-model protocol; it is not presented as field
validation. The NASA data are not redistributed here. Obtain and preprocess
them from the [NASA C-MAPSS public data page](https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data)
before rerunning that benchmark.

## Reproduce the analyses

```bash
python3 scripts/analysis/calibration_analysis.py
```

The calibration analysis reruns the descriptive diagnostic from the frozen C1
prediction stores. The plotting dependency is listed in
`requirements-calibration.txt`.

This writes the coverage/PIT summaries and compact result files under
`calibration_results/`. Manuscript-facing figures and LaTeX tables are generated
only when an explicit manuscript output directory is supplied. The repository
omits the multi-gigabyte prediction stores. Calibration is a supplementary
diagnostic and does not alter any preregistered decision rule.

## Reproduce the C-MAPSS shared-model evaluation

The training and evaluation scripts are:

- `scripts/cmapss/train_cmapss_shared.py`
- `scripts/cmapss/evaluate_cmapss_geometry_shared.py`

They train one model across the full view and two reduced views, split by
engine, and save MAE, energy distances, engine-level bootstrap intervals,
configuration, and seeds. The local result report is under
`cmapss_results/SHARED_MODEL_RUN_REPORT.md`.

## Data and large artifacts

The repository intentionally excludes raw C-MAPSS files, large formal
prediction stores, and local GPU checkpoints. Public result summaries and
small model-independent artifacts are retained. The exact files intended for a
release are listed in `reproducibility/release_manifest.json`.

## Release status

The code-only `v0.2.1` release withholds the manuscript source while retaining
the frozen protocol, thresholds, decision snapshots, and compact result bundle.
The historical `v0.2.0` tag includes the manuscript source and should remain
private. See `RELEASE_NOTES_v0.2.1.md`, `zenodo.json`, and
`reproducibility/RELEASE_CHECKLIST.md` for the release record.
