# Sensor-Set Conditioning for Prognostic Posterior Consistency

This repository contains the manuscript source, analysis code, frozen protocol
documents, and compact result artifacts for the study of sensor-set
conditioning in probabilistic remaining-useful-life prediction.

The paper's primary evidence comes from a controlled synthetic benchmark with
an exact oracle posterior. C-MAPSS FD001 is included as a public simulated
benchmark under a shared-model protocol; it is not presented as field
validation. The NASA data are not redistributed here. Obtain and preprocess
them from the [NASA C-MAPSS public data page](https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data)
before rerunning that benchmark.

## Reproduce the manuscript

```bash
cd paper
latexmk -pdf -interaction=nonstopmode main.tex
```

The current manuscript includes the shared-model C-MAPSS results and the
descriptive calibration diagnostic. In the full research workspace, the
calibration analysis can be rerun from the frozen C1 prediction stores with:

```bash
python3 scripts/analysis/calibration_analysis.py
```

The plotting dependency is listed in `requirements-calibration.txt`.

This writes the coverage/PIT summary, the manuscript table, and the reliability
figure. The public GitHub bundle contains the compact outputs but omits the
multi-gigabyte prediction stores. Calibration is a supplementary diagnostic and
does not alter any preregistered decision rule.

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

This is a pre-release working tree. Before making a public GitHub release,
choose a software license, review the data-availability statement, and create a
versioned release containing the manuscript source and compact result bundle.
The release can then be connected to Zenodo if a DOI is needed for submission.
